package rconv2

import (
	"context"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"os"
	"sync"
	"syscall"
	"time"
)

var (
	defaultTimeout = 5 * time.Second
)

type ConnectionPoolOptions struct {
	// Logger is an optional logging instance. If passed in, the pool will issue debug information to this logger instance
	// for, well, debugging purposes. In a production environment, this instance is not required and can be nil.
	// The passed in logger instance is not modified, meaning if it logs on a logging level higher than slog.LevelDebug,
	// no messages will be seen from the pool.
	Logger *slog.Logger
	// Hostname is the hostname/IP address of the Hell Let Loose server where it can be reached.
	// Only IPv4 addresses are supported.
	Hostname string
	// Port is the Hell Let Loose RCon port of the server. The RCon port can usually be found in the Game Service Provider's
	// server management console.
	Port int
	// Password is the RCon password of the Hell Let Loose server used to authenticate.
	Password string

	// MaxOpenConnections is the maximum number of open connections the pool can not exceed. A request for a connection
	// when the pool reached this size (and no idle connections are available) will be put into a queue and be served
	// once a connection is returned to the pool. This queue is on the best effort basis and might fail based on the
	// provided deadline to Get.
	// The number of requests that can be put into a queue is not limited.
	MaxOpenConnections *int
	// MaxIdleConnections is the maximum number of idle connections in the pool. Idle connections are established connections to
	// the server (warm) but are not currently in use. Warm connections are preferably used to fulfill connection requests
	// (Get) to reduce the overhead of opening and closing a connection on every request. Consider a high max
	// idle connection to benefit from re-using connections as much as possible.
	// MaxIdleConnections cannot be greater than MaxOpenConnections
	MaxIdleConnections *int
}

func NewConnectionPool(opts ConnectionPoolOptions) (*ConnectionPool, error) {
	if opts.Logger == nil {
		opts.Logger = slog.New(slog.NewTextHandler(io.Discard, &slog.HandlerOptions{Level: slog.LevelError}))
	}
	if opts.Hostname == "" {
		return nil, errors.New("hostname cannot be an empty string")
	}
	if opts.Port <= 0 || opts.Port > 65_536 {
		return nil, errors.New("port must be a positive integer greater than 0 and lower than 65,536")
	}
	if toInt(opts.MaxOpenConnections) == 0 {
		opts.MaxOpenConnections = fromInt(10)
	}
	if toInt(opts.MaxIdleConnections) == 0 {
		opts.MaxIdleConnections = fromInt(10)
	}
	if toInt(opts.MaxIdleConnections) > toInt(opts.MaxOpenConnections) {
		return nil, errors.New("the MaxIdleConnections cannot exceed MaxOpenConnections")
	}
	return &ConnectionPool{
		logger:       opts.Logger,
		host:         opts.Hostname,
		port:         opts.Port,
		pw:           opts.Password,
		mu:           sync.Mutex{},
		idles:        map[string]*Connection{},
		maxOpenCount: toInt(opts.MaxOpenConnections),
		maxIdleCount: toInt(opts.MaxIdleConnections),
	}, nil
}

type ConnectionPool struct {
	logger       *slog.Logger
	host         string
	port         int
	pw           string
	mu           sync.Mutex
	idles        map[string]*Connection
	numOpen      int
	maxOpenCount int
	maxIdleCount int
	queued       []request
}

type request struct {
	connChan chan *Connection
	errChan  chan error
}

func IsBrokenHllConnection(err error) bool {
	return err != nil &&
		(os.IsTimeout(err) ||
			errors.Is(err, syscall.ECONNRESET) ||
			errors.Is(err, syscall.ECONNREFUSED) ||
			errors.Is(err, syscall.ECONNREFUSED) ||
			errors.Is(err, syscall.EPIPE))
}

