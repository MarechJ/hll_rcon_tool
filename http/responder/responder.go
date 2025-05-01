package responder

import (
	"bytes"
	"encoding/json"
	"log"
	"net/http"
)

func B(s string) []byte {
	return []byte(s)
}

func Json(s interface{}) []byte {
	b, _ := json.Marshal(s)
	return b
}

var (
	Jr = &Responser{
		WrapError: func(message string) []byte {
			err := map[string]string{"message": message}
			d, _ := json.Marshal(&err)
			return d
		},
		ContentType: "application/json",
	}
)

type Responser struct {
	WrapError   func(message string) []byte
	ContentType string
}

func (r *Responser) Ok(w http.ResponseWriter, data ...[]byte) {
	r.Respond(w, http.StatusOK, data...)
}

func (r *Responser) InternalServerError(w http.ResponseWriter, data ...[]byte) {
	r.Respond(w, http.StatusInternalServerError, data...)
}

func (r *Responser) BadRequest(w http.ResponseWriter, data ...[]byte) {
	r.Respond(w, http.StatusBadRequest, data...)
}

func (r *Responser) NotFound(w http.ResponseWriter, data ...[]byte) {
	r.Respond(w, http.StatusNotFound, data...)
}

func (r *Responser) Respond(w http.ResponseWriter, code int, content ...[]byte) {
	if len(content) == 0 {
		content = append(content, []byte(http.StatusText(code)))
	}
	if (code < 200 || code > 399) && r.WrapError != nil {
		wrapped := r.WrapError(string(bytes.Join(content, nil)))
		content = [][]byte{wrapped}
	}

	if len(content) > 0 {
		r.setContentTypeHeader(w)
	}
	w.WriteHeader(code)

	for _, c := range content {
		_, err := w.Write(c)
		if err != nil {
			log.Printf("error while writing http response: %s\n", err.Error())
			break
		}
	}
}

func (r *Responser) setContentTypeHeader(w http.ResponseWriter) {
	switch {
	case w.Header().Get("Content-Type") != "":
		return
	case r == nil || r.ContentType == "":
		w.Header().Set("Content-Type", "application/octet-stream")
	default:
		w.Header().Set("Content-Type", r.ContentType)
	}
}
