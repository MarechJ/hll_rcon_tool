package rconv2

import (
	"context"
	"github.com/floriansw/go-hll-rcon/rconv2/api"
)

// Connection represents a persistent connection to a HLL server using RCon. It can be used to issue commands against
// the HLL server and query data. The connection can either be utilised using the higher-level API methods, or by sending
// raw commands using ListCommand or Command.
//
// A Connection is not thread-safe by default. Do not attempt to run multiple commands (either of the higher-level or
// low-level API). Doing so may either run into non-expected indefinitely blocking execution (until the context.Context
// deadline exceeds) or to mixed up data (sending a command and getting back the response for another command).
// Instead, in goroutines use a ConnectionPool and request a new connection for each goroutine. The ConnectionPool will
// ensure that one Connection is only used once at the same time. It also speeds up processing by opening a number of
// Connections until the pool size is reached.
type Connection struct {
	id     string
	socket *socket
}

func (c *Connection) Players(ctx context.Context) (*api.GetPlayersResponse, error) {
	return execCommand[api.ServerInformation, api.GetPlayersResponse](ctx, c.socket, api.ServerInformation{
		Name: api.ServerInformationNamePlayers,
	})
}

func (c *Connection) Player(ctx context.Context, playerId string) (*api.GetPlayerResponse, error) {
	return execCommand[api.ServerInformation, api.GetPlayerResponse](ctx, c.socket, api.ServerInformation{
		Name:  api.ServerInformationNamePlayer,
		Value: playerId,
	})
}

func (c *Connection) ServerConfig(ctx context.Context) (*api.GetServerConfigResponse, error) {
	return execCommand[api.ServerInformation, api.GetServerConfigResponse](ctx, c.socket, api.ServerInformation{
		Name: api.ServerInformationNameServerConfig,
	})
}

func (c *Connection) SessionInfo(ctx context.Context) (*api.GetSessionResponse, error) {
	return execCommand[api.ServerInformation, api.GetSessionResponse](ctx, c.socket, api.ServerInformation{
		Name: api.ServerInformationNameSession,
	})
}

func (c *Connection) MapRotation(ctx context.Context) (*api.GetMapRotationResponse, error) {
	return execCommand[api.ServerInformation, api.GetMapRotationResponse](ctx, c.socket, api.ServerInformation{
		Name: api.ServerInformationNameMapRotation,
	})
}

func (c *Connection) MapSequence(ctx context.Context) (*api.GetMapSequenceResponse, error) {
	return execCommand[api.ServerInformation, api.GetMapSequenceResponse](ctx, c.socket, api.ServerInformation{
		Name: api.ServerInformationNameMapSequence,
	})
}

func (c *Connection) DisplayableCommands(ctx context.Context) (*api.GetDisplayableCommandsResponse, error) {
	return execCommand[api.DisplayableCommands, api.GetDisplayableCommandsResponse](ctx, c.socket, api.DisplayableCommands{})
}

func (c *Connection) AdminLog(ctx context.Context, timeSeconds int32, filter string) (*api.GetAdminLogResponse, error) {
	return execCommand[api.AdminLog, api.GetAdminLogResponse](ctx, c.socket, api.AdminLog{
		LogBackTrackTime: timeSeconds,
		Filters:          filter,
	})
}

func (c *Connection) MapChange(ctx context.Context, mapName string) error {
	_, err := execCommand[api.MapChange, any](ctx, c.socket, api.MapChange{
		MapName: mapName,
	})
	return err
}

func (c *Connection) ChangeSectorLayout(ctx context.Context, sectors []string) error {
	r := api.ChangeSectorLayout{}
	for i, sector := range sectors {
		if i == 0 {
			r.SectorOne = sector
		}
		if i == 1 {
			r.SectorTwo = sector
		}
		if i == 2 {
			r.SectorThree = sector
		}
		if i == 3 {
			r.SectorFour = sector
		}
		if i == 4 {
			r.SectorFive = sector
		}
	}
	_, err := execCommand[api.ChangeSectorLayout, any](ctx, c.socket, r)
	return err
}

func (c *Connection) AddAdmin(ctx context.Context, playerId, adminGroup, comment string) error {
	_, err := execCommand[api.AddAdmin, any](ctx, c.socket, api.AddAdmin{
		PlayerId:   playerId,
		AdminGroup: adminGroup,
		Comment:    comment,
	})
	return err
}

func (c *Connection) AddMapToRotation(ctx context.Context, mapName string, index int32) error {
	_, err := execCommand[api.AddMapToRotation, any](ctx, c.socket, api.AddMapToRotation{
		MapName: mapName,
		Index:   index,
	})
	return err
}

func (c *Connection) AddMapToSequence(ctx context.Context, mapName string, index int32) error {
	_, err := execCommand[api.AddMapToSequence, any](ctx, c.socket, api.AddMapToSequence{
		MapName: mapName,
		Index:   index,
	})
	return err
}

func (c *Connection) RemoveMapFromRotation(ctx context.Context, index int32) error {
	_, err := execCommand[api.RemoveMapFromRotation, any](ctx, c.socket, api.RemoveMapFromRotation{
		Index: index,
	})
	return err
}

func (c *Connection) RemoveMapToSequence(ctx context.Context, index int32) error {
	_, err := execCommand[api.RemoveMapFromSequence, any](ctx, c.socket, api.RemoveMapFromSequence{
		Index: index,
	})
	return err
}

func (c *Connection) ShuffleMapSequence(ctx context.Context, enable bool) error {
	_, err := execCommand[api.ShuffleMapSequence, any](ctx, c.socket, api.ShuffleMapSequence{
		Enable: enable,
	})
	return err
}

