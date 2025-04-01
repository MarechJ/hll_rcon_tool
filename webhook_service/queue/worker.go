package queue

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/MarechJ/hll_rcon_tool/webhook_service/discord"
	"github.com/redis/go-redis/v9"
	"log/slog"
	"math/rand"
	"net/http"
	"strconv"
	"time"
)

const (
	bucketQueuePrefix        = "discord_webhook_queue:bucket:"
	message404               = "discord_webhook:message404"
	bucketRateLimitCountHash = "discord_webhook_bucket_rl_count"
)

// BucketWorker Manages a rate limit bucket
type BucketWorker struct {
	logger              *slog.Logger
	rdb                 *redis.Client
	queueKey            string
	bucket              string
	maxMsgReattempts    int
	rateLimitWindowSize time.Duration
	rateLimit           *RateLimitState
	localRateLimit      *LocalRateLimit
	webhookErrors       *WebhookErrors
	queue               *Queue
}

func NewBucketWorker(l *slog.Logger, rdb *redis.Client, queue *Queue, localRateLimit *LocalRateLimit, webhookErrors *WebhookErrors, bucketID string, maxMsgReattempts int, rateLimitWindowSize time.Duration) *BucketWorker {
	return &BucketWorker{
		logger:              l,
		rdb:                 rdb,
		maxMsgReattempts:    maxMsgReattempts,
		localRateLimit:      localRateLimit,
		webhookErrors:       webhookErrors,
		queueKey:            bucketQueuePrefix + bucketID,
		bucket:              bucketID,
		rateLimit:           &RateLimitState{},
		queue:               queue,
		rateLimitWindowSize: rateLimitWindowSize,
	}
}

func (bw *BucketWorker) UpdateBucket(bucket string) {
	bw.bucket = bucket
	bw.queueKey = bucketQueuePrefix + bucket
}

