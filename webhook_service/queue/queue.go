package queue

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/MarechJ/hll_rcon_tool/webhook_service/discord"
	"github.com/redis/go-redis/v9"
	"log/slog"
	"strconv"
	"sync"
	"time"
)

const (
	inputQueue       = "discord_webhook_queue:input"
	bucketsHash      = "discord_webhook:webhook_buckets"
	firstTimeQueue   = "discord_webhook_queue:first_time"
	transientChannel = "discord_webhook_transient:channel"
)

// Message represents the incoming message structure from Redis
type Message struct {
	ServerNumber  int                        `json:"server_number"`
	Discardable   bool                       `json:"discardable"`
	Edit          bool                       `json:"edit"`
	SentAt        time.Time                  `json:"sent_at"`
	RetryAttempts int                        `json:"retry_attempts"`
	PayloadType   *string                    `json:"payload_type,omitempty"`
	WebhookType   discord.WebhookType        `json:"webhook_type"`
	MessageType   discord.WebhookMessageType `json:"message_type"`
	Payload       discord.DiscordWebhookDict `json:"payload"`
	MessageNumber int
}

func (m *Message) String() string {
	return fmt.Sprintf("S#: %d Discard: %t Edit: %t Msg#: %d",
		m.ServerNumber, m.Discardable, m.Edit, m.MessageNumber)
}

// Queue Global settings and shared variables
type Queue struct {
	logger              *slog.Logger
	rdb                 *redis.Client
	maxQueueSize        int64
	maxMsgReattempts    int
	rateLimitWindowSize time.Duration
	localRateLimit      *LocalRateLimit
	workerLookup        map[string]*BucketWorker
	mu                  sync.Mutex
	errors              *WebhookErrors

	pubsub *redis.PubSub
}

func NewQueue(l *slog.Logger, rdb *redis.Client, webhookErrors *WebhookErrors, localRateLimit *LocalRateLimit, maxQueueSize int64, maxMsgReattempts int, rateLimitWindowSize time.Duration) *Queue {
	return &Queue{
		logger:              l,
		rdb:                 rdb,
		errors:              webhookErrors,
		maxQueueSize:        maxQueueSize,
		maxMsgReattempts:    maxMsgReattempts,
		rateLimitWindowSize: rateLimitWindowSize,
		workerLookup:        make(map[string]*BucketWorker),
		localRateLimit:      localRateLimit,
	}
}

func (q *Queue) Run(ctx context.Context) error {
	go q.bootstrapQueue()
	go q.subscribeBuckets(ctx)
	go q.subscribeTransients(ctx)
	return nil
}

func (q *Queue) subscribeTransients(ctx context.Context) {
	q.pubsub = q.rdb.Subscribe(ctx, transientChannel)

	q.logger.Info(fmt.Sprintf("Subscribing to: %s", transientChannel))
	for msg := range q.pubsub.Channel() {
		var transientMsg Message
		if err := json.Unmarshal([]byte(msg.Payload), &transientMsg); err != nil {
			q.logger.Error(fmt.Sprintf("transient unmarshal error: %v, JSON: %s", err, msg.Payload))
			continue
		}
		go q.processTransient(ctx, transientMsg)
	}
}

func (q *Queue) Close() error {
	err := q.pubsub.Close()
	if err != nil {
		return err
	}
	return nil
}

func (q *Queue) subscribeBuckets(ctx context.Context) {
	for {
		results, err := q.rdb.BLPop(ctx, 30*time.Second, inputQueue).Result()
		if err != nil {
			q.logger.Error(fmt.Sprintf("Input pop error: %v", err))
			time.Sleep(time.Second)
			continue
		}

		var msg Message
		var rawStr string
		rawMessage := []byte(results[1])
		// This is stupid, but we have to get the raw JSON string into a string before we can
		// unmarshal it into our struct because of how it's encoded from CRCON
		if err := json.Unmarshal(rawMessage, &rawStr); err == nil {
			if err := json.Unmarshal([]byte(rawStr), &msg); err != nil {
				q.logger.Error(fmt.Sprintf("unmarshal error: %v, JSON: %s", err, rawStr))
				time.Sleep(time.Second)
				continue
			}
		} else {
			q.logger.Error(fmt.Sprintf("Input unmarshal error: %v, JSON: %s", err, rawMessage))
			time.Sleep(time.Second)
			continue
		}

		// Check to see if we already know this webhook's rate limit bucket
		// We check by webhook ID since multiple webhooks can share the same bucket
		webhookID, err := discord.ExtractWebhookID(msg.Payload.URL)
		if err != nil {
			q.logger.Error(fmt.Sprintf("Could not parse webhook ID from: %s:%s", msg.Payload.URL, err))
			continue
		}
		bucket, err := q.rdb.HGet(ctx, bucketsHash, webhookID).Result()
		var msgBytes []byte
		msgBytes, _ = json.Marshal(msg)
		if errors.Is(err, redis.Nil) {
			// Unknown webhook, send to first-time queue
			q.rdb.RPush(ctx, firstTimeQueue, msgBytes)
			q.rdb.LTrim(ctx, firstTimeQueue, 0, q.maxQueueSize-1)
		} else {
			// Known bucket, send to bucket queue
			queueKey := bucketQueuePrefix + bucket
			q.rdb.RPush(ctx, queueKey, msgBytes)
			q.rdb.LTrim(ctx, queueKey, 0, q.maxQueueSize-1)

			// Start workers if new bucket
			if _, exists := q.GetWorker(bucket); !exists {
				worker := q.newBucketWorker(bucket)
				q.SetWorker(bucket, worker)
				go worker.ProcessQueue(ctx)
			}
		}
	}
}

