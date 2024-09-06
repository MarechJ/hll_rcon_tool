import { createBrowserRouter, Navigate } from "react-router-dom";
import Root from "../pages/root"
import Dashboard from "../pages/dashboard";
import LiveView from "../pages/views/live";
import TeamView from "../pages/views/team";
import PlayerRecords from "../pages/records/players"
import Blacklists from "../pages/records/blacklists/manage"
import BlacklistRecords from "../pages/records/blacklists"
import GameLogsRecords from "../pages/records/game-logs"
import AuditLogsRecords from "../pages/records/audit-logs"
import LiveGameStats from "../pages/stats/live-game";
import LiveSessionStats from "../pages/stats/live-sessions";
import GamesStats from "../pages/stats/games";
import Settings from "../pages/settings"
import MapManager from "../pages/settings/map-manager"
import MapChange from "../pages/settings/map-manager/map-change"
import MapRotation from "../pages/settings/map-manager/map-rotation"
import MapObjectives from "../pages/settings/map-manager/objectives"
import MapVotemap from "../pages/settings/map-manager/votemap"
import ConfigDetail from "../pages/settings/[configs]/detail"
import PlayerProfile from "../pages/records/players/[playerId]"
import { loader as configLoader } from "../pages/settings/[configs]/detail"
import { loader as playerProfileLoader } from "../pages/records/players/[playerId]"
import { action as playerProfileAction } from "../pages/records/players/[playerId]"

const router = createBrowserRouter([
    {
        path: '/',
        element: <Root />,
        children: [
            {
                path: '',
                element: <Dashboard />,
            },
            {
                path: 'views',
                children: [
                    {
                        path: 'live',
                        element: <LiveView />
                    },
                    {
                        path: 'team',
                        element: <TeamView />
                    }
                ]
            },
            {
                path: "records",
                children: [
                    {
                        path: 'players',
                        element: <PlayerRecords />,
                    },
                    {
                        path: 'players/:playerId',
                        element: <PlayerProfile />,
                        loader: playerProfileLoader,
                        action: playerProfileAction,
                    },
                    {
                        path: 'blacklists',
                        element: <BlacklistRecords />,
                    },
                    {
                        path: 'blacklists/manage',
                        element: <Blacklists />,
                    },
                    {
                        path: 'game-logs',
                        element: <GameLogsRecords />
                    },
                    {
                        path: 'audit-logs',
                        element: <AuditLogsRecords />
                    },
                ],
            },
            {
                path: 'settings',
                children: [
                    {
                        path: '',
                        element: <Settings />
                    },
                    {
                        path: 'maps',
                        element: <MapManager />,
                        children: [
                            {
                                path: 'change',
                                element: <MapChange />,
                            },
                            {
                                path: 'rotation',
                                element: <MapRotation />,
                            },
                            {
                                path: 'objectives',
                                element: <MapObjectives />,
                            },
                            {
                                path: 'votemap',
                                element: <MapVotemap />,
                            }
                        ]
                    },
                    {
                        path: ':category/:type',
                        element: <ConfigDetail />,
                        errorElement: <h1>CONFIG NOT FOUND</h1>,
                        loader: configLoader,
                    },
                ]
            },
            {
                path: 'stats',
                children: [
                    {
                        path: 'games',
                        element: <GamesStats />
                    },
                    {
                        path: 'live-game',
                        element: <LiveGameStats />
                    },
                    {
                        path: 'live-sessions',
                        element: <LiveSessionStats />
                    },
                ]
            }
        ]
    },
]);

export default router;
