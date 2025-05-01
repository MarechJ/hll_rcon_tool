package servers

import (
	. "github.com/MarechJ/hll_rcon_tool/http/responder"
	"github.com/MarechJ/hll_rcon_tool/resources"
	"github.com/floriansw/go-hll-rcon/rconv2"
	"github.com/julienschmidt/httprouter"
	"net/http"
	"strconv"
)

type serverHandler struct {
	resource Servers
	pools    Pools
}

func NewServerHandler(resource Servers, pools Pools, r *httprouter.Router) *serverHandler {
	h := &serverHandler{
		resource: resource,
		pools:    pools,
	}
	h.init(r)
	return h
}

func (s *serverHandler) init(r *httprouter.Router) {
	r.GET("/servers", s.List)
	r.GET("/servers/:id", s.WithServer(s.Get))
	r.GET("/servers/:id/gamestate", s.WithConnection(s.GetGameState))
	r.GET("/servers/:id/players", s.WithConnection(s.GetOnlinePlayers))
}

func (s *serverHandler) WithServer(f func(w http.ResponseWriter, r *http.Request, p httprouter.Params, s resources.Server)) httprouter.Handle {
	return func(w http.ResponseWriter, r *http.Request, p httprouter.Params) {
		if id, err := strconv.Atoi(p.ByName("id")); err != nil {
			jr.BadRequest(w)
		} else if server, err := s.resource.Find(id); err != nil {
			jr.InternalServerError(w, b(err.Error()))
		} else if server == nil {
			jr.NotFound(w)
		} else {
			f(w, r, p, *server)
		}
	}
}

func (s *serverHandler) WithConnection(f func(w http.ResponseWriter, r *http.Request, p httprouter.Params, c *rconv2.Connection) error) httprouter.Handle {
	return func(w http.ResponseWriter, r *http.Request, p httprouter.Params) {
		if id, err := strconv.Atoi(p.ByName("id")); err != nil {
			jr.BadRequest(w)
		} else if server, err := s.resource.Find(id); err != nil {
			jr.InternalServerError(w, b(err.Error()))
		} else if server == nil {
			jr.NotFound(w)
		} else if server.State != resources.ServerStateActive {
			jr.BadRequest(w, b("server is not active"))
		} else if pool, err := s.pools.ForServer(*server); err != nil {
			jr.InternalServerError(w, b(err.Error()))
		} else {
			err = pool.WithConnection(r.Context(), func(c *rconv2.Connection) error {
				return f(w, r, p, c)
			})
			if err != nil {
				jr.InternalServerError(w, b(err.Error()))
			}
		}
	}
}

func (s *serverHandler) List(w http.ResponseWriter, _ *http.Request, _ httprouter.Params) {
	if l, err := s.resource.List(); err != nil {
		jr.InternalServerError(w)
	} else {
		jr.Ok(w, Json(renderServerList(l)))
	}
}

func (s *serverHandler) Get(w http.ResponseWriter, _ *http.Request, _ httprouter.Params, server resources.Server) {
	jr.Ok(w, Json(renderServer(server, false)))
}

func (s *serverHandler) GetGameState(w http.ResponseWriter, r *http.Request, _ httprouter.Params, c *rconv2.Connection) error {
	si, err := c.SessionInfo(r.Context())
	if err != nil {
		return err
	}
	jr.Ok(w, Json(renderGameState(si)))
	return nil
}

func (s *serverHandler) GetOnlinePlayers(w http.ResponseWriter, r *http.Request, _ httprouter.Params, c *rconv2.Connection) error {
	p, err := c.Players(r.Context())
	if err != nil {
		return err
	}
	jr.Ok(w, Json(renderPlayerList(p)))
	return nil
}
