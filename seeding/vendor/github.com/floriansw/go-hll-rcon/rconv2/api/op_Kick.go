package api

type Kick struct {
	Reason   string `json:"Reason"`
	PlayerId string `json:"PlayerId"`
}
