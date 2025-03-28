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
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"math/rand"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
	"strconv"
	"sync"
	"time"

	"github.com/redis/go-redis/v9"
)

var webhookIDPattern = regexp.MustCompile(`webhooks/([0-9]+)/`)

var logger *slog.Logger

func init() {
	logger = slog.New(slog.NewTextHandler(os.Stdout, nil))
	tag := os.Getenv("TAGGED_VERSION")
	logger = logger.With("tag", tag)
}

const (
	inputQueue                 = "discord_webhook_queue:input"
	firstTimeQueue             = "discord_webhook_queue:first_time"
	bucketQueuePrefix          = "discord_webhook_queue:bucket:"
	webhookErrors              = "discord_webhook_queue:webhook_id_errors"
	transientChannel           = "discord_webhook_transient:channel"
	message_404                = "discord_webhook:message_404"
	bucketsHash                = "discord_webhook:webhook_buckets"
	bucketRateLimitCountHash   = "discord_webhook_bucket_rl_count"
	discordGloballyRateLimited = "discord_webhook:global_rate_limited"
)

// WebhookType represents the type of webhook service
type WebhookType string

const (
	WebhookTypeDiscord WebhookType = "discord"
)

// WebhookMessageType represents the underlying type of a webhook message
type WebhookMessageType string

const (
	WebhookMessageTypeLogLine     WebhookMessageType = "log_line"
	WebhookMessageTypeLogLineChat WebhookMessageType = "log_line_chat"
	WebhookMessageTypeLogLineKill WebhookMessageType = "log_line_kill"
	WebhookMessageTypeTeamkill    WebhookMessageType = "log_line_teamkill"
	WebhookMessageTypeAdminPing   WebhookMessageType = "admin_ping"
	WebhookMessageTypeScoreboard  WebhookMessageType = "scoreboard"
	WebhookMessageTypeAudit       WebhookMessageType = "audit"
	WebhookMessageTypeOther       WebhookMessageType = "other"
)

// DiscordWebhookDict represents the payload for a Discord webhook
type DiscordWebhookDict struct {
	URL             string               `json:"url"`
	WebhookID       string               `json:"webhook_id"`
	MessageID       *string              `json:"message_id,omitempty"`
	AllowedMentions *AllowedMentionsDict `json:"allowed_mentions,omitempty"`
	Content         *string              `json:"content,omitempty"`
	Embeds          []DiscordEmbedDict   `json:"embeds,omitempty"`
}

// Override unmarshaling so we can ignore extra fields
func (d *DiscordWebhookDict) UnmarshalJSON(data []byte) error {
	type Alias DiscordWebhookDict
	aux := struct {
		*Alias
		Extra map[string]any `json:"-"` // Catch-all for unknown fields
	}{
		Alias: (*Alias)(d),
	}

	if err := json.Unmarshal(data, &aux); err != nil {
		return err
	}

	return nil
}

// AllowedMentionsDict specifies which mentions are allowed
type AllowedMentionsDict struct {
	Parse       []string `json:"parse,omitempty"`
	Roles       []string `json:"roles,omitempty"`
	Users       []string `json:"users,omitempty"`
	RepliedUser *bool    `json:"replied_user,omitempty"`
}

// EmbedFooterDict represents an embed footer
type EmbedFooterDict struct {
	Text         string  `json:"text"`
	IconURL      *string `json:"icon_url,omitempty"`
	ProxyIconURL *string `json:"proxy_icon_url,omitempty"`
}

// EmbedImageDict represents an embed image
type EmbedImageDict struct {
	URL      string  `json:"url"`
	ProxyURL *string `json:"proxy_url,omitempty"`
	Height   *int    `json:"height,omitempty"`
	Width    *int    `json:"width,omitempty"`
}

// EmbedThumbnailDict represents an embed thumbnail
type EmbedThumbnailDict struct {
	URL      string  `json:"url"`
	ProxyURL *string `json:"proxy_url,omitempty"`
	Height   *int    `json:"height,omitempty"`
	Width    *int    `json:"width,omitempty"`
}

