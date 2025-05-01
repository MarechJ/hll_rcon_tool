package resources

import (
	"os"
	"strconv"
)

type envServers struct {
	server Server
}

func NewEnvServers() *envServers {
	server := Server{
		Id:                1,
		Name:              "Environment Server",
		State:             ServerStateActive,
		ConnectionDetails: &RConDetails{},
	}
	port, err := strconv.Atoi(os.Getenv("HLL_PORT"))
	if err != nil {
		server.State = ServerStateInactive
	} else {
		server.ConnectionDetails.Port = port
	}
	if h, ok := os.LookupEnv("HLL_HOST"); ok {
		server.ConnectionDetails.Host = h
	} else {
		server.State = ServerStateInactive
	}
	if pw, ok := os.LookupEnv("HLL_PASSWORD"); ok {
		server.ConnectionDetails.Password = pw
	} else {
		server.State = ServerStateInactive
	}
	return &envServers{
		server: server,
	}
}

func (e *envServers) List() ([]Server, error) {
	return []Server{
		{
			Id:                e.server.Id,
			Name:              e.server.Name,
			State:             e.server.State,
			ConnectionDetails: nil,
		},
	}, nil
}

func (e *envServers) Find(id int) (*Server, error) {
	if id == e.server.Id {
		return &e.server, nil
	}
	return nil, nil
}