func (q *Queue) newBucketWorker(bucketId string) *BucketWorker {
	return NewBucketWorker(q.logger.WithGroup("bucket-worker"), q.rdb, q, q.localRateLimit, q.errors, bucketId, q.maxMsgReattempts, q.rateLimitWindowSize)
}

func (q *Queue) bootstrapQueue() {
	ctx := context.Background()
	for {
		results, err := q.rdb.BLPop(ctx, 30*time.Second, firstTimeQueue).Result()
		if err != nil {
			q.logger.Error(fmt.Sprintf("First-time pop error: %v", err))
			time.Sleep(time.Second)
			continue
		}

		var msg Message
		rawMessage := []byte(results[1])
		if err := json.Unmarshal(rawMessage, &msg); err != nil {
			q.logger.Error(fmt.Sprintf("First-time unmarshal error: %v, JSON: %s", err, rawMessage))
			continue
		}

		webhookID, err := discord.ExtractWebhookID(msg.Payload.URL)
		if err != nil {
			q.logger.Error(fmt.Sprintf("Could not parse webhook ID from: %s:%s", msg.Payload.URL, err))
			continue
		}

		// If we've already seen this webhookID and know the bucket, insert it
		// into the appropriate queue instead of sending here
		bucket, err := q.rdb.HGet(ctx, bucketsHash, webhookID).Result()
		if !errors.Is(err, redis.Nil) {
			queueKey := bucketQueuePrefix + bucket
			var msgBytes []byte
			msgBytes, _ = json.Marshal(msg)
			q.rdb.RPush(ctx, queueKey, msgBytes)
			q.rdb.LTrim(ctx, queueKey, 0, q.maxQueueSize-1)
			continue
		}

		// Our retry logic here does block the first time queue but this should be
		// fairly rare; after any successful attempt messages will be routed to the
		// appropriate queue; and there aren't that many unique places CRCON dispatches
		// webhooks from
		var rateLimited *RateLimited
		for attempts := 0; attempts < q.maxMsgReattempts && (!msg.Discardable); attempts++ {
			worker := q.newBucketWorker("")
			bucket, err = worker.SendWebhook(ctx, &msg)
			if err == nil {
				q.rdb.HSet(ctx, bucketsHash, webhookID, bucket)
				// Start worker if new bucket
				if _, exists := q.GetWorker(bucket); !exists {
					worker.UpdateBucket(bucket)
					q.SetWorker(bucket, worker)
					go worker.ProcessQueue(ctx)
				}
			} else if errors.As(err, &rateLimited) {
				q.logger.Error(fmt.Sprintf("First-time rate limited: %s", err))
				time.Sleep(rateLimited.RateLimitSleepTime)
			} else {
				q.logger.Error(fmt.Sprintf("First-time send error: %s", err))
				// We had some sort of (non rate limiting error) trying to send this message
				// back off before attempting again
				time.Sleep(time.Second * 2 * time.Duration(attempts+1))
			}
		}
		queueKey := bucketQueuePrefix + bucket
		q.rdb.LTrim(ctx, queueKey, 0, q.maxQueueSize-1)
	}
}

func (q *Queue) processTransient(ctx context.Context, msg Message) {
	webhookID, err := discord.ExtractWebhookID(msg.Payload.URL)
	if err != nil {
		q.logger.Error(fmt.Sprintf("could not parse webhook ID from: %s:%s", msg.Payload.URL, err))
		return
	}

	bucket, err := q.rdb.HGet(ctx, bucketsHash, webhookID).Result()
	var worker *BucketWorker
	if !errors.Is(err, redis.Nil) {
		worker, _ = q.GetWorker(bucket)
	}

	if worker == nil {
		worker = q.newBucketWorker(bucket)
		q.SetWorker(bucket, worker)
	}

	// No need to try reattempts; these messages are inherently discardable
	bucket, err = worker.SendWebhook(ctx, &msg)
	if err != nil {
		q.logger.Error(fmt.Sprintf("transient message send error for %s: %v", msg.Payload.WebhookID, err))
	} else {
		worker.UpdateBucket(bucket)
	}
	q.rdb.HSet(ctx, bucketsHash, webhookID, bucket)
}

func (q *Queue) GetWorker(bucket string) (*BucketWorker, bool) {
	q.mu.Lock()
	defer q.mu.Unlock()
	worker, exists := q.workerLookup[bucket]
	return worker, exists
}

func (q *Queue) SetWorker(bucket string, worker *BucketWorker) {
	q.mu.Lock()
	defer q.mu.Unlock()
	q.workerLookup[bucket] = worker
}

func (q *Queue) SetGloballyRateLimited(ctx context.Context, limited bool, resetTime time.Time, resetAfter time.Duration) {
	// The CRCON API will decode these as true/false
	var payload string
	if limited {
		payload = "1"
	} else {
		payload = "0"
	}
	q.rdb.Set(ctx, payload, strconv.Itoa(int(resetTime.Unix())), resetAfter)
}