// EmbedVideoDict represents an embed video
type EmbedVideoDict struct {
	URL      *string `json:"url,omitempty"`
	ProxyURL *string `json:"proxy_url,omitempty"`
	Height   *int    `json:"height,omitempty"`
	Width    *int    `json:"width,omitempty"`
}

// EmbedProviderDict represents an embed provider
type EmbedProviderDict struct {
	Name *string `json:"name,omitempty"`
	URL  *string `json:"url,omitempty"`
}

// EmbedAuthorDict represents an embed author
type EmbedAuthorDict struct {
	Name         string  `json:"name"`
	URL          *string `json:"url,omitempty"`
	IconURL      *string `json:"icon_url,omitempty"`
	ProxyIconURL *string `json:"proxy_icon_url,omitempty"`
}

// EmbedFieldDict represents an embed field
type EmbedFieldDict struct {
	Name   string `json:"name"`
	Value  string `json:"value"`
	Inline *bool  `json:"inline,omitempty"`
}

type DiscordEmbedDict struct {
	Title       *string             `json:"title,omitempty"`
	Description *string             `json:"description,omitempty"`
	URL         *string             `json:"url,omitempty"`
	Timestamp   *string             `json:"timestamp,omitempty"` // ISO 8601 string
	Color       *int                `json:"color,omitempty"`
	Footer      *EmbedFooterDict    `json:"footer,omitempty"`
	Image       *EmbedImageDict     `json:"image,omitempty"`
	Thumbnail   *EmbedThumbnailDict `json:"thumbnail,omitempty"`
	Video       *EmbedVideoDict     `json:"video,omitempty"`
	Provider    *EmbedProviderDict  `json:"provider,omitempty"`
	Author      *EmbedAuthorDict    `json:"author,omitempty"`
	Fields      []EmbedFieldDict    `json:"fields,omitempty"`
}

// Message represents the incoming message structure from Redis
type Message struct {
	ServerNumber  int                `json:"server_number"`
	Discardable   bool               `json:"discardable"`
	Edit          bool               `json:"edit"`
	SentAt        time.Time          `json:"sent_at"`
	RetryAttempts int                `json:"retry_attempts"`
	PayloadType   *string            `json:"payload_type,omitempty"`
	WebhookType   WebhookType        `json:"webhook_type"`
	MessageType   WebhookMessageType `json:"message_type"`
	Payload       DiscordWebhookDict `json:"payload"`
	MessageNumber int
}

func (m *Message) String() string {
	return fmt.Sprintf("S#: %d Discard: %t Edit: %t Msg#: %d",
		m.ServerNumber, m.Discardable, m.Edit, m.MessageNumber)
}

// Tracks bucket specific rate limits
type RateLimitState struct {
	BucketID    string
	Remaining   int
	Limit       int
	ResetTime   time.Time
	ResetAfter  time.Duration
	RateLimited bool
	mu          sync.Mutex
}

func (r *RateLimitState) String() string {
	return fmt.Sprintf("ID: %s Remaining: %d Limit: %d ResetTime: %s ResetAfter: %d RateLimited: %t",
		r.BucketID, r.Remaining, r.Limit, r.ResetTime, r.ResetAfter, r.RateLimited)
}

func (rateLimit *RateLimitState) GetRateLimitSleepTime() time.Duration {
	rateLimit.mu.Lock()
	defer rateLimit.mu.Unlock()

	if rateLimit.RateLimited {
		return time.Until(rateLimit.ResetTime)
	}

	return 0
}

// Global settings and shared variables
type globalState struct {
	// A context is required to work with redis
	ctx                 context.Context
	MaxQueueSize        int64
	MaxMsgReattempts    int
	RateLimitWindowSize time.Duration
	WorkerLookup        map[string]*BucketWorker
	mu                  sync.Mutex
}

func (state *globalState) GetWorker(bucket string) (*BucketWorker, bool) {
	state.mu.Lock()
	defer state.mu.Unlock()
	worker, exists := state.WorkerLookup[bucket]
	return worker, exists
}

func (state *globalState) SetWorker(bucket string, worker *BucketWorker) {
	state.mu.Lock()
	defer state.mu.Unlock()
	state.WorkerLookup[bucket] = worker
}

