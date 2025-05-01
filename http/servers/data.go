package servers

import (
	"github.com/MarechJ/hll_rcon_tool/http/responder"
	"github.com/MarechJ/hll_rcon_tool/resources"
	"github.com/floriansw/go-hll-rcon/rconv2"
)

var (
	jr = responder.Jr
	b  = responder.B
)

type Servers interface {
	List() ([]resources.Server, error)
	Find(id int) (*resources.Server, error)
}

type Pools interface {
	ForServer(s resources.Server) (*rconv2.ConnectionPool, error)
}
