/*
	The current Python web service is very inefficient because it polls.

	Here's the goal of our new solution; use a master queue for messages.

	Listen to the queue in a blocking fashion for CPU efficiency.

	When we receive a message; examine it and determine if we already know
	the Discord RL bucket for it; and if so send it to the queue for
	that bucket.

	If we don't; send it to the shared queue and once we've established the
	RL bucket after a successful request to Discord; future messages will go
	to the appropriate queue.

	Each queue will also BLOP for efficiency and process one message at a time;
	the key/value pairs for transient messages (scoreboard at this point)
	are done with redis pub/sub which naturally handles dropping unhandled messages
	if nobody is listening and also is CPU efficient with blocking and waiting for
	messages to arrive

	Workers for each rate limit bucket handle their rate limits/sleeping when they
	need to wait for Discord

	We also maintain a local rate limit window (configurable by .env vars) so people
	can do some tuning on their end

	If we become globally rate limited by Discord each worker will discover that and
	sleep the appropriate amount; which isn't necessarily ideal but does simplify the
	code some
*/

package main

import (
	"context"
	"fmt"
	"github.com/MarechJ/hll_rcon_tool/webhook_service/queue"
	"io"
	"log/slog"
	"os"
	"os/signal"
	"path/filepath"
	"strconv"
	"strings"
	"syscall"
	"time"

	"github.com/redis/go-redis/v9"
)

var logger *slog.Logger
var logFile *os.File

func init() {
	logPath := os.Getenv("LOGGING_PATH")
	logPath = filepath.Join(logPath, "webhook_service.log")
	logFile, err := os.OpenFile(logPath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		panic(err)
	}

	// Mimic the rest of CRCON and log to both stdout and a file
	mw := io.MultiWriter(os.Stdout, logFile)

	tagFile, err := os.ReadFile("tag_version")
	var tag string
	if err != nil {
		tag = "unknown"
	} else {
		tag = strings.TrimRight(string(tagFile), "\n")
	}

	logger = slog.New(slog.NewTextHandler(mw, nil))
	logger = logger.With("tag", tag)
}

func main() {
	ctx := context.Background()
	logger.Info("Starting service")
	rdb := SetupRedis()

	// For the Docker health check
	path := filepath.Join("/app", "webhook-service-healthy")
	os.Create(path)

	maxRequests, err := strconv.Atoi(os.Getenv("HLL_LOCAL_MAX_SENDS_PER_SEC"))
	if err != nil {
		maxRequests = 45
	}

	maxQueueSize, err := strconv.ParseInt(os.Getenv("HLL_WH_MAX_QUEUE_LENGTH"), 10, 64)
	if err != nil {
		maxQueueSize = 150
	}

	maxReattempts, err := strconv.Atoi(os.Getenv("HLL_WH_MAX_RETRIES"))
	if err != nil {
		maxReattempts = 5
	}

	var rateLimitWindowSize time.Duration
	windowSize, err := strconv.Atoi(os.Getenv("HLL_WH_SERVICE_RL_TIME_WINDOW"))
	if err != nil {
		rateLimitWindowSize = time.Duration(600 * int(time.Second))
	} else {
		rateLimitWindowSize = time.Duration(windowSize * int(time.Second))
	}

	q := queue.NewQueue(logger, rdb, queue.NewWebhookErrors(rdb), queue.NewLocalRateLimit(maxRequests), maxQueueSize, maxReattempts, rateLimitWindowSize)

	go q.Bootstrap()
	if err = q.Run(ctx); err != nil {
		logger.Error("queue-run", "error", err)
	}

	// Keep running
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
	<-stop

	logger.Info("graceful-shutdown")
	if err = q.Close(); err != nil {
		logger.Error("closing-queue", "error", err)
	}
	if err = rdb.Close(); err != nil {
		logger.Error("closing-redis", "error", err)
	}
	if err = logFile.Close(); err != nil {
		logger.Error("closing-log-file", "error", err)
	}
}

// SetupRedis initializes the Redis client
func SetupRedis() *redis.Client {
	logger.Info("Initializing redis")
	host := os.Getenv("HLL_REDIS_HOST")
	if host == "" {
		panic("HLL_REDIS_HOST not set")
	}

	portStr := os.Getenv("HLL_REDIS_PORT")
	port, err := strconv.Atoi(portStr)
	if err != nil || port <= 0 {
		panic("HLL_REDIS_PORT not set or invalid")
	}

	addr := fmt.Sprintf("%s:%d", host, port)
	return redis.NewClient(&redis.Options{
		Addr: addr,
		DB:   0, // CRCON uses DB #0 as a global shared database for all game servers
	})
}