// ProcessQueue handles a bucket queue with retries
func (bw *BucketWorker) ProcessQueue(ctx context.Context) {
	for {
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
			if wait > 0 {
				bw.logger.Info(fmt.Sprintf("Bucket %s waiting %v", bw.bucket, wait))
				time.Sleep(wait)
			}
			continue
		}

		// Grab our next message off the queue
		results, err := bw.rdb.BLPop(ctx, 5*time.Second, bw.queueKey).Result()
		if errors.Is(err, redis.Nil) {
			continue
		} else if err != nil {
			bw.logger.Error(fmt.Sprintf("Error popping from %s: %v", bw.queueKey, err))
			continue
		}

		var msg Message
		if err := json.Unmarshal([]byte(results[1]), &msg); err != nil {
			bw.logger.Error(fmt.Sprintf("Unmarshal error: %v, JSON: %s", err, results[1]))
			continue
		}
		msg.MessageNumber = rand.Int()

		// We retry rate limited messages N times instead of re-enqueuing them which can slow down
		// processing other messages; but doesn't let an unhandled bad message block a queue forever
		// and if we're getting an error on this message; we would very likely have errors on the remaining
		// messages anyway
		for attempts := 0; attempts < bw.maxMsgReattempts && !msg.Discardable; attempts++ {
			_, err := bw.SendWebhook(ctx, &msg)
			if err == nil {
				break
			}

			bw.logger.Info(fmt.Sprintf("Retry %d for %d in bucket %s: %v", attempts+1, msg.MessageNumber, bw.bucket, err))
			if attempts == 2 {
				bw.logger.Warn(fmt.Sprintf("Dropped after 3 retries: %s", msg.Payload.URL))
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

// SendWebhook Makes the HTTP request to Discord and updates rate limit state
func (bw *BucketWorker) SendWebhook(ctx context.Context, msg *Message) (string, error) {
	now := time.Now()
	if err := bw.localRateLimit.CheckLocalRateLimit(0, now); err != nil {
		return "", err
	}

	// Extract what we need to make our POST request to Discord
	payload := map[string]any{}
	if msg.Payload.Content != nil {
		payload["content"] = *msg.Payload.Content
	}
	payload["embeds"] = msg.Payload.Embeds
	if msg.Payload.AllowedMentions != nil {
		payload["allowed_mentions"] = msg.Payload.AllowedMentions
	}

	jsonPayload, err := json.Marshal(payload)
	if err != nil {
		return "", fmt.Errorf("marshal error: %v", err)
	}

	var resp *http.Response

	if msg.Edit {
		resp, err = discord.ExecuteWebhook("PATCH", jsonPayload, fmt.Sprintf("%s/messages/%s", msg.Payload.URL, *msg.Payload.MessageID))
	} else {
		resp, err = discord.ExecuteWebhook("POST", jsonPayload, msg.Payload.URL)
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
	webhookID, _ := discord.ExtractWebhookID(msg.Payload.URL)
	switch resp.StatusCode {
	case http.StatusUnauthorized:
		bw.webhookErrors.SetWebhookError(ctx, webhookID, true, false, false)
	case http.StatusForbidden:
		bw.webhookErrors.SetWebhookError(ctx, webhookID, false, true, false)
	case http.StatusNotFound:
		bw.webhookErrors.SetWebhookError(ctx, webhookID, false, false, true)
	}

	if resp.StatusCode == http.StatusNotFound {
		str := fmt.Sprintf("%s:%s", message404, *msg.Payload.MessageID)
		bw.rdb.Set(ctx, str, true, 0)
		if msg.Payload.MessageID != nil {
			return "", fmt.Errorf("HTTP 404 for %s", *msg.Payload.MessageID)
		} else {
			return "", fmt.Errorf("HTTP 404; no message ID included")
		}
	} else if resp.StatusCode == 400 || resp.StatusCode == http.StatusUnauthorized || resp.StatusCode == http.StatusForbidden {
		return "", fmt.Errorf("%s is not a valid webhook URL", msg.Payload.URL)

	} else if resp.StatusCode == http.StatusOK || resp.StatusCode == http.StatusNoContent || resp.StatusCode == http.StatusTooManyRequests {
		bw.webhookErrors.ClearWebhookError(ctx, webhookID)
		// These responses will contain valid rate limit headers
		bucket := resp.Header.Get("X-RateLimit-Bucket")

		if remaining, err := strconv.Atoi(resp.Header.Get("X-RateLimit-Remaining")); err == nil {
			bw.rateLimit.Remaining = remaining
		}
		if limit, err := strconv.Atoi(resp.Header.Get("X-RateLimit-Limit")); err == nil {
			bw.rateLimit.Limit = limit
		}
		if reset, err := strconv.ParseInt(resp.Header.Get("X-RateLimit-Reset"), 10, 64); err == nil {
			bw.rateLimit.ResetTime = time.Unix(reset, 0)
			// Pad the reset time two seconds because Discord are liars and following their header
			// responses exactly will still cause excessive 429s
			bw.rateLimit.ResetTime = bw.rateLimit.ResetTime.Add(time.Duration(2.0 * float64(time.Second)))

		}
		if resetAfter, err := strconv.ParseFloat(resp.Header.Get("X-RateLimit-Reset-After"), 64); err == nil {
			// Pad the reset time two seconds because Discord are liars and following their header
			// responses exactly will still cause excessive 429s
			bw.rateLimit.ResetAfter = time.Duration((resetAfter + 2.0) * float64(time.Second))
		}

		if resp.StatusCode == http.StatusTooManyRequests {
			bw.updateBucketRateLimitCount(bucket)
			bw.logger.Warn(fmt.Sprintf("HTTP %d for %s", resp.StatusCode, bucket))
			bw.rateLimit.RateLimited = true
			if resp.Header.Get("X-RateLimit-Global") != "" {
				// Set the global rate limit flag in Redis so it can be retrieved by the API
				// we don't explicitly check it because each worker will flag itself as rate limited
				// and the redis key will expire naturally due to the TTL
				bw.logger.Warn(fmt.Sprintf("Global rate limit hit, pausing for %v", bw.rateLimit.ResetAfter))
				bw.queue.SetGloballyRateLimited(ctx, true, bw.rateLimit.ResetTime, bw.rateLimit.ResetAfter)
				// Force wait by maxing out the requests in our local window
				bw.localRateLimit.GloballyRateLimited()
			}
			return bucket, &RateLimited{RateLimitSleepTime: bw.rateLimit.GetRateLimitSleepTime()}
		}

		bw.rateLimit.RateLimited = false
		return bucket, nil
	} else {
		return "", fmt.Errorf("unhandled HTTP status %d", resp.StatusCode)
	}
}

type RateLimited struct {
	RateLimitSleepTime time.Duration
}

func (r RateLimited) Error() string {
	return fmt.Sprintf("rate limited until %v", r.RateLimitSleepTime)
}

// updateBucketRateLimitCount Add a hash entry anytime a bucket is rate limited so we can count
// the number of rate limits within the user configured window size
// and return it from the API
func (bw *BucketWorker) updateBucketRateLimitCount(bucket string) {
	ctx := context.Background()
	hashName := fmt.Sprintf("%s:%s", bucketRateLimitCountHash, bucket)
	key := strconv.Itoa(int(time.Now().Unix()))
	bw.rdb.HSet(ctx, hashName, key, true)
	bw.rdb.HExpire(ctx, hashName, bw.rateLimitWindowSize, key)
}

// RateLimitState Tracks bucket specific rate limits
type RateLimitState struct {
	Remaining   int
	Limit       int
	ResetTime   time.Time
	ResetAfter  time.Duration
	RateLimited bool
}

func (r *RateLimitState) GetRateLimitSleepTime() time.Duration {
	if r.RateLimited {
		return time.Until(r.ResetTime)
	}

	return 0
}