// Tracks our local rate limit window
type localRateLimitState struct {
	Requests    int
	MaxRequests int
	Window      time.Time
	mu          sync.Mutex
}

// Keeps us under `HLL_LOCAL_MAX_SENDS_PER_SEC` across all requests
func (state *localRateLimitState) CheckLocalRateLimit(globalState *globalState, requests int, now time.Time) error {
	state.mu.Lock()
	defer state.mu.Unlock()

	// If it's been more than 1 second since our last request; reset the window
	if now.Sub(state.Window) >= time.Second {
		state.Requests = requests
		state.Window = now
	}

	// Don't exceed our configured max requests per second
	if state.Requests >= state.MaxRequests {
		state.mu.Unlock()
		return fmt.Errorf("local rate limit exceeded")
	}

	state.Requests++
	return nil
}

// Manages a rate limit bucket
type BucketWorker struct {
	QueueKey  string
	rdb       *redis.Client
	ctx       context.Context
	rateLimit *RateLimitState
}

func NewBucketWorker(bucketID string, rdb *redis.Client) *BucketWorker {
	return &BucketWorker{
		QueueKey:  bucketQueuePrefix + bucketID,
		rdb:       rdb,
		ctx:       context.Background(),
		rateLimit: &RateLimitState{BucketID: bucketID},
	}
}

// Makes the HTTP request to Discord and updates rate limit state
func SendWebhook(rdb *redis.Client, state *localRateLimitState, globalState *globalState, msg *Message, rateLimit *RateLimitState) (string, error) {
	now := time.Now()
	if err := state.CheckLocalRateLimit(globalState, 0, now); err != nil {
		return "", err
	}

	// Extract what we need to make our POST request to Discord
	payload := map[string]any{}
	if msg.Payload.Content != nil {
		payload["content"] = *msg.Payload.Content
	}
	if len(msg.Payload.Embeds) > 0 {
		payload["embeds"] = msg.Payload.Embeds
	}
	if msg.Payload.AllowedMentions != nil {
		payload["allowed_mentions"] = msg.Payload.AllowedMentions
	}

	var jsonPayload []byte
	var err error
	jsonPayload, err = json.Marshal(payload)
	if err != nil {
		return "", fmt.Errorf("marshal error: %v", err)
	}

	var resp *http.Response

	if msg.Edit {
		resp, err = ExecuteWebhook("PATCH", jsonPayload, fmt.Sprintf("%s/messages/%s", msg.Payload.URL, *msg.Payload.MessageID))
	} else {
		resp, err = ExecuteWebhook("POST", jsonPayload, msg.Payload.URL)
	}

	if err != nil {
		return "", err
	}

	// If we didn't get a 429 or a 500 series error; flag the message so it will be dropped
	// 200s went through; all the other status codes are unrecoverable
	if resp.StatusCode != http.StatusTooManyRequests || resp.StatusCode < 500 {
		msg.Discardable = true
	}

	// Flag the webhook if we get these specific errors
	// Not checking the error; if we got this far it's a URL with a parseable ID
	webhookID, _ := ExtractWebhookID(msg.Payload.URL)
	switch resp.StatusCode {
	case http.StatusUnauthorized:
		SetWebhookError(rdb, webhookID, true, false, false)
	case http.StatusForbidden:
		SetWebhookError(rdb, webhookID, false, true, false)
	case http.StatusNotFound:
		SetWebhookError(rdb, webhookID, false, false, true)
	}

	if resp.StatusCode == http.StatusNotFound {
		ctx := context.Background()
		str := fmt.Sprintf("%s:%s", message_404, *msg.Payload.MessageID)
		rdb.Set(ctx, str, true, 0)
		if msg.Payload.MessageID != nil {
			return "", fmt.Errorf("HTTP 404 for %s", *msg.Payload.MessageID)
		} else {
			return "", fmt.Errorf("HTTP 404; no message ID included")
		}
	} else if resp.StatusCode == 400 || resp.StatusCode == http.StatusUnauthorized || resp.StatusCode == http.StatusForbidden {
		return "", fmt.Errorf("%s is not a valid webhook URL", msg.Payload.URL)

	} else if resp.StatusCode == http.StatusOK || resp.StatusCode == http.StatusNoContent || resp.StatusCode == http.StatusTooManyRequests {
		ClearWebhookError(rdb, webhookID)
		// These responses will contain valid rate limit headers
		bucket := resp.Header.Get("X-RateLimit-Bucket")
		rateLimit.mu.Lock()
		defer rateLimit.mu.Unlock()

		if remaining, err := strconv.Atoi(resp.Header.Get("X-RateLimit-Remaining")); err == nil {
			rateLimit.Remaining = remaining
		}
		if limit, err := strconv.Atoi(resp.Header.Get("X-RateLimit-Limit")); err == nil {
			rateLimit.Limit = limit
		}
		if reset, err := strconv.ParseInt(resp.Header.Get("X-RateLimit-Reset"), 10, 64); err == nil {
			rateLimit.ResetTime = time.Unix(reset, 0)
			// Pad the reset time two seconds because Discord are liars and following their header
			// responses exactly will still cause excessive 429s
			rateLimit.ResetTime = rateLimit.ResetTime.Add(time.Duration(2.0 * float64(time.Second)))

		}
		if resetAfter, err := strconv.ParseFloat(resp.Header.Get("X-RateLimit-Reset-After"), 64); err == nil {
			// Pad the reset time two seconds because Discord are liars and following their header
			// responses exactly will still cause excessive 429s
			rateLimit.ResetAfter = time.Duration((resetAfter + 2.0) * float64(time.Second))
		}

		if resp.StatusCode == http.StatusTooManyRequests {
			UpdateBucketRateLimitCount(rdb, globalState, bucket)
			logger.Warn(fmt.Sprintf("HTTP %d for %s", resp.StatusCode, bucket))
			rateLimit.RateLimited = true
			if resp.Header.Get("X-RateLimit-Global") != "" {
				// Set the global rate limit flag in Redis so it can be retrieved by the API
				// we don't explicitly check it because each worker will flag itself as rate limited
				logger.Warn(fmt.Sprintf("Global rate limit hit, pausing for %v", rateLimit.ResetAfter))
				SetGloballyRateLimited(rdb, rateLimit.ResetTime, rateLimit.ResetAfter)
				// Force wait by maxing out the requests in our local window
				state.CheckLocalRateLimit(globalState, state.MaxRequests, time.Now())
			}
			return bucket, fmt.Errorf("rate limited until %v", rateLimit.ResetTime)
		}

		rateLimit.RateLimited = false
		return bucket, nil
	} else {
		return "", fmt.Errorf("unhandled HTTP status %d", resp.StatusCode)
	}
}