func (c *Connection) MoveMapInSequence(ctx context.Context, currentIndex, newIndex int32) error {
	_, err := execCommand[api.MoveMapInSequence, any](ctx, c.socket, api.MoveMapInSequence{
		CurrentIndex: currentIndex,
		NewIndex:     newIndex,
	})
	return err
}

func (c *Connection) SetTeamSwitchCooldown(ctx context.Context, timer int32) error {
	_, err := execCommand[api.SetTeamSwitchCooldown, any](ctx, c.socket, api.SetTeamSwitchCooldown{
		TeamSwitchTimer: timer,
	})
	return err
}

func (c *Connection) SetMaxQueuedPlayers(ctx context.Context, maxQueuedPlayers int32) error {
	_, err := execCommand[api.SetMaxQueuedPlayers, any](ctx, c.socket, api.SetMaxQueuedPlayers{
		MaxQueuedPlayers: maxQueuedPlayers,
	})
	return err
}

func (c *Connection) SetIdleKickDuration(ctx context.Context, idleTimeoutMinutes int32) error {
	_, err := execCommand[api.SetIdleKickDuration, any](ctx, c.socket, api.SetIdleKickDuration{
		IdleTimeoutMinutes: idleTimeoutMinutes,
	})
	return err
}

func (c *Connection) SendServerMessage(ctx context.Context, msg string) error {
	_, err := execCommand[api.SendServerMessage, any](ctx, c.socket, api.SendServerMessage{
		Message: msg,
	})
	return err
}

func (c *Connection) ServerBroadcast(ctx context.Context, msg string) error {
	_, err := execCommand[api.ServerBroadcast, any](ctx, c.socket, api.ServerBroadcast{
		Message: msg,
	})
	return err
}

func (c *Connection) SetHighPingThreshold(ctx context.Context, highPingMs int32) error {
	_, err := execCommand[api.SetHighPingThreshold, any](ctx, c.socket, api.SetHighPingThreshold{
		HighPingThresholdMs: highPingMs,
	})
	return err
}

func (c *Connection) MessagePlayer(ctx context.Context, playerId, message string) error {
	_, err := execCommand[api.MessagePlayer, any](ctx, c.socket, api.MessagePlayer{
		Message:  message,
		PlayerId: playerId,
	})
	return err
}

func (c *Connection) PunishPlayer(ctx context.Context, playerId, reason string) error {
	_, err := execCommand[api.PunishPlayer, any](ctx, c.socket, api.PunishPlayer{
		Reason:   reason,
		PlayerId: playerId,
	})
	return err
}

func (c *Connection) Kick(ctx context.Context, playerId, reason string) error {
	_, err := execCommand[api.Kick, any](ctx, c.socket, api.Kick{
		Reason:   reason,
		PlayerId: playerId,
	})
	return err
}

func (c *Connection) TempBan(ctx context.Context, playerId string, duration int32, reason, adminName string) error {
	_, err := execCommand[api.TempBan, any](ctx, c.socket, api.TempBan{
		Reason:    reason,
		PlayerId:  playerId,
		Duration:  duration,
		AdminName: adminName,
	})
	return err
}

func (c *Connection) RemoveTempBan(ctx context.Context, playerId string) error {
	_, err := execCommand[api.RemoveTempBan, any](ctx, c.socket, api.RemoveTempBan{
		PlayerId: playerId,
	})
	return err
}

func (c *Connection) PermanentBan(ctx context.Context, playerId, reason, adminName string) error {
	_, err := execCommand[api.PermanentBan, any](ctx, c.socket, api.PermanentBan{
		Reason:    reason,
		PlayerId:  playerId,
		AdminName: adminName,
	})
	return err
}

func (c *Connection) RemovePermanentBan(ctx context.Context, playerId string) error {
	_, err := execCommand[api.RemovePermanentBan, any](ctx, c.socket, api.RemovePermanentBan{
		PlayerId: playerId,
	})
	return err
}

func (c *Connection) AutoBalance(ctx context.Context, enable bool) error {
	_, err := execCommand[api.AutoBalance, any](ctx, c.socket, api.AutoBalance{
		EnableAutoBalance: enable,
	})
	return err
}

func (c *Connection) AutoBalanceThreshold(ctx context.Context, threshold int32) error {
	_, err := execCommand[api.AutoBalanceThreshold, any](ctx, c.socket, api.AutoBalanceThreshold{
		AutoBalanceThreshold: threshold,
	})
	return err
}

func (c *Connection) VoteKickEnabled(ctx context.Context, enabled bool) error {
	_, err := execCommand[api.VoteKickEnabled, any](ctx, c.socket, api.VoteKickEnabled{
		Enabled: enabled,
	})
	return err
}

func (c *Connection) ResetKickThreshold(ctx context.Context) error {
	_, err := execCommand[api.ResetKickThreshold, any](ctx, c.socket, api.ResetKickThreshold{})
	return err
}

func (c *Connection) VoteKickThreshold(ctx context.Context, threshold string) error {
	_, err := execCommand[api.VoteKickThreshold, any](ctx, c.socket, api.VoteKickThreshold{
		ThresholdValue: threshold,
	})
	return err
}

func (c *Connection) ClientReferenceData(ctx context.Context, command string) (*string, error) {
	return execCommand[api.ClientReferenceData, string](ctx, c.socket, api.ClientReferenceData(command))
}

func execCommand[T, U any](ctx context.Context, so *socket, req T) (result *U, err error) {
	err = so.SetContext(ctx)
	if err != nil {
		return nil, err
	}
	r := Request[T, U]{
		Body: req,
	}
	res, err := r.do(so)
	if err != nil {
		return nil, err
	}
	if res.StatusCode != 200 {
		return nil, NewUnexpectedStatus(res.StatusCode, res.StatusMessage)
	}
	body := res.Body()
	return &body, nil
}
