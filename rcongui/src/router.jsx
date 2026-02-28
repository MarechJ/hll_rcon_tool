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

import SettingsPage from "./pages/settings/general-group"
import GeneralSettingsPage from "./pages/settings/general-group/general";
import { loader as generalSettingsLoader } from "./pages/settings/general-group/general/loader"
import AdminCamSettingsPage from "./pages/settings/general-group/admin-cam-notifications";
import { loader as adminCamSettingsLoader } from "./pages/settings/general-group/admin-cam-notifications/loader"
import ServerNameSettingsPage from "./pages/settings/general-group/server-name";
import { loader as serverNameSettingsLoader } from "./pages/settings/general-group/server-name/loader"
import CrconAppSettingsPage from "./pages/settings/general-group/crcon-app";
import GameSettingsPage from "./pages/settings/general-group/game";
import { loader as gameSettingsLoader } from "./pages/settings/general-group/game/loader"

import MapsManager from "./pages/settings/maps"
import { loader as mapsManagerLoader } from "./pages/settings/maps/loader"
import MapList from "./pages/settings/maps/list"
import MapRotation from "./pages/settings/maps/rotation"
import MapRotationBuilder from "./pages/settings/maps/rotation/builder"
import { loader as mapRotationBuilderLoader } from "./pages/settings/maps/rotation/builder/loader"
import MapRotationSettings from "./pages/settings/maps/rotation/settings"
import { loader as mapRotationSettingsLoader } from "./pages/settings/maps/rotation/settings/loader"
import Votemap from "./pages/settings/maps/votemap"
import VotemapStatus from "./pages/settings/maps/votemap/status"
import { loader as votemapStatusLoader } from "./pages/settings/maps/votemap/status/loader"
import VotemapBuilder from "./pages/settings/maps/votemap/builder"
import { loader as votemapBuilderLoader } from "./pages/settings/maps/votemap/builder/loader"
import VotemapSettings from "./pages/settings/maps/votemap/settings"
import { loader as votemapSettingsLoader } from "./pages/settings/maps/votemap/settings/loader"
import MapObjectives from "./pages/settings/maps/objectives";
import MapObjectivesError from "./pages/settings/maps/objectives/error";
import { loader as mapObjectivesLoader } from "./pages/settings/maps/objectives/loader"

import ConfigDetail from "./pages/settings/[configs]/detail"
import { loader as configLoader } from "./pages/settings/[configs]/detail"
import { action as configAction } from "./pages/settings/[configs]/detail"

import PlayerProfile from "./pages/records/players/[playerId]"
import PlayerProfileDetail from "./pages/records/players/[playerId]/[detail]"
import { loader as playerProfileLoader } from "./pages/records/players/[playerId]/router"
import { action as playerProfileAction } from "./pages/records/players/[playerId]/router"

import PlayerLogs from "./pages/records/players/[playerId]/[detail]/logs"
import { loader as playerLogsLoader } from "./pages/records/players/[playerId]/[detail]/logs"

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
import { loader as vipLoader } from "./pages/settings/vip"