// ProcessQueue handles a bucket queue with retries
func (bw *BucketWorker) ProcessQueue(rdb *redis.Client, state *localRateLimitState, globalState *globalState) {
	for {
		bw.rateLimit.mu.Lock()
		now := time.Now()
		// Reset rate limit state if ResetTime has passed
		if now.After(bw.rateLimit.ResetTime) {
			bw.rateLimit.RateLimited = false
			// Discord will tell us the actual number remaining after the next request
			// but give it at least 1 request so it can make the next request
			bw.rateLimit.Remaining = 1
			bw.rateLimit.ResetTime = time.Time{}
			bw.rateLimit.ResetAfter = 0
			// logger.Printf("Bucket %s rate limit reset",  bw.rateLimit.BucketID)
		}

		// We're safe to sleep this particular rate limit bucket without impacting other threads
		// because if Discord is rate limiting us; any other worker (transient messages)
		// can't process anyway; Discord would just reject it
		if bw.rateLimit.RateLimited || bw.rateLimit.Remaining <= 0 {
			wait := time.Until(bw.rateLimit.ResetTime)
			bw.rateLimit.mu.Unlock()
			if wait > 0 {
				logger.Info(fmt.Sprintf("Bucket %s waiting %v", bw.rateLimit.BucketID, wait))
				time.Sleep(wait)
			}
			continue
		}
		bw.rateLimit.mu.Unlock()

		// Grab our next message off the quueue
		results, err := bw.rdb.BLPop(bw.ctx, 5*time.Second, bw.QueueKey).Result()
		if err == redis.Nil {
			continue
		} else if err != nil {
			logger.Error(fmt.Sprintf("Error popping from %s: %v", bw.QueueKey, err))
			continue
		}

		var msg Message
		if err := json.Unmarshal([]byte(results[1]), &msg); err != nil {
			logger.Error(fmt.Sprintf("Unmarshal error: %v, JSON: %s", err, results[1]))
			continue
		}
		msg.MessageNumber = rand.Int()

		// We retry rate limited messages N times instead of re-enqueuing them which can slow down
		// processing other messages; but doesn't let an unhandled bad message block a queue forever
		// and if we're getting an error on this message; we would very likely have errors on the remaining
		// messages anyway
		for attempts := 0; attempts < globalState.MaxMsgReattempts && !msg.Discardable; attempts++ {
			_, err := SendWebhook(rdb, state, globalState, &msg, bw.rateLimit)
			if err == nil {
				break
			}

			logger.Info(fmt.Sprintf("Retry %d for %d in bucket %s: %v", attempts+1, msg.MessageNumber, bw.rateLimit.BucketID, err))
			if attempts == 2 {
				logger.Warn(fmt.Sprintf("Dropped after 3 retries: %s", msg.Payload.URL))
				break
			}
			wait := bw.rateLimit.GetRateLimitSleepTime()
			if wait > 0 {
				time.Sleep(wait)
			} else {
				// We failed to send for some reason other than rate limiting
				// back off before attempting again
				time.Sleep(time.Second * 2 * time.Duration(attempts+1))
			}
		}
	}
}

