package api

type AddAdmin struct {
	PlayerId   string `json:"playerId"`
	AdminGroup string `json:"adminGroup"`
	Comment    string `json:"comment"`
}
