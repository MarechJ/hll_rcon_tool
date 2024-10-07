import HomeIcon from '@mui/icons-material/Home';
import SportsEsportsIcon from '@mui/icons-material/SportsEsports';
import BoltIcon from '@mui/icons-material/Bolt';
import GroupsIcon from '@mui/icons-material/Groups';
import PeopleIcon from '@mui/icons-material/PeopleAlt';
import TextSnippetIcon from '@mui/icons-material/TextSnippet';
import SimCardAlertIcon from '@mui/icons-material/SimCardAlert';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import WebhookIcon from '@mui/icons-material/Webhook';
import SettingsIcon from '@mui/icons-material/Settings';
import DnsIcon from '@mui/icons-material/Dns';
import PersonOffIcon from '@mui/icons-material/PersonOff';
import NoTransferIcon from '@mui/icons-material/NoTransfer';
import SpaIcon from '@mui/icons-material/Spa';
import RemoveRedEyeIcon from '@mui/icons-material/RemoveRedEye';
import RestaurantIcon from '@mui/icons-material/Restaurant';
import ChatIcon from '@mui/icons-material/Chat';
import VideocamIcon from '@mui/icons-material/Videocam';
import PrivacyTipIcon from '@mui/icons-material/PrivacyTip';
import RateReviewIcon from '@mui/icons-material/RateReview';
import TimerOffIcon from '@mui/icons-material/TimerOff';
import DriveFileRenameOutlineIcon from '@mui/icons-material/DriveFileRenameOutline';
import SportsMartialArtsIcon from '@mui/icons-material/SportsMartialArts';
import CableIcon from '@mui/icons-material/Cable';
import ScoreboardIcon from '@mui/icons-material/Scoreboard';
import GavelIcon from '@mui/icons-material/Gavel';
import BrowseGalleryIcon from '@mui/icons-material/BrowseGallery';
import HourglassBottomIcon from '@mui/icons-material/HourglassBottom';
import MiscellaneousServicesIcon from '@mui/icons-material/MiscellaneousServices';
import NoStrollerIcon from '@mui/icons-material/NoStroller';
import MapIcon from '@mui/icons-material/Map';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import FolderIcon from '@mui/icons-material/Folder';
import ViewCarouselIcon from '@mui/icons-material/ViewCarousel';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import StreamIcon from '@mui/icons-material/Stream';
import ThreeSixtyIcon from '@mui/icons-material/ThreeSixty';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import HowToVoteIcon from '@mui/icons-material/HowToVote';
import AdsClickIcon from '@mui/icons-material/AdsClick';
import LibraryBooksIcon from '@mui/icons-material/LibraryBooks';
import ElectricalServicesIcon from '@mui/icons-material/ElectricalServices';
import SettingsSuggestIcon from '@mui/icons-material/SettingsSuggest';
import GradeIcon from '@mui/icons-material/Grade';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';

