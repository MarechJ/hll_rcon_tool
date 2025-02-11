import { createBrowserRouter, Link } from "react-router-dom";

import Root from "./pages/root"
import { loader as rootLoader } from "./pages/root"
import { action as rootAction } from "./pages/root"

import Dashboard from "./pages/dashboard";

import LiveView from "./pages/views/live";
import { loader as liveViewLoader } from "./pages/views/live"

import TeamView from "./pages/views/team";

import PlayerRecords from "./pages/records/players"
import { loader as playerRecordsLoader } from "./pages/records/players"

import Blacklists from "./pages/records/blacklists/manage"
import BlacklistRecords from "./pages/records/blacklists"

import GameLogsRecords from "./pages/records/game-logs"
import { loader as gameLogsLoader } from "./pages/records/game-logs"

import AuditLogsRecords from "./pages/records/audit-logs"
import { loader as auditLogsLoader } from "./pages/records/audit-logs"

import LiveSessionStats from "./pages/stats/live-sessions";
import GamesLayout from "./pages/stats/games/layout";

import LiveGamePage from "./pages/stats/live-game";
import { loader as liveGameLoader } from "./pages/stats/live-game";

import GamesPage from "./pages/stats/games";
import { loader as gamesLoader } from "./pages/stats/games";

import GameDetailsPage from "./pages/stats/games/[gameId]";

import Login from "./pages/login"
import { loader as loginLoader } from "./pages/login"
import { action as loginAction } from "./pages/login"

import SettingsPage from "./pages/settings"
import { loader as settingsLoader } from "./pages/settings"
import { action as settingsAction } from "./pages/settings"

import MapManager from "./pages/settings/map-manager"
import MapChange from "./pages/settings/map-manager/map-change"
import MapRotation from "./pages/settings/map-manager/map-rotation"
import MapObjectives from "./pages/settings/map-manager/objectives"
import MapVotemap from "./pages/settings/map-manager/votemap"

import ConfigDetail from "./pages/settings/[configs]/detail"
import { loader as configLoader } from "./pages/settings/[configs]/detail"
import { action as configAction } from "./pages/settings/[configs]/detail"

import PlayerProfile from "./pages/records/players/[playerId]"
import { loader as playerProfileLoader } from "./pages/records/players/[playerId]"
import { action as playerProfileAction } from "./pages/records/players/[playerId]"

import ServicesSettings from "./pages/settings/services"
import { loader as servicesLoader } from "./pages/settings/services"
import { action as servicesAction } from "./pages/settings/services"

import TemplatesSettings from "./pages/settings/templates"
import { loader as templatesLoader } from "./pages/settings/templates/detail"
import { action as templatesAction } from "./pages/settings/templates/detail"
import TemplatesDetail from "./pages/settings/templates/detail"

import AutoSettings from "./pages/settings/autosettings"
import { loader as autosettingsLoader } from "./pages/settings/autosettings"
import { action as autosettingsAction } from "./pages/settings/autosettings"

import WelcomeMessageSettings from "./pages/settings/welcome-message"
import { loader as welcomeMessageLoader } from "./pages/settings/welcome-message"
import { action as welcomeMessageAction } from "./pages/settings/welcome-message"

import BroadcastMessageSettings from "./pages/settings/broadcast-message"
import { loader as broadcastMessageLoader } from "./pages/settings/broadcast-message"
import { action as broadcastMessageAction } from "./pages/settings/broadcast-message"

import ProfanityFilterSettings from "./pages/settings/profanity-filter"
import { loader as profanityFilterLoader } from "./pages/settings/profanity-filter"
import { action as profanityFilterAction } from "./pages/settings/profanity-filter"

import ConsoleAdminSettings from "./pages/settings/console-admins"
import { loader as consoleAdminSettingsLoader } from "./pages/settings/console-admins"
import { action as consoleAdminSettingsAction } from "./pages/settings/console-admins"

import VipSettings from "./pages/settings/vip"
import { loader as vipSettingsLoader } from "./pages/settings/vip"
import { action as vipSettingsAction } from "./pages/settings/vip"

