package main

import (
	"github.com/MarechJ/hll_rcon_tool/http/servers"
	"github.com/MarechJ/hll_rcon_tool/internal"
	"github.com/MarechJ/hll_rcon_tool/resources"
	"github.com/julienschmidt/httprouter"
	"log"
	"log/slog"
	"net/http"
	"os"
)

func main() {
	level := slog.LevelInfo
	if os.Getenv("DEBUG") != "" {
		level = slog.LevelDebug
	}
	l := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{Level: level}))
	serverResource := resources.NewEnvServers()
	pools := internal.NewPools(l)

	router := httprouter.New()
	servers.NewServerHandler(serverResource, pools, router)

	log.Fatal(http.ListenAndServe(":8080", router))
}
