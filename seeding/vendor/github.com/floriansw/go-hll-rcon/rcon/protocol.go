package rcon

import (
	"bytes"
	"context"
	"errors"
	"fmt"
	"net"
	"os"
	"strconv"
	"strings"
	"syscall"
	"time"
)

const (
	MSGLEN = 8196
)

var (
	ErrWriteSentUnequal = errors.New("write wrote less or more bytes than command is long")
)

var (
	CommandFailed          = errors.New("FAIL")
	ReconnectTriesExceeded = errors.New("there are no reconnects left")
)

type socket struct {
	con            net.Conn
	key            []byte
	pw             string
	host           string
	port           int
	reconnectCount int

	lastContext *context.Context
}

func (r *socket) SetContext(ctx context.Context) error {
	r.lastContext = &ctx
	if deadline, ok := ctx.Deadline(); ok {
		return r.con.SetDeadline(deadline)
	} else {
		return r.con.SetDeadline(time.Now().Add(20 * time.Second))
	}
}

func (r *socket) Context() context.Context {
	if r.lastContext != nil {
		return *r.lastContext
	}
	return context.Background()
}

func makeConnection(h string, p int) (net.Conn, []byte, error) {
	con, err := net.DialTimeout("tcp4", fmt.Sprintf("%s:%d", h, p), 5*time.Second)
	if err != nil {
		return nil, nil, err
	}
	// use an intermediate timeout, it's unlikely that a new connection times out, however, if it does for whatever reason
	// it might get stuck here
	err = con.SetDeadline(time.Now().Add(20 * time.Second))
	if err != nil {
		return nil, nil, err
	}
	xorKey := make([]byte, MSGLEN)
	_, err = con.Read(xorKey)
	if err != nil {
		return nil, nil, err
	}
	xorKey = bytes.Trim(xorKey, "\x00")

	return con, xorKey, err
}

func newSocket(h string, p int, pw string) (*socket, error) {
	r := &socket{
		pw:             pw,
		host:           h,
		port:           p,
		reconnectCount: 0,
	}
	return r, r.reconnect(nil)
}

func (r *socket) Close() error {
	return r.con.Close()
}

func (r *socket) login() error {
	login := r.xor([]byte(fmt.Sprintf("login %s", r.pw)))
	_, err := r.con.Write(login)
	if err != nil {
		return err
	}

	res, err := r.read(false)
	if err != nil {
		return err
	}
	if string(res) == "FAIL" {
		return CommandFailed
	}
	return nil
}

func (r *socket) listCommand(cmd string) ([]string, error) {
	err := r.write(cmd)
	if err != nil {
		return nil, err
	}
	a, err := r.read(false)
	if err != nil {
		return nil, err
	}
	lines := strings.Split(string(a), "\t")
	l, err := strconv.Atoi(lines[0])
	if err != nil {
		return []string{string(a)}, err
	}
	for {
		if strings.Count(string(a), "\t")-1 >= l {
			break
		}
		var ir []byte
		ir, err = r.read(false)
		if err != nil {
			return lines, err
		}
		a = append(a, ir...)
	}
	lines = strings.Split(string(a), "\t")[1:]
	var res []string
	for _, line := range lines {
		if line != "" {
			res = append(res, line)
		}
	}
	return res, nil
}

func (r *socket) command(cmd string) (string, error) {
	err := r.write(cmd)
	if err != nil {
		return "", err
	}
	a, err := r.read(false)
	if err != nil {
		return "", err
	}
	if string(a) == "FAIL" {
		return "", CommandFailed
	}
	return string(a), nil
}

func (r *socket) write(cmd string) error {
	s, err := r.con.Write(r.xor([]byte(cmd)))
	if errors.Is(err, syscall.EPIPE) {
		err = r.reconnect(err)
		if err != nil {
			return err
		}
		return r.write(cmd)
	}
	if s != len(cmd) {
		return fmt.Errorf("%w Cmd: %s (%d), sent: %d", ErrWriteSentUnequal, cmd, len(cmd), s)
	}
	if err != nil {
		r.resetReconnectCount()
	}
	return err
}

func (r *socket) reconnect(orig error) error {
	if r.reconnectCount > 3 {
		return ReconnectTriesExceeded
	}
	r.reconnectCount++
	con, xorKey, err := makeConnection(r.host, r.port)
	r.con = con
	err = r.SetContext(r.Context())
	if err != nil {
		return err
	}
	r.key = xorKey
	if err != nil {
		return fmt.Errorf("reconnect failed: %s, original error: %w", err.Error(), orig)
	}
	err = r.login()
	if err != nil {
		return fmt.Errorf("reconnect failed: %s, original error: %w", err.Error(), orig)
	}
	return nil
}

// read reads data from the connection, until data is returned or the connection times out.
// canTimeout indicates if a timeout is expected. This is actually only expected for the showlog command.
// otherwise, if a timeout occurs, the socket will automatically try to reconnect, assuming the connection is broken.
// If the reconnect fails multiple times, the underlying error is returned.
func (r *socket) read(canTimeout bool) ([]byte, error) {
	var answer []byte
	for i := 0; i <= 30; i++ {
		rb := make([]byte, MSGLEN)
		l, err := r.con.Read(rb)
		if errors.Is(err, syscall.ECONNRESET) || (!canTimeout && os.IsTimeout(err)) {
			err = r.reconnect(err)
			if err != nil {
				return nil, err
			}
			l, err = r.con.Read(rb)
		}
		if err != nil {
			return nil, err
		} else {
			r.resetReconnectCount()
		}
		rb = rb[:l]

		answer = append(answer, r.xor(rb)...)

		if len(rb) >= MSGLEN {
			continue
		}
		break
	}

	return answer, nil
}

func (r *socket) xor(b []byte) []byte {
	var msg []byte
	for i := range b {
		mb := b[i] ^ r.key[i%len(r.key)]
		msg = append(msg, mb)
	}
	return msg
}

func (r *socket) resetReconnectCount() {
	if r.reconnectCount != 0 {
		r.reconnectCount = 0
	}
}