func ExecuteWebhook(method string, payload []byte, url string) (*http.Response, error) {
	req, err := http.NewRequest(method, url, bytes.NewBuffer(payload))
	if err != nil {
		return nil, fmt.Errorf("request error: %v", err)
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("send error: %v", err)
	}
	defer resp.Body.Close()

	return resp, nil
}

// ProcessFirstTime discovers buckets for unknown webhooks
func ProcessFirstTime(rdb *redis.Client, state *localRateLimitState, globalState *globalState) {
	ctx := context.Background()
	for {
		results, err := rdb.BLPop(ctx, 0, firstTimeQueue).Result()
		if err != nil {
			logger.Error(fmt.Sprintf("First-time pop error: %v", err))
			time.Sleep(time.Second)
			continue
		}

		var msg Message
		rawMessage := []byte(results[1])
		if err := json.Unmarshal(rawMessage, &msg); err != nil {
			logger.Error(fmt.Sprintf("First-time unmarshal error: %v, JSON: %s", err, rawMessage))
			continue
		}

		webhookID, err := ExtractWebhookID(msg.Payload.URL)
		if err != nil {
			logger.Error(fmt.Sprintf("Could not parse webhook ID from: %s:%s", msg.Payload.URL, err))
			continue
		}

		// If we've already seen this webhookID and know the bucket, insert it
		// into the appropriate queue instead of sending here
		bucket, err := rdb.HGet(ctx, bucketsHash, webhookID).Result()
		if err != redis.Nil {
			queueKey := bucketQueuePrefix + bucket
			var msgBytes []byte
			msgBytes, _ = json.Marshal(msg)
			rdb.RPush(ctx, queueKey, msgBytes)
			rdb.LTrim(ctx, queueKey, 0, globalState.MaxQueueSize-1)
			continue
		}

		// Our retry logic here does block the first time queue but this should be
		// fairly rare; after any successful attempt messages will be routed to the
		// appropriate queue; and there aren't that many unique places CRCON dispatches
		// webhooks from
		rateLimit := &RateLimitState{}
		for attempts := 0; attempts < globalState.MaxMsgReattempts && (!msg.Discardable); attempts++ {
			bucket, err = SendWebhook(rdb, state, globalState, &msg, rateLimit)
			if err == nil {
				rdb.HSet(ctx, bucketsHash, webhookID, bucket)
				// Start worker if new bucket
				if _, exists := globalState.GetWorker(bucket); !exists {
					// Make a new worker but use the response we got from Discord
					// for the first time the message was sent
					worker := NewBucketWorker(bucket, rdb)
					worker.rateLimit.RateLimited = rateLimit.RateLimited
					worker.rateLimit.Remaining = rateLimit.Remaining
					worker.rateLimit.ResetAfter = rateLimit.ResetAfter
					worker.rateLimit.ResetTime = rateLimit.ResetTime
					globalState.SetWorker(bucket, worker)
					go worker.ProcessQueue(rdb, state, globalState)
				}
			} else {
				logger.Error(fmt.Sprintf("First-time send error: %v", err))
				if rateLimit.RateLimited {
					wait := rateLimit.GetRateLimitSleepTime()
					time.Sleep(wait)
				} else {
					// We had some sort of (non rate limiting error) trying to send this message
					// back off before attempting again
					time.Sleep(time.Second * 2 * time.Duration(attempts+1))
				}
			}
		}
		queueKey := bucketQueuePrefix + bucket
		rdb.LTrim(ctx, queueKey, 0, globalState.MaxQueueSize-1)
	}
}

