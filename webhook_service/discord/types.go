package discord

import "encoding/json"

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
