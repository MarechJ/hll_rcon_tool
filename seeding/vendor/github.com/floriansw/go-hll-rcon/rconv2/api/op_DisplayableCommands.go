package api

type DisplayableCommands struct {
}

func (c DisplayableCommands) CommandName() string {
	return "test"
}

type GetDisplayableCommandsResponse struct {
	Entries []DisplayableCommandEntry `json:"entries"`
}

type DisplayableCommandEntry struct {
	Id                string `json:"iD"`
	FriendlyName      string `json:"friendlyName"`
	IsClientSupported bool   `json:"isClientSupported"`
}
