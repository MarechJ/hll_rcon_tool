package rconv2

import (
	"errors"
	"fmt"
)

var (
	ErrInvalidCredentials = errors.New("wrong password")
)

type UnexpectedStatus struct {
	code    int
	message string
}

func NewUnexpectedStatus(code int, message string) *UnexpectedStatus {
	return &UnexpectedStatus{
		code:    code,
		message: message,
	}
}

func (u UnexpectedStatus) Error() string {
	return fmt.Sprintf("invalid status code received, got %d with message %s", u.code, u.message)
}

type Command interface {
	CommandName() string
}

type ValidatableCommand interface {
	Validate() error
}

func newConnectionRequestTimeout(currentPoolSize int) connectionRequestTimeout {
	return connectionRequestTimeout{
		openConnections: currentPoolSize,
	}
}

type connectionRequestTimeout struct {
	openConnections int
}

func (c connectionRequestTimeout) Error() string {
	return fmt.Sprintf("connection request timed out before a connection was available. Open connections: %d", c.openConnections)
}

func (c connectionRequestTimeout) Timeout() bool {
	return true
}
