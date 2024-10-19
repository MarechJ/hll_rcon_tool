import { createBrowserRouter, Link } from "react-router-dom";

import Root from "../pages/admin/root"
import { loader as rootLoader } from "../pages/admin/root"
import { action as rootAction } from "../pages/admin/root"

import ErrorPage from "../pages/admin/error";
import Dashboard from "../pages/admin/dashboard";

import LiveView from "../pages/admin/views/live";
import { loader as liveViewLoader } from "../pages/admin/views/live"

import TeamView from "../pages/admin/views/team";
import PlayerRecords from "../pages/admin/records/players"
import Blacklists from "../pages/admin/records/blacklists/manage"
import BlacklistRecords from "../pages/admin/records/blacklists"
import GameLogsRecords from "../pages/admin/records/game-logs"
import AuditLogsRecords from "../pages/admin/records/audit-logs"
import LiveGameStats from "../pages/admin/stats/live-game";
import LiveSessionStats from "../pages/admin/stats/live-sessions";
import GamesStats from "../pages/admin/stats/games";

import Login from "../pages/admin/login"
import { loader as loginLoader } from "../pages/admin/login"
import { action as loginAction } from "../pages/admin/login"

import Settings from "../pages/admin/settings"
import MapManager from "../pages/admin/settings/map-manager"
import MapChange from "../pages/admin/settings/map-manager/map-change"
import MapRotation from "../pages/admin/settings/map-manager/map-rotation"
import MapObjectives from "../pages/admin/settings/map-manager/objectives"
import MapVotemap from "../pages/admin/settings/map-manager/votemap"

import ConfigDetail from "../pages/admin/settings/[configs]/detail"
import { loader as configLoader } from "../pages/admin/settings/[configs]/detail"
import { action as configAction } from "../pages/admin/settings/[configs]/detail"
import { ErrorElement as SharedErrorElement } from "../pages/admin/settings/[configs]/detail"

import PlayerProfile from "../pages/admin/records/players/[playerId]"
import { loader as playerProfileLoader } from "../pages/admin/records/players/[playerId]"
import { action as playerProfileAction } from "../pages/admin/records/players/[playerId]"

import ServicesSettings from "../pages/admin/settings/services"
import { loader as servicesLoader } from "../pages/admin/settings/services"
import { action as servicesAction } from "../pages/admin/settings/services"

import TemplatesSettings from "../pages/admin/settings/templates"
import { loader as templatesLoader } from "../pages/admin/settings/templates/detail"
import { action as templatesAction } from "../pages/admin/settings/templates/detail"
import TemplatesDetail from "../pages/admin/settings/templates/detail"

import AutoSettings from "../pages/admin/settings/autosettings"
import { loader as autosettingsLoader } from "../pages/admin/settings/autosettings"
import { action as autosettingsAction } from "../pages/admin/settings/autosettings"

import WelcomeMessageSettings from "../pages/admin/settings/welcome-message"
import { loader as welcomeMessageLoader } from "../pages/admin/settings/welcome-message"
import { action as welcomeMessageAction } from "../pages/admin/settings/welcome-message"

import BroadcastMessageSettings from "../pages/admin/settings/broadcast-message"
import { loader as broadcastMessageLoader } from "../pages/admin/settings/broadcast-message"
import { action as broadcastMessageAction } from "../pages/admin/settings/broadcast-message"

import ProfanityFilterSettings from "../pages/admin/settings/profanity-filter"
import { loader as profanityFilterLoader } from "../pages/admin/settings/profanity-filter"
import { action as profanityFilterAction } from "../pages/admin/settings/profanity-filter"

import ConsoleAdminSettings from "../pages/admin/settings/console-admins"
import { loader as consoleAdminSettingsLoader } from "../pages/admin/settings/console-admins"
import { action as consoleaAdminSettingsAction } from "../pages/admin/settings/console-admins"

import VipSettings from "../pages/admin/settings/vip"
import { loader as vipSettingsLoader } from "../pages/admin/settings/vip"
import { action as vipSettingsAction } from "../pages/admin/settings/vip"

import { AuthProvider } from "@/hooks/useAuth";
import { GlobalState } from "@/hooks/useGlobalState";

const router = createBrowserRouter([
    {
        path: '/',
        element: (
            <AuthProvider>
                <GlobalState />
                <Root />
            </AuthProvider>
        ),
        errorElement: <ErrorPage />,
        action: rootAction,
        loader: rootLoader,
        children: [
            {
                path: '',
                index: true,
                element: <Dashboard />,
                errorElement: <SharedErrorElement />,
            },
            {
                path: 'views',
                errorElement: <SharedErrorElement />,
                handle: { crumb: () => <span>Views</span> },
                children: [
                    {
                        path: 'live',
                        handle: { crumb: () => <Link to={'/views/live'}>Live</Link> },
                        element: <LiveView />,
                        loader: liveViewLoader,
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
                errorElement: <SharedErrorElement />,
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
                errorElement: <SharedErrorElement />,
                handle: { crumb: () => <span>Settings</span> },
                children: [
                    {
                        path: '',
                        handle: { crumb: () => <span>General</span> },
                        element: <Settings />,
                    },
                    {
                        path: 'services',
                        handle: { crumb: () => <span>Services</span> },
                        element: <ServicesSettings />,
                        loader: servicesLoader,
                        action: servicesAction,
                    },
                    {
                        path: 'vip',
                        handle: { crumb: () => <Link to={'/settings/vip'}>Vip</Link> },
                        element: <VipSettings />,
                        loader: vipSettingsLoader,
                        action: vipSettingsAction,
                    },
                    {
                        path: 'console-admins',
                        handle: { crumb: () => <Link to={'/settings/console-admins'}>Console Admins</Link> },
                        element: <ConsoleAdminSettings />,
                        loader: consoleAdminSettingsLoader,
                        action: consoleaAdminSettingsAction,
                    },
                    {
                        path: 'profanity-filter',
                        handle: { crumb: () => <span>Profanity Filter</span> },
                        element: <ProfanityFilterSettings />,
                        loader: profanityFilterLoader,
                        action: profanityFilterAction,
                    },
                    {
                        path: 'welcome-message',
                        handle: { crumb: () => <span>Welcome Message</span> },
                        element: <WelcomeMessageSettings />,
                        loader: welcomeMessageLoader,
                        action: welcomeMessageAction,
                    },
                    {
                        path: 'broadcast-message',
                        handle: { crumb: () => <span>Broadcast Message</span> },
                        element: <BroadcastMessageSettings />,
                        loader: broadcastMessageLoader,
                        action: broadcastMessageAction,
                    },
                    {
                        path: 'autosettings',
                        handle: { crumb: () => <span>Autosettings</span> },
                        element: <AutoSettings />,
                        loader: autosettingsLoader,
                        action: autosettingsAction,
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
                        path: 'templates',
                        handle: { crumb: () => <span>Templates</span> },
                        element: <TemplatesSettings />,
                        children: [
                            {
                                path: ':category',
                                handle: { crumb: () => <span>Detail</span> },
                                loader: templatesLoader,
                                action: templatesAction,
                                errorElement: <SharedErrorElement />,
                                element: <TemplatesDetail />,
                            },
                        ]
                    },
                ]
            },
            {
                path: '/settings/:category/:type',
                element: <ConfigDetail />,
                errorElement: <SharedErrorElement />,
                loader: configLoader,
                action: configAction,
            },
            {
                path: 'stats',
                errorElement: <SharedErrorElement />,
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
        path: '/login',
        element: <Login />,
        errorElement: <ErrorPage />,
        action: loginAction,
        loader: loginLoader,
    },
]); 

export default router;
