package queue

import (
	"context"
	"fmt"
	"github.com/redis/go-redis/v9"
)

const (
	webhookErrors = "discord_webhook_queue:webhook_id_errors"
)

type WebhookErrors struct {
	http401 bool
	http403 bool
	http404 bool

	rdb *redis.Client
}

func NewWebhookErrors(rdb *redis.Client) *WebhookErrors {
	return &WebhookErrors{
		rdb: rdb,
	}
}

func (wh *WebhookErrors) Payload() map[string]bool {
	return map[string]bool{
		"http_401": wh.http401,
		"http_403": wh.http403,
		"http_404": wh.http404,
	}
}

// SetWebhookError Flag a webhook error in Redis so the status is available to the API
// these are cleared on a successful request to Discord
func (wh *WebhookErrors) SetWebhookError(ctx context.Context, webhookID string, http401, http403, http404 bool) {
	key := fmt.Sprintf("%s:%s", webhookErrors, webhookID)
	wh.http401 = http401
	wh.http403 = http403
	wh.http404 = http404
	wh.rdb.HSet(ctx, key, wh.Payload())
}

func (wh *WebhookErrors) ClearWebhookError(ctx context.Context, webhookID string) {
	key := fmt.Sprintf("%s:%s", webhookErrors, webhookID)
	wh.http401 = false
	wh.http403 = false
	wh.http404 = false
	wh.rdb.HSet(ctx, key, wh.Payload())
}
