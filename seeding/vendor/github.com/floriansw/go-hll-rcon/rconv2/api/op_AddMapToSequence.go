package api

type AddMapToSequence struct {
	MapName string `json:"mapName"`
	Index   int32  `json:"index"`
}