import { AuthProvider } from "@/hooks/useAuth";
import { GlobalState } from "@/hooks/useGlobalState";
import RouteError from "@/components/shared/RouteError";

const router = createBrowserRouter([
    {
        path: '/',
        element: (
            <AuthProvider>
                <GlobalState />
                <Root />
            </AuthProvider>
        ),
        errorElement: <RouteError />,
        action: rootAction,
        loader: rootLoader,
        children: [
            {
                path: '',
                index: true,
                element: <Dashboard />,
                errorElement: <RouteError />,
            },
            {
                path: 'views',
                errorElement: <RouteError />,
                handle: { crumb: () => <span>Views</span> },
                children: [
                    {
                        path: 'live',
                        handle: { crumb: () => <Link to={'/views/live'}>Live</Link> },
                        element: <LiveView />,
                        loader: liveViewLoader,
                        errorElement: <RouteError />,
                    },
                    {
                        path: 'team',
                        handle: { crumb: () => <Link to={'/views/team'}>Team</Link> },
                        element: <TeamView />,
                        errorElement: <RouteError />,
                    }
                ]
            },
            {
                path: "records",
                errorElement: <RouteError />,
                handle: { crumb: () => <span>Records</span> },
                children: [
                    {
                        path: 'players',
                        handle: { crumb: () => <Link to={'/records/players'}>Players</Link> },
                        element: <PlayerRecords />,
                        errorElement: <RouteError />,
                        loader: playerRecordsLoader,
                    },
                    {
                        path: 'players/:playerId',
                        element: <PlayerProfile />,
                        loader: playerProfileLoader,
                        action: playerProfileAction,
                        handle: { crumb: (data) => [<Link to={'/records/players'}>Players</Link>, <Link to={'/records/players/' + data?.profile?.player_id}>{data?.profile?.names[0]?.name ?? ''}</Link>] },
                        errorElement: <RouteError />,
                    },
                    {
                        path: 'blacklists',
                        handle: { crumb: () => <Link to={'/records/blacklists'}>Blacklists</Link> },
                        element: <BlacklistRecords />,
                        errorElement: <RouteError />,
                    },
                    {
                        path: 'blacklists/manage',
                        handle: { crumb: () => [<Link to={'/records/blacklists'}>Blacklists</Link>, <span>Manage</span>] },
                        element: <Blacklists />,
                        errorElement: <RouteError />,
                    },
                    {
                        path: 'game-logs',
                        handle: { crumb: () => <Link to={'/records/game-log'}>Game Logs</Link> },
                        element: <GameLogsRecords />,
                        errorElement: <RouteError />,
                        loader: gameLogsLoader,
                    },
                    {
                        path: 'audit-logs',
                        handle: { crumb: () => <Link to={'/records/audit-log'}>Audit Logs</Link> },
                        element: <AuditLogsRecords />,
                        errorElement: <RouteError />,   
                        loader: auditLogsLoader,
                    },
                ],
            },
            {
                path: 'settings',
                errorElement: <RouteError />,
                handle: { crumb: () => <span>Settings</span> },
                children: [
                    {
                        path: '',
                        handle: { crumb: () => <span>General</span> },
                        element: <SettingsPage />,
                        loader: settingsLoader,
                        action: settingsAction,
                        index: true,
                        errorElement: <RouteError />,
                    },
                    {
                        path: 'services',
                        handle: { crumb: () => <span>Services</span> },
                        element: <ServicesSettings />,
                        loader: servicesLoader,
                        action: servicesAction,
                        errorElement: <RouteError />,
                    },
                    {
                        path: 'vip',
                        handle: { crumb: () => <Link to={'/settings/vip'}>Vip</Link> },
                        element: <VipSettings />,
                        loader: vipSettingsLoader,
                        action: vipSettingsAction,
                        errorElement: <RouteError />,
                    },
                    {
                        path: 'console-admins',
                        handle: { crumb: () => <Link to={'/settings/console-admins'}>Console Admins</Link> },
                        element: <ConsoleAdminSettings />,
                        loader: consoleAdminSettingsLoader,
                        action: consoleAdminSettingsAction,
                        errorElement: <RouteError />,
                    },
                    {
                        path: 'profanity-filter',
                        handle: { crumb: () => <span>Profanity Filter</span> },
                        element: <ProfanityFilterSettings />,
                        loader: profanityFilterLoader,
                        action: profanityFilterAction,
                        errorElement: <RouteError />,
                    },
                    {
                        path: 'welcome-message',
                        handle: { crumb: () => <span>Welcome Message</span> },
                        element: <WelcomeMessageSettings />,
                        loader: welcomeMessageLoader,
                        action: welcomeMessageAction,
                        errorElement: <RouteError />,
                    },
                    {
                        path: 'broadcast-message',
                        handle: { crumb: () => <span>Broadcast Message</span> },
                        element: <BroadcastMessageSettings />,
                        loader: broadcastMessageLoader,
                        action: broadcastMessageAction,
                        errorElement: <RouteError />,
                    },
                    {
                        path: 'autosettings',
                        handle: { crumb: () => <span>Autosettings</span> },
                        element: <AutoSettings />,
                        loader: autosettingsLoader,
                        action: autosettingsAction,
                        errorElement: <RouteError />,
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
                                errorElement: <RouteError />,
                            },
                            {
                                path: 'rotation',
                                handle: { crumb: () => <Link to={'/settings/maps/rotation'}>Rotation</Link> },
                                element: <MapRotation />,
                                errorElement: <RouteError />,
                            },
                            {
                                path: 'objectives',
                                handle: { crumb: () => <Link to={'/settings/maps/objectives'}>Objectives</Link> },
                                element: <MapObjectives />,
                                errorElement: <RouteError />,
                            },
                            {
                                path: 'votemap',
                                handle: { crumb: () => <Link to={'/settings/maps/votemap'}>Votemap</Link> },
                                element: <MapVotemap />,
                                errorElement: <RouteError />,
                            }
                        ]
                    },
                    {
                        path: 'templates',
                        handle: { crumb: () => <span>Templates</span> },
                        element: <TemplatesSettings />,
                        children: [
                            {
                                path: ':category',
                                handle: { crumb: () => <span>Detail</span> },
                                loader: templatesLoader,
                                action: templatesAction,
                                errorElement: <RouteError />,
                                element: <TemplatesDetail />,
                            },
                        ]
                    },
                ]
            },
            {
                path: '/settings/:category/:type',
                element: <ConfigDetail />,
                errorElement: <RouteError />,
                loader: configLoader,
                action: configAction,
            },
            {
                path: 'stats',
                errorElement: <RouteError />,
                handle: { crumb: () => <span>Stats</span> },
                children: [
                    {
                        path: 'live-game',
                        handle: { crumb: () => <Link to={'/stats/live-game'}>Live Game</Link> },
                        element: <LiveGamePage />,
                        loader: liveGameLoader,
                        errorElement: <RouteError />,
                    },
                    {
                        path: 'live-sessions',
                        handle: { crumb: () => <Link to={'/stats/live-sessions'}>Live Sessions</Link> },
                        element: <LiveSessionStats />,
                        errorElement: <RouteError />,
                    },
                    {
                        path: 'games',
                        handle: { crumb: () => <Link to={'/stats/games'}>Games</Link> },
                        element: <GamesLayout />,
                        children: [
                            {
                                path: '',
                                index: true,
                                loader: gamesLoader,
                                element: <GamesPage />,
                                errorElement: <RouteError />,
                            },
                            {
                                path: ':gameId',
                                handle: { crumb: (data) => <span>{data?.gameId}</span> },
                                element: <GameDetailsPage />,
                                errorElement: <RouteError />,
                            }
                        ]
                    }
                ]
            }
        ]
    },
    {
        path: '/login',
        element: <Login />,
        errorElement: <RouteError />,
        action: loginAction,
        loader: loginLoader,
    },
]); 

export default router;
