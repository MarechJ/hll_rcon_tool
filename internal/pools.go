package internal

import (
	"fmt"
	"github.com/MarechJ/hll_rcon_tool/resources"
	"github.com/floriansw/go-hll-rcon/rconv2"
	"log/slog"
	"sync"
)

type details struct {
	server         resources.Server
	pool           *rconv2.ConnectionPool
	lastUpdateHash string
}

type pools struct {
	l  *slog.Logger
	rw sync.RWMutex
	// map of Server IDs to connection pool
	p map[int]*details
}

func NewPools(l *slog.Logger) *pools {
	return &pools{
		l: l,
		p: make(map[int]*details),
	}
}

func (p *pools) ForServer(s resources.Server) (*rconv2.ConnectionPool, error) {
	p.rw.RLock()
	if d, ok := p.p[s.Id]; ok && d.lastUpdateHash == s.ConnectionDetails.Hash() {
		p.rw.RUnlock()
		return d.pool, nil
	}

	p.rw.RUnlock()
	p.rw.Lock()
	defer p.rw.Unlock()
	pool, err := rconv2.NewConnectionPool(rconv2.ConnectionPoolOptions{
		Logger:   p.l.WithGroup(fmt.Sprintf("pool-%d", s.Id)),
		Hostname: s.ConnectionDetails.Host,
		Port:     s.ConnectionDetails.Port,
		Password: s.ConnectionDetails.Password,
	})
	if err != nil {
		return nil, err
	}
	p.p[s.Id] = &details{
		server:         s,
		pool:           pool,
		lastUpdateHash: s.ConnectionDetails.Hash(),
	}
	return p.p[s.Id].pool, nil
}
