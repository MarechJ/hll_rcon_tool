package main

import (
	"context"
	"log/slog"
	"os"
	"os/signal"
	"seeding/internal"
	"seeding/internal/crcon"
	"strconv"
	"syscall"
	"time"

	"github.com/floriansw/go-hll-rcon/rconv2"
	"github.com/floriansw/hll-geofences/data"
	"github.com/floriansw/hll-geofences/worker"
)

var (
	hllPassword      = os.Getenv("HLL_PASSWORD")
	hllHost          = os.Getenv("HLL_HOST")
	hllPort          = os.Getenv("HLL_PORT")
	rconWebApiSecret = os.Getenv("RCONWEB_API_SECRET")
	rconBackendUrl   = os.Getenv("RCONWEB_BACKEND_URL")

	punishAfterSeconds = 10

	// designates the map orientation from left to right
	alliedToAxisHorizontalMaps = []string{"CARENTAN", "HILL 400", "HÜRTGEN FOREST", "MORTAIN"}
	axisToAlliedHorizontalMaps = []string{"EL ALAMEIN", "OMAHA BEACH", "SAINTE-MÈRE-ÉGLISE", "STALINGRAD", "TOBRUK", "UTAH BEACH"}
	// designates the map orientation from top to bottom
	alliedToAxisVerticalMaps = []string{"ELSENBORN RIDGE", "KHARKOV", "KURSK", "PURPLE HEART LANE", "ST MARIE DU MONT"}
	axisToAlliedVerticalMaps = []string{"DRIEL", "FOY", "REMAGEN"}

	horizontalCaps = []string{"A", "B", "C", "D", "E", "F", "G", "H", "I", "J"}
)

type CRConClient interface {
	GetAutoModSeedingConfig(ctx context.Context) (*crcon.AutoModSeedingConfig, error)
}

func main() {
	level := slog.LevelInfo
	if _, ok := os.LookupEnv("DEBUG"); ok {
		level = slog.LevelDebug
	}

	logger := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{Level: level}))

	if rconBackendUrl == "" {
		rconBackendUrl = "http://backend:8000"
	}

	ctx, cancel := context.WithCancel(context.Background())
	a := internal.NewAuthentication(hllPassword, rconWebApiSecret)
	c := crcon.NewClient(rconBackendUrl, a)

	go scheduleWorker(ctx, logger, c)

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
	<-stop

	logger.Info("graceful-shutdown")
	cancel()
}

func scheduleWorker(ctx context.Context, logger *slog.Logger, c CRConClient) {
	refreshConfig := time.NewTicker(time.Second * 5)

	var (
		childCtx, cancelFn = context.WithCancel(ctx)
		previous           *crcon.AutoModSeedingConfig
	)
	for {
		select {
		case <-ctx.Done():
			refreshConfig.Stop()
			cancelFn()
			return
		case <-refreshConfig.C:
			ac, err := c.GetAutoModSeedingConfig(childCtx)
			if err != nil {
				logger.Error("find-seeding-automod-config", "error", err)
				continue
			}
			if ac.Equals(previous) {
				continue
			}
			logger.Info("config-updated-restart")
			cancelFn()
			previous = ac
			childCtx, cancelFn = context.WithCancel(ctx)
			initialize(childCtx, logger, ac)
		}
	}
}

