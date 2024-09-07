import { createBrowserRouter, Link } from "react-router-dom";

import Root from "../pages/root"
import { loader as rootLoader } from "../pages/root"
import { action as rootAction } from "../pages/root"

import ErrorPage from "../pages/error";
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

import Login from "../pages/login"
import { loader as loginLoader } from "../pages/login"
import { action as loginAction } from "../pages/login"

import Settings from "../pages/settings"
import MapManager from "../pages/settings/map-manager"
import MapChange from "../pages/settings/map-manager/map-change"
import MapRotation from "../pages/settings/map-manager/map-rotation"
import MapObjectives from "../pages/settings/map-manager/objectives"
import MapVotemap from "../pages/settings/map-manager/votemap"

import ConfigDetail from "../pages/settings/[configs]/detail"
import { loader as configLoader } from "../pages/settings/[configs]/detail"
import { action as configAction } from "../pages/settings/[configs]/detail"
import { ErrorBoundary as ConfigErrorBoundary } from "../pages/settings/[configs]/detail"

import PlayerProfile from "../pages/records/players/[playerId]"
import { loader as playerProfileLoader } from "../pages/records/players/[playerId]"
import { action as playerProfileAction } from "../pages/records/players/[playerId]"

const router = createBrowserRouter([
    {
        path: '/',
        element: <Root />,
        errorElement: <ErrorPage />,
        action: rootAction,
        loader: rootLoader,
        children: [
            {
                path: '',
                element: <Dashboard />,
            },
            {
                path: 'views',
                handle: { crumb: () => <span>Views</span> },
                children: [
                    {
                        path: 'live',
                        handle: { crumb: () => <Link to={'/views/live'}>Live</Link> },
                        element: <LiveView />
                    },
                    {
                        path: 'team',
                        handle: { crumb: () => <Link to={'/views/team'}>Team</Link> },
                        element: <TeamView />
                    }
                ]
            },
            {
                path: "records",
                handle: { crumb: () => <span>Records</span> },
                children: [
                    {
                        path: 'players',
                        handle: { crumb: () => <Link to={'/records/players'}>Players</Link> },
                        element: <PlayerRecords />,
                    },
                    {
                        path: 'players/:playerId',
                        element: <PlayerProfile />,
                        loader: playerProfileLoader,
                        action: playerProfileAction,
                        handle: { crumb: (data) => [<Link to={'/records/players'}>Players</Link>, <Link to={'/records/players/' + data?.profile?.player_id}>{data?.profile?.names[0]?.name ?? ''}</Link>] },
                    },
                    {
                        path: 'blacklists',
                        handle: { crumb: () => <Link to={'/records/blacklists'}>Blacklists</Link> },
                        element: <BlacklistRecords />,
                    },
                    {
                        path: 'blacklists/manage',
                        handle: { crumb: () => [<Link to={'/records/blacklists'}>Blacklists</Link>, <span>Manage</span>] },
                        element: <Blacklists />,
                    },
                    {
                        path: 'game-logs',
                        handle: { crumb: () => <Link to={'/records/game-log'}>Game Logs</Link> },
                        element: <GameLogsRecords />,
                    },
                    {
                        path: 'audit-logs',
                        handle: { crumb: () => <Link to={'/records/audit-log'}>Audit Logs</Link> },
                        element: <AuditLogsRecords />,
                    },
                ],
            },
            {
                path: 'settings',
                handle: { crumb: () => <span>Settings</span> },
                children: [
                    {
                        path: '',
                        handle: { crumb: () => <Link to={'/settings'}>General</Link> },
                        element: <Settings />,
                    },
                    {
                        path: 'maps',
                        handle: { crumb: () => <span>Maps</span> },
                        element: <MapManager />,
                        children: [
                            {
                                path: 'change',
                                handle: { crumb: () => <Link to={'/settings/maps/change'}>Change</Link> },
                                element: <MapChange />,
                            },
                            {
                                path: 'rotation',
                                handle: { crumb: () => <Link to={'/settings/maps/rotation'}>Rotation</Link> },
                                element: <MapRotation />,
                            },
                            {
                                path: 'objectives',
                                handle: { crumb: () => <Link to={'/settings/maps/objectives'}>Objectives</Link> },
                                element: <MapObjectives />,
                            },
                            {
                                path: 'votemap',
                                handle: { crumb: () => <Link to={'/settings/maps/votemap'}>Votemap</Link> },
                                element: <MapVotemap />,
                            }
                        ]
                    },
                    {
                        path: ':category/:type',
                        element: <ConfigDetail />,
                        errorElement: <h1>CONFIG NOT FOUND</h1>,
                        loader: configLoader,
                        action: configAction,
                        ErrorBoundary: ConfigErrorBoundary,
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
    {
        path: 'login',
        element: <Login />,
        errorElement: <ErrorPage />,
        action: loginAction,
        loader: loginLoader,
    },
]);

export default router;
