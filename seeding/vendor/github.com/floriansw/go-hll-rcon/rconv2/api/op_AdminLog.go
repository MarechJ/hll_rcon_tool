package api

import (
	"strconv"
	"strings"
	"time"
)

type AdminLog struct {
	LogBackTrackTime int32  `json:"logBackTrackTime"`
	Filters          string `json:"filters"`
}

type GetAdminLogResponse struct {
	Entries []AdminLogEntry `json:"entries"`
}

type AdminLogEntry struct {
	Timestamp string `json:"timestamp"`
	Message   string `json:"message"`
}

func (a AdminLogEntry) ReceivedTime() time.Time {
	li := strings.LastIndex(a.Timestamp, ":")
	p, _ := strconv.Atoi(a.Timestamp[li+1:])
	r, _ := time.Parse("2006.01.02-15:04:05", a.Timestamp[:li])
	return time.Date(r.Year(), r.Month(), r.Day(), r.Hour(), r.Minute(), r.Second(), p*1000000, r.Location())
}

func (a AdminLogEntry) EventTime() time.Time {
	s := strings.Index(a.Message, "(")
	c := strings.Index(a.Message, ")")
	if s == -1 || c == -1 {
		return time.Time{}
	}
	ts, err := strconv.ParseInt(a.Message[s+1:c], 10, 64)
	if err != nil {
		return time.Time{}
	}
	return time.Unix(ts, 0)
}