export const navMenus = [
  {
    links: [
      {
        name: "Home",
        to: "/",
        icon: <HomeIcon />,
      },
    ]
  },
  {
    name: "Views",
    icon: <ViewCarouselIcon />,
    links: [
      {
        name: "Live",
        to: "views/live",
        icon: <BoltIcon />,
      },
      {
        name: "Team",
        to: "views/team",
        icon: <GroupsIcon />,
      },
    ],
  },
  {
    name: "Maps",
    icon: <MapIcon />,
    links: [
      {
        name: 'Change',
        to: '/settings/maps/change',
        icon: <RestartAltIcon />,
      },
      {
        name: 'Rotation',
        to: '/settings/maps/rotation',
        icon: <ThreeSixtyIcon />,
      },
      {
        name: 'Objectives',
        to: '/settings/maps/objectives',
        icon: <AdsClickIcon />,
      },
      {
        name: 'Votemap',
        to: '/settings/maps/votemap',
        icon: <HowToVoteIcon />,
      },
    ]
  },
  {
    name: "Records",
    icon: <FolderIcon />,
    links: [
      {
        name: "Players",
        to: "records/players",
        icon: <PeopleIcon />,
      },
      {
        name: "Blacklist",
        to: "records/blacklists",
        icon: <AccountBalanceIcon />,
      },
      {
        name: "Game Logs",
        to: "records/game-logs",
        icon: <TextSnippetIcon />,
      },
      {
        name: "Audit Logs",
        to: "records/audit-logs",
        icon: <TextSnippetIcon />,
      },
      {
        name: "Admins",
        to: "records/admin",
        icon: <AdminPanelSettingsIcon />,
      },
      {
        name: "Vips",
        to: "records/vip",
        icon: <GradeIcon />,
      },
    ],
  },
  {
    name: "Settings",
    icon: <SettingsIcon />,
    links: [
      {
        name: "General",
        to: "/settings",
        icon: <SettingsIcon />,
      },
      {
        name: "Services",
        to: "/settings/services",
        icon: <ElectricalServicesIcon />,
      },
      {
        name: "Messages",
        to: "/settings/messages/message",
        icon: <LibraryBooksIcon />,
      },
      {
        name: "Autosettings",
        to: "/settings/autosettings",
        icon: <SettingsSuggestIcon />,
      },
    ],
  },
  {
    name: 'Webhooks',
    icon: <WebhookIcon />,
    links: [
      {
        name: "Audit",
        to: "/settings/webhooks/audit",
        icon: <SimCardAlertIcon />,
      },
      {
        name: "Admin Ping",
        to: "/settings/webhooks/admin-ping",
        icon: <PrivacyTipIcon />,
      },
      {
        name: "Watchlist",
        to: "/settings/webhooks/watchlist",
        icon: <RemoveRedEyeIcon />,
      },
      {
        name: "Camera",
        to: "/settings/webhooks/camera",
        icon: <VideocamIcon />,
      },
      {
        name: "Chat",
        to: "/settings/webhooks/chat",
        icon: <ChatIcon />,
      },
      {
        name: "Kill/TK",
        to: "/settings/webhooks/kills",
        icon: <RestaurantIcon />,
      },
      {
        name: "Log Line",
        to: "/settings/webhooks/log-line",
        icon: <TextSnippetIcon />,
      },
    ]
  },
  {
    name: "Automods",
    icon: <SmartToyIcon />,
    links: [
      {
        name: "Level",
        to: "/settings/automods/level",
        icon: <NoStrollerIcon />,
      },
      {
        name: "No Leader",
        to: "/settings/automods/no-leader",
        icon: <PersonOffIcon />,
      },
      {
        name: "Seeding",
        to: "/settings/automods/seeding",
        icon: <SpaIcon />,
      },
      {
        name: "No Solo Tank",
        to: "/settings/automods/no-solo-tank",
        icon: <NoTransferIcon />,
      },
      {
        name: "VAC/Game Bans",
        to: "/settings/others/vac-bans",
        icon: <AccountBalanceIcon />,
      },
      {
        name: "TK Ban On Connect",
        to: "/settings/others/tk-bans",
        icon: <GavelIcon />,
      },
      {
        name: "Name Kicks",
        to: "/settings/others/name-kicks",
        icon: <SportsMartialArtsIcon />,
      },
    ]
  },
  {
    name: 'Others',
    icon: <MiscellaneousServicesIcon />,
    links: [
      {
        name: "RCON Game Server Connection",
        to: "/settings/others/game-server",
        icon: <CableIcon />,
      },
      {
        name: "CRCON Settings",
        to: "/settings/others/crcon",
        icon: <DnsIcon />,
      },
      {
        name: "Chat Commands",
        to: "/settings/others/chat-commands",
        icon: <RateReviewIcon />,
      },
      {
        name: "RCon Chat Commands",
        to: "/settings/rcon-chat-commands",
      },
      {
        name: "Scorebot",
        to: "/settings/others/scorebot",
        icon: <ScoreboardIcon />,
      },
      {
        name: "Steam API",
        to: "/settings/others/steam",
        icon: <RemoveRedEyeIcon />,
      },
      {
        name: "Expired VIP",
        to: "/settings/others/expired-vip",
        icon: <TimerOffIcon />,
      },
      {
        name: "GTX Server Name Change",
        to: "/settings/others/gtx-server",
        icon: <DriveFileRenameOutlineIcon />,
      },
      {
        name: "Log Stream",
        to: "/settings/others/log-stream",
        icon: <StreamIcon />,
      },
      {
        name: "Seed VIP",
        to: "/settings/seed-vip",
      },
    ],
  },
  {
    name: "Stats",
    icon: <AnalyticsIcon />,
    links: [
      {
        name: "Live Sessions",
        to: "stats/live-sessions",
        icon: <BrowseGalleryIcon />,
      },
      {
        name: "Live Game",
        to: "stats/live-game",
        icon: <SportsEsportsIcon />,
      },
      {
        name: "Games",
        to: "stats/games",
        icon: <HourglassBottomIcon />,
      },
    ],
  },
];
