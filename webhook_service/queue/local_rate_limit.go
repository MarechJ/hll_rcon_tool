package queue

import (
	"fmt"
	"sync"
	"time"
)

// LocalRateLimit Tracks our local rate limit window
type LocalRateLimit struct {
	requests    int
	maxRequests int
	window      time.Time
	mu          sync.Mutex
}

func NewLocalRateLimit(maxRequests int) *LocalRateLimit {
	return &LocalRateLimit{
		maxRequests: maxRequests,
	}
}

func (state *LocalRateLimit) GloballyRateLimited() {
	_ = state.CheckLocalRateLimit(state.maxRequests, time.Now())
}

// CheckLocalRateLimit Keeps us under `HLL_LOCAL_MAX_SENDS_PER_SEC` across all requests
func (state *LocalRateLimit) CheckLocalRateLimit(requests int, now time.Time) error {
	state.mu.Lock()
	defer state.mu.Unlock()

	// If it's been more than 1 second since our last request; reset the window
	if now.Sub(state.window) >= time.Second {
		state.requests = requests
		state.window = now
	}

	// Don't exceed our configured max requests per second
	if state.requests >= state.maxRequests {
		return fmt.Errorf("local rate limit exceeded")
	}

	state.requests++
	return nil
}
