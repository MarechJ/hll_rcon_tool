package api

type PermanentBan struct {
	Reason    string `json:"Reason"`
	PlayerId  string `json:"PlayerId"`
	AdminName string `json:"AdminName"`
}
