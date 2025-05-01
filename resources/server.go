package resources

import (
	"crypto/sha256"
	"encoding/hex"
	"strconv"
)

var (
	ServerStateActive   = ServerState("active")
	ServerStateInactive = ServerState("inactive")
)

type ServerState string

type Server struct {
	Id                int
	Name              string
	State             ServerState
	ConnectionDetails *RConDetails
}

type RConDetails struct {
	Host     string
	Port     int
	Password string
}

func (r RConDetails) Hash() string {
	h := sha256.New()
	h.Write([]byte(r.Host))
	h.Write([]byte(strconv.Itoa(r.Port)))
	h.Write([]byte(r.Password))
	return hex.EncodeToString(h.Sum(nil))
}
