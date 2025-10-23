package internal

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"strings"
)

type Authentication struct {
	apiKey string
}

func NewAuthentication(hllPassword, rconWebApiSecret string) *Authentication {
	if hllPassword == "" {
		panic("HLL_PASSWORD not set")
	}
	if rconWebApiSecret == "" {
		// from rconweb/settings.py SECRET_KEY default
		rconWebApiSecret = "9*i9zm1jx(5y-ns=*r6p%#6-q!bst98u3o3pw6joyf#-e(bh(0"
	}
	h := hmac.New(sha256.New, []byte(rconWebApiSecret))
	h.Write([]byte(hllPassword))
	return &Authentication{
		apiKey: strings.ToUpper(hex.EncodeToString(h.Sum(nil))),
	}
}

func (a *Authentication) GetInternalApiKey() string {
	return a.apiKey
}