// Return returns a previously gathered Connection from Get back to the pool for later use. The Connection
// might either be closed, put into a pool of "hot", idle connections or directly returned to a queued Get
// request.
func (p *ConnectionPool) Return(c *Connection, err error) {
	l := p.logger.With("action", "return", "id", c.id)
	l.Debug("wait-for-lock")
	p.mu.Lock()
	defer p.mu.Unlock()

	if IsBrokenHllConnection(err) {
		l.Debug("retire-broken", "error", err)
		c.socket.Close()
		p.numOpen--
	} else if len(p.queued) != 0 {
		r := p.queued[0]
		l.Debug("re-using-for-queue")
		p.queued = p.queued[1:]
		r.connChan <- c
	} else if p.maxIdleCount > len(p.idles) {
		l.Debug("returning-idle")
		p.idles[c.id] = c
	} else {
		l.Debug("closing")
		c.socket.Close()
		p.numOpen--
	}
}

// Get returns a connection from the pool. This method does not guarantee you to get a new, fresh Connection.
// A Connection might either be opened newly for this request, re-used from the pool of idle connections or one that was
// returned to the pool just now.
//
// If there are no idle connections and if the limit of open connections is already reached, the request to retrieve a
// Connection will be queued. The request might or might not be fulfilled later, once a Connection is returned to the
// pool.
//
// It is recommended to provide a context.Context with a deadline. The deadline will be the maximum time the caller is
// ok with waiting for a connection before a Timeout error is returned. If no deadline is provided in the context.Context,
// Get might wait indefinitely.
func (p *ConnectionPool) Get(ctx context.Context) (*Connection, error) {
	deadline, ok := ctx.Deadline()
	l := p.logger.With("action", "get-with-context", "deadline", deadline, "hasDeadline", ok, "queued", len(p.queued), "open", p.numOpen, "idles", len(p.idles))
	l.Debug("wait-for-lock")
	p.mu.Lock()

	if len(p.idles) > 0 {
		defer p.mu.Unlock()
		l.Debug("from-idle-pool")
		for _, c := range p.idles {
			delete(p.idles, c.id)
			return c, nil
		}
	}

	if p.numOpen >= p.maxOpenCount {
		l.Debug("queue-request", "queued", len(p.queued), "open", p.numOpen)
		req := request{
			connChan: make(chan *Connection, 1),
			errChan:  make(chan error, 1),
		}

		p.queued = append(p.queued, req)
		p.mu.Unlock()

		timeout := defaultTimeout
		if d, o := ctx.Deadline(); o {
			timeout = time.Until(d)
		}

		select {
		case con := <-req.connChan:
			return con, nil
		case err := <-req.errChan:
			return nil, err
		case <-time.After(timeout):
			return nil, newConnectionRequestTimeout(p.numOpen)
		}
	}

	l.Debug("open-new", "queued", len(p.queued), "open", p.numOpen)
	p.numOpen++
	defer p.mu.Unlock()

	nc, err := p.new()
	if err != nil {
		p.numOpen--
		return nil, err
	}

	return nc, nil
}

// WithConnection gathers a connection from the pool, if available, and executes the passed in function f.
// Once the function returns, the connection is correctly returned to the pool with the error returned from f to ensure
// the connection is not kept.
//
// This is a helper to reduce the possibility a connection is obtained from the pool, but then not returned to it. It
// is basically the same as using Get and Return in your own code.
func (p *ConnectionPool) WithConnection(ctx context.Context, f func(c *Connection) error) error {
	c, err := p.Get(ctx)
	if err != nil {
		return err
	}
	var cerr error
	defer p.Return(c, cerr)

	cerr = f(c)
	return nil
}

func (p *ConnectionPool) new() (*Connection, error) {
	c, err := newSocket(p.host, p.port, p.pw)
	if err != nil {
		return nil, err
	}

	return &Connection{
		id:     fmt.Sprintf("%d", time.Now().UnixNano()),
		socket: c,
	}, nil
}

func (p *ConnectionPool) Shutdown() {
	p.mu.Lock()
	for _, c := range p.idles {
		c.socket.Close()
		p.numOpen--
	}
	p.mu.Unlock()
}
