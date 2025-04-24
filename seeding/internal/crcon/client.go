package crcon

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
)

type Authentication interface {
	GetInternalApiKey() string
}

type client struct {
	h       *http.Client
	auth    Authentication
	baseUrl string
}

func NewClient(baseUrl string, auth Authentication) *client {
	return &client{
		h:       &http.Client{},
		auth:    auth,
		baseUrl: baseUrl,
	}
}

type response[T any] struct {
	Result T `json:"result"`
}

type autoModSeedingConfig struct {
	Enabled         bool `json:"enabled"`
	DryRun          bool `json:"dry_run"`
	EnforceCapFight struct {
		MinPlayers       int    `json:"min_players"`
		MaxPlayers       int    `json:"max_players"`
		MaxCaps          int    `json:"max_caps"`
		SkipWarning      bool   `json:"skip_warning"`
		ViolationMessage string `json:"violation_message"`
	} `json:"enforce_cap_fight"`
}

func (c *client) GetAutoModSeedingConfig(ctx context.Context) (*AutoModSeedingConfig, error) {
	req, err := http.NewRequest("GET", fmt.Sprintf("%s/api/get_auto_mod_seeding_config", c.baseUrl), nil)
	if err != nil {
		return nil, err
	}
	req = req.WithContext(ctx)
	req.Header.Set("Authorization", "Bearer "+c.auth.GetInternalApiKey())
	res, err := c.h.Do(req)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()
	var d response[autoModSeedingConfig]
	err = json.NewDecoder(res.Body).Decode(&d)
	if err != nil {
		return nil, err
	}
	return &AutoModSeedingConfig{
		Enabled: d.Result.Enabled,
		DryRun:  d.Result.DryRun,
		EnforceCapFight: EnforceCapFight{
			MinPlayers:       d.Result.EnforceCapFight.MinPlayers,
			MaxPlayers:       d.Result.EnforceCapFight.MaxPlayers,
			MaxCaps:          d.Result.EnforceCapFight.MaxCaps,
			SkipWarning:      d.Result.EnforceCapFight.SkipWarning,
			ViolationMessage: d.Result.EnforceCapFight.ViolationMessage,
		}}, nil
}
