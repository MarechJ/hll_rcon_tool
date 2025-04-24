package api

type SetIdleKickDuration struct {
	IdleTimeoutMinutes int32 `json:"IdleTimeoutMinutes"`
}