func initialize(ctx context.Context, logger *slog.Logger, ac *crcon.AutoModSeedingConfig) {
	// Prefilling fences for first-spawners on the server. Whenever a player joins a server, they are randomly assigned
	// a spawn on either side (even before side selection). To not give them a warning that they are outside of the spawns
	// during seeding, the HQ lines for each team opponent are allowlisted as well.
	alliedFences := []data.Fence{

		{
			X: &horizontalCaps[0],
			Condition: &data.Condition{
				Equals: map[string][]string{
					"map_name": axisToAlliedHorizontalMaps,
				},
			},
		},
		{
			X: &horizontalCaps[9],
			Condition: &data.Condition{
				Equals: map[string][]string{
					"map_name": alliedToAxisHorizontalMaps,
				},
			},
		},
		{
			Y: internal.Pointer(1),
			Condition: &data.Condition{
				Equals: map[string][]string{
					"map_name": axisToAlliedVerticalMaps,
				},
			},
		},
		{
			Y: internal.Pointer(10),
			Condition: &data.Condition{
				Equals: map[string][]string{
					"map_name": alliedToAxisVerticalMaps,
				},
			},
		},
	}
	axisFences := []data.Fence{
		{
			X: &horizontalCaps[9],
			Condition: &data.Condition{
				Equals: map[string][]string{
					"map_name": axisToAlliedHorizontalMaps,
				},
			},
		},
		{
			X: &horizontalCaps[0],
			Condition: &data.Condition{
				Equals: map[string][]string{
					"map_name": alliedToAxisHorizontalMaps,
				},
			},
		},
		{
			Y: internal.Pointer(10),
			Condition: &data.Condition{
				Equals: map[string][]string{
					"map_name": axisToAlliedVerticalMaps,
				},
			},
		},
		{
			Y: internal.Pointer(1),
			Condition: &data.Condition{
				Equals: map[string][]string{
					"map_name": alliedToAxisVerticalMaps,
				},
			},
		},
	}

	// Allowlist deadzonefences: Horizontal A2 to J2 and A9 to J9 for all horizontal maps
	for _, cap := range horizontalCaps {
		alliedFences = append(alliedFences, data.Fence{
			X: &cap,
			Y: internal.Pointer(2),
			Condition: &data.Condition{
				Equals: map[string][]string{
					"map_name": append([]string{}, axisToAlliedHorizontalMaps..., alliedToAxisHorizontalMaps...),
				},
			},
		})
		alliedFences = append(alliedFences, data.Fence{
			X: &cap,
			Y: internal.Pointer(9),
			Condition: &data.Condition{
				Equals: map[string][]string{
					"map_name": append([]string{}, axisToAlliedHorizontalMaps..., alliedToAxisHorizontalMaps...),
				},
			},
		})
		axisFences = append(axisFences, data.Fence{
			X: &cap,
			Y: internal.Pointer(2),
			Condition: &data.Condition{
				Equals: map[string][]string{
					"map_name": append([]string{}, axisToAlliedHorizontalMaps..., alliedToAxisHorizontalMaps...),
				},
			},
		})
		axisFences = append(axisFences, data.Fence{
			X: &cap,
			Y: internal.Pointer(9),
			Condition: &data.Condition{
				Equals: map[string][]string{
					"map_name": append([]string{}, axisToAlliedHorizontalMaps..., alliedToAxisHorizontalMaps...),
				},
			},
		})
	}

	// Allowlist deadzonefences: Vertical B1 to B10 and I1 to I10 for all vertical maps
	for y := 1; y <= 10; y++ {
		alliedFences = append(alliedFences, data.Fence{
			X: &horizontalCaps[1], // B
			Y: internal.Pointer(y),
			Condition: &data.Condition{
				Equals: map[string][]string{
					"map_name": append([]string{}, axisToAlliedVerticalMaps..., alliedToAxisVerticalMaps...),
				},
			},
		})
		alliedFences = append(alliedFences, data.Fence{
			X: &horizontalCaps[8], // I
			Y: internal.Pointer(y),
			Condition: &data.Condition{
				Equals: map[string][]string{
					"map_name": append([]string{}, axisToAlliedVerticalMaps..., alliedToAxisVerticalMaps...),
				},
			},
		})
		axisFences = append(axisFences, data.Fence{
			X: &horizontalCaps[1], // B
			Y: internal.Pointer(y),
			Condition: &data.Condition{
				Equals: map[string][]string{
					"map_name": append([]string{}, axisToAlliedVerticalMaps..., alliedToAxisVerticalMaps...),
				},
			},
		})
		axisFences = append(axisFences, data.Fence{
			X: &horizontalCaps[8], // I
			Y: internal.Pointer(y),
			Condition: &data.Condition{
				Equals: map[string][]string{
					"map_name": append([]string{}, axisToAlliedVerticalMaps..., alliedToAxisVerticalMaps...),
				},
			},
		})
	}

	// fill the remaining caps as configured by the user.
	for c := range ac.EnforceCapFight.MaxCaps * 2 {
		alliedFences = append(alliedFences, data.Fence{
			X: &horizontalCaps[9-c],
			Condition: &data.Condition{
				Equals: map[string][]string{
					"map_name": axisToAlliedHorizontalMaps,
				},
			},
		})
		alliedFences = append(alliedFences, data.Fence{
			X: &horizontalCaps[c],
			Condition: &data.Condition{
				Equals: map[string][]string{
					"map_name": alliedToAxisHorizontalMaps,
				},
			},
		})

		axisFences = append(axisFences, data.Fence{
			X: &horizontalCaps[c],
			Condition: &data.Condition{
				Equals: map[string][]string{
					"map_name": axisToAlliedHorizontalMaps,
				},
			},
		})
		axisFences = append(axisFences, data.Fence{
			X: &horizontalCaps[9-c],
			Condition: &data.Condition{
				Equals: map[string][]string{
					"map_name": alliedToAxisHorizontalMaps,
				},
			},
		})

		alliedFences = append(alliedFences, data.Fence{
			Y: internal.Pointer(10 - c),
			Condition: &data.Condition{
				Equals: map[string][]string{
					"map_name": axisToAlliedVerticalMaps,
				},
			},
		})
		alliedFences = append(alliedFences, data.Fence{
			Y: internal.Pointer(c + 1),
			Condition: &data.Condition{
				Equals: map[string][]string{
					"map_name": alliedToAxisVerticalMaps,
				},
			},
		})
		axisFences = append(axisFences, data.Fence{
			Y: internal.Pointer(c + 1),
			Condition: &data.Condition{
				Equals: map[string][]string{
					"map_name": axisToAlliedVerticalMaps,
				},
			},
		})
		axisFences = append(axisFences, data.Fence{
			Y: internal.Pointer(10 - c),
			Condition: &data.Condition{
				Equals: map[string][]string{
					"map_name": alliedToAxisVerticalMaps,
				},
			},
		})
	}

	// player count condition is always the same, same as game mode, hence adding it once only.
	for _, fence := range alliedFences {
		fence.Condition.GreaterThan = map[string]int{
			"player_count": ac.EnforceCapFight.MinPlayers,
		}
		fence.Condition.LessThan = map[string]int{
			"player_count": ac.EnforceCapFight.MaxPlayers,
		}
		fence.Condition.Equals["game_mode"] = []string{"Warfare"}
	}
	for _, fence := range axisFences {
		fence.Condition.GreaterThan = map[string]int{
			"player_count": ac.EnforceCapFight.MinPlayers,
		}
		fence.Condition.LessThan = map[string]int{
			"player_count": ac.EnforceCapFight.MaxPlayers,
		}
		fence.Condition.Equals["game_mode"] = []string{"Warfare"}
	}

	if ac.Enabled == false || ac.DryRun == true {
		logger.Info("enforce-cap-fight-disabled")
	} else {
		port, err := strconv.Atoi(hllPort)
		if err != nil {
			logger.Error("parse-port", "error", err)
			return
		}
		pool, err := rconv2.NewConnectionPool(rconv2.ConnectionPoolOptions{
			Logger:             logger,
			Hostname:           hllHost,
			Port:               port,
			Password:           hllPassword,
			MaxIdleConnections: internal.Pointer(2),
			MaxOpenConnections: internal.Pointer(5),
		})
		if err != nil {
			logger.Error("create-connection-pool", "server", hllHost, "error", err)
			return
		}
		w := worker.NewWorker(logger, pool, data.Server{
			Host:               hllHost,
			Port:               port,
			Password:           hllPassword,
			PunishAfterSeconds: &punishAfterSeconds,
			AxisFence:          axisFences,
			AlliesFence:        alliedFences,
			Messages: &data.Messages{
				Warning: nil,
				Punish:  &ac.EnforceCapFight.ViolationMessage,
			},
		})
		go w.Run(ctx)
		logger.Info("started-worker")
	}
}
