package api

type MoveMapInSequence struct {
	CurrentIndex int32 `json:"CurrentIndex"`
	NewIndex     int32 `json:"NewIndex"`
}