func ProcessTransient(rdb *redis.Client, state *localRateLimitState, globalState *globalState, msg Message) {
	webhookID, err := ExtractWebhookID(msg.Payload.URL)
	if err != nil {
		logger.Error(fmt.Sprintf("could not parse webhook ID from: %s:%s", msg.Payload.URL, err))
		return
	}

	ctx := context.Background()
	bucket, err := rdb.HGet(ctx, bucketsHash, webhookID).Result()
	var worker *BucketWorker
	if err != redis.Nil {
		worker, _ = globalState.GetWorker(bucket)
	}

	if worker == nil {
		worker = NewBucketWorker(bucket, rdb)
		globalState.SetWorker(bucket, worker)
	}

	// No need to try reattempts; these messages are inherently discardable
	bucket, err = SendWebhook(rdb, state, globalState, &msg, worker.rateLimit)
	if err != nil {
		logger.Error(fmt.Sprintf("transient message send error for %s: %v", msg.Payload.WebhookID, err))
	}
	rdb.HSet(ctx, bucketsHash, webhookID, bucket)
}

// Subscribe to transient messages via pub/sub
func SubscribeTransients(rdb *redis.Client, state *localRateLimitState, globalState *globalState) {
	ctx := context.Background()
	pubsub := rdb.Subscribe(ctx, transientChannel)
	defer pubsub.Close()

	logger.Info(fmt.Sprintf("Subscribing to: %s", transientChannel))
	for msg := range pubsub.Channel() {
		var transientMsg Message
		if err := json.Unmarshal([]byte(msg.Payload), &transientMsg); err != nil {
			logger.Error(fmt.Sprintf("transient unmarshal error: %v, JSON: %s", err, msg.Payload))
			continue
		}
		go ProcessTransient(rdb, state, globalState, transientMsg)
	}
}

