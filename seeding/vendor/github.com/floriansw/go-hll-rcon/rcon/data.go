package rcon

import (
	"errors"
	"fmt"
	"time"
)

var (
	ErrUnsupportedGameMode = errors.New("the command is not available for the current gamemode")
)

type PlayerId struct {
	Name      string
	SteamId64 string
}

type AdminId struct {
	Name      string
	SteamId64 string
	Role      string
}

type VipId struct {
	Name      string
	SteamId64 string
}

type Unit struct {
	Id   int
	Name string
}

type Score struct {
	CombatEffectiveness int
	Offensive           int
	Defensive           int
	Support             int
}

type PlayerInfo struct {
	Name      string
	SteamId64 string
	Team      string
	Role      string
	Loadout   string
	Unit      Unit
	Kills     int
	Deaths    int
	Score     Score
	Level     int
}

type PlayerCount struct {
	Axis   int
	Allies int
}

type GameScore struct {
	Axis   int
	Allies int
}

type GameState struct {
	Players       PlayerCount
	Score         GameScore
	RemainingTime time.Duration
	Map           string
	NextMap       string
}

type CapPoint string

func (c CapPoint) String() string {
	return string(c)
}

type CapPoints []CapPoint

func (c CapPoints) Exists(p string) bool {
	for _, point := range c {
		if p == point.String() {
			return true
		}
	}
	return false
}

type MapCapPoints []CapPoints

func newConnectionRequestTimeout(currentPoolSize int) connectionRequestTimeout {
	return connectionRequestTimeout{
		openConnections: currentPoolSize,
	}
}

type connectionRequestTimeout struct {
	openConnections int
}

func (c connectionRequestTimeout) Error() string {
	return fmt.Sprintf("connection request timed out before a connection was available. Open connections: %d", c.openConnections)
}

func (c connectionRequestTimeout) Timeout() bool {
	return true
}