import { AuthProvider } from "@/hooks/useAuth";
import { GlobalState } from "./stores/global-state";
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
                        children: [
                            {
                                path: '',
                                element: <PlayerProfileDetail />,
                                errorElement: <RouteError />,
                            },
                            {
                                path: ':detail',
                                element: <PlayerProfileDetail />,
                                errorElement: <RouteError />,
                            },
                            {
                                path: 'logs',
                                element: <PlayerLogs />,
                                errorElement: <RouteError />,
                                loader: playerLogsLoader,
                            }
                        ]
                    },
                    {
                        path: 'vips',
                        handle: { crumb: () => <Link to={'/records/vips'}>Vips</Link> },
                        loader: vipLoader,
                        element: <VipSettings />,
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
                element: <SettingsPage />,
                handle: { crumb: () => <span>Settings</span> },
                children: [
                    {
                        path: 'general',
                        handle: { crumb: () => <span>General</span> },
                        element: <GeneralSettingsPage />,
                        loader: generalSettingsLoader,
                        errorElement: <RouteError />,
                    },
                    {
                        path: 'admin-cam-notifications',
                        handle: { crumb: () => <span>Admin Cam Notifications</span> },
                        element: <AdminCamSettingsPage />,
                        loader: adminCamSettingsLoader,
                        errorElement: <RouteError />,
                    },
                    {
                        path: 'server-name',
                        handle: { crumb: () => <span>Server Name</span> },
                        element: <ServerNameSettingsPage />,
                        loader: serverNameSettingsLoader,
                        errorElement: <RouteError />,
                    },
                    {
                        path: 'game',
                        handle: { crumb: () => <span>Game</span> },
                        element: <GameSettingsPage />,
                        loader: gameSettingsLoader,
                        errorElement: <RouteError />,
                    },
                    {
                        path: 'crcon',
                        handle: { crumb: () => <span>CRCON APP</span> },
                        element: <CrconAppSettingsPage />,
                        errorElement: <RouteError />,
                    },
                ]
            },
            {
                path: 'settings/services',
                handle: { crumb: () => <span>Services</span> },
                element: <ServicesSettings />,
                loader: servicesLoader,
                action: servicesAction,
                errorElement: <RouteError />,
            },
            {
                path: 'settings/console-admins',
                handle: { crumb: () => <Link to={'/settings/console-admins'}>Console Admins</Link> },
                element: <ConsoleAdminSettings />,
                loader: consoleAdminSettingsLoader,
                action: consoleAdminSettingsAction,
                errorElement: <RouteError />,
            },
            {
                path: 'settings/profanity-filter',
                handle: { crumb: () => <span>Profanity Filter</span> },
                element: <ProfanityFilterSettings />,
                loader: profanityFilterLoader,
                action: profanityFilterAction,
                errorElement: <RouteError />,
            },
            {
                path: 'settings/welcome-message',
                handle: { crumb: () => <span>Welcome Message</span> },
                element: <WelcomeMessageSettings />,
                loader: welcomeMessageLoader,
                action: welcomeMessageAction,
                errorElement: <RouteError />,
            },
            {
                path: 'settings/broadcast-message',
                handle: { crumb: () => <span>Broadcast Message</span> },
                element: <BroadcastMessageSettings />,
                loader: broadcastMessageLoader,
                action: broadcastMessageAction,
                errorElement: <RouteError />,
            },
            {
                path: 'settings/autosettings',
                handle: { crumb: () => <span>Autosettings</span> },
                element: <AutoSettings />,
                loader: autosettingsLoader,
                action: autosettingsAction,
                errorElement: <RouteError />,
            },
            {
                path: 'settings/maps',
                element: <MapsManager />,
                loader: mapsManagerLoader,
                errorElement: <RouteError />,
                id: "maps",
                children: [
                    {
                        path: 'change',
                        element: <MapList />,
                        errorElement: <RouteError />,
                    },
                    {
                        path: 'rotation',
                        element: <MapRotation />,
                        errorElement: <RouteError />,
                        children: [
                            {
                                path: '',
                                index: true,
                                loader: mapRotationBuilderLoader,
                                element: <MapRotationBuilder />,
                            },
                            {
                                path: 'settings',
                                loader: mapRotationSettingsLoader,
                                element: <MapRotationSettings />,
                            }
                        ]
                    },
                    {
                        path: 'votemap',
                        element: <Votemap />,
                        errorElement: <RouteError />,
                        children: [
                            {
                                path: '',
                                index: true,
                                element: <VotemapStatus />,
                                loader: votemapStatusLoader,
                            },
                            {
                                path: 'whitelist',
                                element: <VotemapBuilder />,
                                loader: votemapBuilderLoader,
                            },{
                                path: 'settings',
                                element: <VotemapSettings />,
                                loader: votemapSettingsLoader,
                            }
                        ]
                    },
                    {
                        path: 'objectives',
                        element: <MapObjectives />,
                        loader: mapObjectivesLoader,
                        errorElement: <MapObjectivesError />
                    }
                ],
            },
            {
                path: 'settings/templates',
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
