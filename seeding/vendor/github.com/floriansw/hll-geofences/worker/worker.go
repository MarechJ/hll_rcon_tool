package worker

import (
	"context"
	"fmt"
	"github.com/floriansw/go-hll-rcon/rconv2"
	"github.com/floriansw/go-hll-rcon/rconv2/api"
	"github.com/floriansw/hll-geofences/data"
	"log/slog"
	"slices"
	"sync"
	"time"
)

type worker struct {
	pool               *rconv2.ConnectionPool
	l                  *slog.Logger
	c                  data.Server
	axisFences         []data.Fence
	alliesFences       []data.Fence
	punishAfterSeconds time.Duration

	sessionTicker *time.Ticker
	playerTicker  *time.Ticker
	punishTicker  *time.Ticker

	current        *api.GetSessionResponse
	outsidePlayers sync.Map
}

func NewWorker(l *slog.Logger, pool *rconv2.ConnectionPool, c data.Server) *worker {
	punishAfterSeconds := 10
	if c.PunishAfterSeconds != nil {
		punishAfterSeconds = *c.PunishAfterSeconds
	}
	return &worker{
		l:                  l,
		pool:               pool,
		punishAfterSeconds: time.Duration(punishAfterSeconds) * time.Second,
		c:                  c,

		sessionTicker:  time.NewTicker(1 * time.Second),
		playerTicker:   time.NewTicker(500 * time.Millisecond),
		punishTicker:   time.NewTicker(time.Second),
		outsidePlayers: sync.Map{},
	}
}

func (w *worker) Run(ctx context.Context) {
	if err := w.populateSession(ctx); err != nil {
		w.l.Error("fetch-session", "error", err)
		return
	}

	go w.pollSession(ctx)
	go w.pollPlayers(ctx)
	go w.punishPlayers(ctx)
}

func (w *worker) populateSession(ctx context.Context) error {
	return w.pool.WithConnection(ctx, func(c *rconv2.Connection) error {
		si, err := c.SessionInfo(ctx)
		if err != nil {
			return err
		}
		w.current = si
		w.axisFences = w.applicableFences(w.c.AxisFence)
		w.alliesFences = w.applicableFences(w.c.AlliesFence)
		return nil
	})
}

func (w *worker) punishPlayers(ctx context.Context) {
	for {
		select {
		case <-w.punishTicker.C:
			w.outsidePlayers.Range(func(k, v interface{}) bool {
				id := k.(string)
				t := v.(time.Time)
				if time.Since(t) > w.punishAfterSeconds && time.Since(t) < w.punishAfterSeconds+5*time.Second {
					go w.punishPlayer(ctx, id)
				}
				return true
			})
		}
	}
}

func (w *worker) punishPlayer(ctx context.Context, id string) {
	err := w.pool.WithConnection(ctx, func(c *rconv2.Connection) error {
		return c.PunishPlayer(ctx, id, fmt.Sprintf(w.c.PunishMessage(), w.punishAfterSeconds.String()))
	})
	if err != nil {
		w.l.Error("poll-session", "error", err)
	}
	// give the observer time to get the new player position
	time.Sleep(5 * time.Second)
	w.outsidePlayers.Delete(id)
}

func (w *worker) pollSession(ctx context.Context) {
	for {
		select {
		case <-w.sessionTicker.C:
			if err := w.populateSession(ctx); err != nil {
				w.l.Error("poll-session", "error", err)
			}
		}
	}
}

func (w *worker) pollPlayers(ctx context.Context) {
	for {
		select {
		case <-w.playerTicker.C:
			if len(w.alliesFences) == 0 && len(w.axisFences) == 0 {
				continue
			}

			err := w.pool.WithConnection(ctx, func(c *rconv2.Connection) error {
				players, err := c.Players(ctx)
				if err != nil {
					return err
				}
				for _, player := range players.Players {
					go w.checkPlayer(ctx, player)
				}
				return nil
			})
			if err != nil {
				w.l.Error("poll-session", "error", err)
			}
		}
	}
}

var (
	alliedTeams = []api.PlayerTeam{
		api.PlayerTeamB8a,
		api.PlayerTeamDak,
		api.PlayerTeamGb,
		api.PlayerTeamRus,
		api.PlayerTeamUs,
	}
)

func (w *worker) checkPlayer(ctx context.Context, p api.GetPlayerResponse) {
	if !p.Position.IsSpawned() {
		return
	}
	g := p.Position.Grid(w.current)
	var fences []data.Fence
	if slices.Contains(alliedTeams, p.Team) {
		fences = w.alliesFences
	} else {
		fences = w.axisFences
	}
	if len(fences) == 0 {
		return
	}
	for _, f := range fences {
		if f.Includes(g) {
			w.outsidePlayers.Delete(p.Id)
			return
		}
	}
	if _, ok := w.outsidePlayers.Load(p.Id); ok {
		return
	}
	w.outsidePlayers.Store(p.Id, time.Now())
	w.l.Info("player-outside-fence", "player", p.Name, "grid", g)
	err := w.pool.WithConnection(ctx, func(c *rconv2.Connection) error {
		return c.MessagePlayer(ctx, p.Name, fmt.Sprintf(w.c.WarningMessage(), w.punishAfterSeconds.String()))
	})
	if err != nil {
		w.l.Error("message-player-outside-fence", "player", p.Name, "grid", g, "error", err)
	}
}

func (w *worker) applicableFences(f []data.Fence) (v []data.Fence) {
	for _, fence := range f {
		if fence.Matches(w.current) {
			v = append(v, fence)
		}
	}
	return
}