func main() {
	logger.Info("Starting service")
	rdb := SetupRedis()

	// For the Docker health check
	path := filepath.Join("/app", "webhook-service-healthy")
	os.Create(path)

	maxRequests, err := strconv.Atoi(os.Getenv("HLL_LOCAL_MAX_SENDS_PER_SEC"))
	if err != nil {
		maxRequests = 45
	}

	state := localRateLimitState{MaxRequests: maxRequests}

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

	globalState := globalState{
		ctx:                 context.Background(),
		MaxQueueSize:        maxQueueSize,
		MaxMsgReattempts:    maxReattempts,
		RateLimitWindowSize: rateLimitWindowSize,
		WorkerLookup:        make(map[string]*BucketWorker),
	}

	// Monitor the input queue and dispatch messages to the appropriate queue worker
	go func() {
		for {
			results, err := rdb.BLPop(globalState.ctx, 0, inputQueue).Result()
			if err != nil {
				logger.Error(fmt.Sprintf("Input pop error: %v", err))
				time.Sleep(time.Second)
				continue
			}

			var msg Message
			var rawStr string
			rawMessage := []byte(results[1])
			// This is stupid but we have to get the raw JSON string into a string before we can
			// unmarshal it into our struct because of how it's encoded from CRCON
			if err := json.Unmarshal(rawMessage, &rawStr); err == nil {
				if err := json.Unmarshal([]byte(rawStr), &msg); err != nil {
					logger.Error(fmt.Sprintf("unmarshal error: %v, JSON: %s", err, rawStr))
					time.Sleep(time.Second)
					continue
				}
			} else {
				logger.Error(fmt.Sprintf("Input unmarshal error: %v, JSON: %s", err, rawMessage))
				time.Sleep(time.Second)
				continue
			}

			// Check to see if we already know this webhook's rate limit bucket
			// We check by webhook ID since multiple webhooks can share the same bucket
			webhookID, err := ExtractWebhookID(msg.Payload.URL)
			if err != nil {
				logger.Error(fmt.Sprintf("Could not parse webhook ID from: %s:%s", msg.Payload.URL, err))
				continue
			}
			bucket, err := rdb.HGet(globalState.ctx, bucketsHash, webhookID).Result()
			var msgBytes []byte
			msgBytes, _ = json.Marshal(msg)
			if err == redis.Nil {
				// Unknown webhook, send to first-time queue
				rdb.RPush(globalState.ctx, firstTimeQueue, msgBytes)
				rdb.LTrim(globalState.ctx, firstTimeQueue, 0, maxQueueSize-1)
			} else {
				// Known bucket, send to bucket queue
				queueKey := bucketQueuePrefix + bucket
				rdb.RPush(globalState.ctx, queueKey, msgBytes)
				rdb.LTrim(globalState.ctx, queueKey, 0, maxQueueSize-1)

				// Start workers if new bucket
				if _, exists := globalState.GetWorker(bucket); !exists {
					worker := NewBucketWorker(bucket, rdb)
					globalState.SetWorker(bucket, worker)
					go worker.ProcessQueue(rdb, &state, &globalState)
				}
			}
		}
	}()

	go ProcessFirstTime(rdb, &state, &globalState)
	go SubscribeTransients(rdb, &state, &globalState)

	// Keep running
	select {}
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

func ExtractWebhookID(url string) (string, error) {
	matches := webhookIDPattern.FindStringSubmatch(url)
	if len(matches) < 2 {
		return "", fmt.Errorf("no webhook ID found in URL")
	}
	return matches[1], nil
}

func SetGloballyRateLimited(rdb *redis.Client, resetTime time.Time, resetAfter time.Duration) {
	ctx := context.Background()
	val := strconv.FormatInt(resetTime.Unix(), 10)
	rdb.Set(ctx, discordGloballyRateLimited, val, resetAfter)
}

// Add a hash entry anytime a bucket is rate limited so we can count
// the number of rate limits within the user configured window size
// and return it from the API
func UpdateBucketRateLimitCount(rdb *redis.Client, globalState *globalState, bucket string) {
	ctx := context.Background()
	hashName := fmt.Sprintf("%s:%s", bucketRateLimitCountHash, bucket)
	key := strconv.FormatInt(time.Now().Unix(), 10)
	rdb.HSet(ctx, hashName, key, true)
	rdb.HExpire(ctx, hashName, globalState.RateLimitWindowSize, key)
}

// Flag a webhook error in Redis so the status is available to the API
// these are cleared on a successful request to Discord
func SetWebhookError(rdb *redis.Client, webhookID string, http_401, http_403, http_404 bool) {
	ctx := context.Background()
	key := fmt.Sprintf("%s:%s", webhookErrors, webhookID)
	payload := map[string]bool{
		"http_401": http_401,
		"http_403": http_403,
		"http_404": http_404,
	}
	rdb.HSet(ctx, key, payload)
}

func ClearWebhookError(rdb *redis.Client, webhookID string) {
	ctx := context.Background()
	key := fmt.Sprintf("%s:%s", webhookErrors, webhookID)
	payload := map[string]bool{
		"http_401": false,
		"http_403": false,
		"http_404": false,
	}
	rdb.HSet(ctx, key, payload)
}
