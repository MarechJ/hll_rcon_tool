package discord

import (
	"bytes"
	"fmt"
	"net/http"
	"regexp"
)

var webhookIDPattern = regexp.MustCompile(`webhooks/([0-9]+)/`)

func ExtractWebhookID(url string) (string, error) {
	matches := webhookIDPattern.FindStringSubmatch(url)
	if len(matches) < 2 {
		return "", fmt.Errorf("no webhook ID found in URL")
	}
	return matches[1], nil
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
