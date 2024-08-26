import datetime
import enum
from dataclasses import dataclass
from typing import List, Literal, Optional

# # TODO: On Python 3.11.* specifically, Pydantic requires we use typing_extensions.TypedDict
# over typing.TypedDict. Once we bump our Python image we can replace this.
from typing_extensions import TypedDict

from rcon.maps import Layer, LayerType


# Have to inherit from str to allow for JSON serialization w/ pydantic
class RconInvalidNameActionType(str, enum.Enum):
    warn = "WARN"
    kick = "KICK"
    ban = "BAN"


class WindowsStoreIdActionType(str, enum.Enum):
    kick = "KICK"
    temp_ban = "TEMP BAN"
    perma_ban = "PERMA BAN"


# Have to inherit from str to allow for JSON serialization w/ pydantic
class StatTypes(str, enum.Enum):
    top_killers = "TOP_KILLERS"
    top_ratio = "TOP_RATIO"
    top_performance = "TOP_PERFORMANCE"
    try_harders = "TRY_HARDERS"
    top_stamina = "TOP_STAMINA"
    top_kill_streak = "TOP_KILL_STREAK"
    most_patient = "MOST_PATIENT"
    i_never_give_up = "I_NEVER_GIVE_UP"
    im_clumsy = "IM_CLUMSY"
    i_need_glasses = "I_NEED_GLASSES"
    i_love_voting = "I_LOVE_VOTING"
    what_is_a_break = "WHAT_IS_A_BREAK"
    survivors = "SURVIVORS"
    u_r_still_a_man = "U_R_STILL_A_MAN"


class MessageVariable(enum.Enum):
    """Globally available message variables"""

    vip_status = "vip_status"
    vip_expiration = "vip_expiration"
    server_name = "server_name"
    server_short_name = "server_short_name"
    discord_invite_url = "discord_invite_url"
    admin_ping_trigger_words = "admin_ping_trigger_words"

    num_online_mods = "num_online_mods"
    num_ingame_mods = "num_ingame_mods"
    next_map = "next_map"
    map_rotation = "map_rotation"

    # TODO: vote map stuff

    # game stats
    top_kills_player_name = "top_kills_player_name"
    top_kills_player_score = "top_kills_player_score"
    top_kill_streak_player_name = "top_kill_streak_player_name"
    top_kill_streak_player_score = "top_kill_streak_player_score"

    # TODO: remaining stats
    # top_kill_death_ratio_player_name = ""
    # top_kill_death_ratio_score = ""
    # top_kills_per_min_player_name = ""
    # top_kills_per_min_player_score = ""

    # worst_deaths_player_name = ""
    # worst_deaths_player_score = ""
    # worst_death_streak_player_name = ""
    # worst_death_streak_player_score = ""
    # worst kdr
    # worst_deaths_per_min_player_name = ""
    # worst_deaths_per_min_player_score = ""

    # top_combat_eff_player_name = "best_attack_player_name"
    # top_combat_eff_player_score = "best_attack_player_score"
    # top_attack_player_name = "best_attack_player_name"
    # top_attack_player_score = "best_attack_player_score"
    # top_defense_player_name = "best_defense_player_name"
    # top_defense_player_score = "best_defense_player_score"
    # top_support_player_name = "best_support_player_name"
    # top_support_player_score = "best_support_player_score"


class MessageVariableContext(enum.Enum):
    """Available message variables if context passed"""

    player_name = "player_name"
    player_id = "player_id"

    # MostRecentEvents
    last_victim_player_id = "last_victim_player_id"
    last_victim_name = "last_victim_name"
    last_nemesis_player_id = "last_nemesis_player_id"
    last_nemesis_name = "last_nemesis_name"
    last_victim_weapon = "last_victim_weapon"
    last_nemesis_weapon = "last_nemesis_weapon"
    last_tk_victim_player_id = "last_tk_victim_player_id"
    last_tk_victim_name = "last_tk_victim_name"
    last_tk_victim_weapon = "last_tk_victim_weapon"
    last_tk_nemesis_player_id = "last_tk_nemesis_player_id"
    last_tk_nemesis_name = "last_tk_nemesis_name"
    last_tk_nemesis_weapon = "last_tk_nemesis_weapon"

    # TODO: automod stuff, etc.


@dataclass
class MostRecentEvents:
    player_name: str | None = None
    last_victim_name: str | None = None
    last_victim_player_id: str | None = None
    last_nemesis_name: str | None = None
    last_nemesis_player_id: str | None = None
    last_victim_weapon: str | None = None
    last_nemesis_weapon: str | None = None
    last_tk_victim_name: str | None = None
    last_tk_victim_player_id: str | None = None
    last_tk_victim_weapon: str | None = None
    last_tk_nemesis_name: str | None = None
    last_tk_nemesis_player_id: str | None = None
    last_tk_nemesis_weapon: str | None = None


class ServerInfoType(TypedDict):
    host: str | None
    port: str | None
    password: str | None


# Have to inherit from str to allow for JSON serialization w/ pydantic
class Roles(str, enum.Enum):
    commander = "armycommander"
    squad_lead = "officer"
    rifleman = "rifleman"
    engineer = "engineer"
    medic = "medic"
    anti_tank = "antitank"
    automatic_rifleman = "automaticrifleman"
    assault = "assault"
    machine_gunner = "heavymachinegunner"
    support = "support"
    spotter = "spotter"
    sniper = "sniper"
    tank_commander = "tankcommander"
    crewman = "crewman"


class InvalidRoleError(ValueError):
    def __init__(self, role: str) -> None:
        super().__init__()
        self.role = role

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.role} must be one of ({', '.join(r for r in Roles)})"

    def asdict(self):
        return {
            "type": InvalidRoleError.__name__,
            "role": self.role,
            "allowed_roles": [r for r in Roles],
        }


ROLES_TO_LABELS = {
    Roles.commander: "Commander",
    Roles.squad_lead: "Squad Lead",
    Roles.rifleman: "Rifleman",
    Roles.engineer: "Engineer",
    Roles.medic: "Medic",
    Roles.anti_tank: "Anti-Tank",
    Roles.automatic_rifleman: "Automatic Rifleman",
    Roles.assault: "Assault",
    Roles.machine_gunner: "Machinegunner",
    Roles.support: "Support",
    Roles.spotter: "Spotter",
    Roles.sniper: "Sniper",
    Roles.tank_commander: "Tank Commander",
    Roles.crewman: "Crewman",
}


class AdminType(TypedDict):
    player_id: str
    name: str
    role: str


class StatusType(TypedDict):
    name: str
    map: "LayerType"
    current_players: int
    max_players: int
    short_name: str
    server_number: int


class VipIdType(TypedDict):
    player_id: str
    name: str
    vip_expiration: datetime.datetime | None


class GameServerBanType(TypedDict):
    type: str
    name: str | None
    player_id: str | None
    timestamp: datetime.datetime | None
    ban_time: str | None
    reason: str | None
    by: str | None
    raw: str


class SteamPlayerSummaryType(TypedDict):
    """Result of steam API ISteamUser.GetPlayerSummaries"""

    avatar: str
    avatarfull: str
    avatarhash: str
    avatarmedium: str
    # 1 - not visible 3 - visibile
    communityvisibilitystate: Literal[1] | Literal[3]
    lastlogoff: int
    loccityid: int
    loccountrycode: str
    locstatecode: str
    personaname: str
    personastate: int
    personastateflags: int
    primaryclanid: str
    profilestate: int
    profileurl: str
    realname: str
    steamid: str
    timecreated: int


class SteamBansType(TypedDict):
    """Result of steam API ISteamUser.GetPlayerBans"""

    SteamId: str
    CommunityBanned: bool
    VACBanned: bool
    NumberOfVACBans: int
    DaysSinceLastBan: int
    NumberOfGameBans: int
    EconomyBan: str


class SteamInfoType(TypedDict):
    """Dictionary version of SteamInfo model"""

    id: int
    created: datetime.datetime
    updated: datetime.datetime
    profile: SteamPlayerSummaryType | None
    country: str | None
    bans: SteamBansType | None
    has_bans: bool


class PlayerNameType(TypedDict):
    id: int
    name: str
    player_id: str
    created: datetime.datetime
    last_seen: datetime.datetime


class PlayerSessionType(TypedDict):
    id: int
    player_id: str
    start: Optional[datetime.datetime]
    end: Optional[datetime.datetime]
    created: datetime.datetime


class BasicPlayerProfileType(TypedDict):
    id: int
    player_id: str
    created: datetime.datetime
    names: list[PlayerNameType]
    steaminfo: Optional[SteamInfoType]


class BlacklistSyncMethod(str, enum.Enum):
    """Enumeration of all available methods when it comes to enforcing
    blacklists. Each method has its pros and cons."""

    KICK_ONLY = "kick_only"
    """Kick only: Kick a player as soon as they connect. This means the ban
    reason is always visible and variables remain up-to-date. However, the
    player must wait in queue before being told they are banned."""

    BAN_ON_CONNECT = "ban_on_connect"
    """Ban on connect: Ban a player as soon as they connect. This is a balance
    between the other two options and guarantees the player sees the ban reason
    (exactly) once."""

    BAN_IMMEDIATELY = "ban_immediately"
    """Ban immediately: Immediately ban the player from the server. Unless they
    are online at the time of the ban, they will never be able to actually see
    the reason they were banned."""


class BlacklistType(TypedDict):
    id: int
    name: str
    sync: BlacklistSyncMethod
    servers: Optional[List[int]]


class BlacklistRecordType(TypedDict):
    id: int
    player_id: str
    reason: str
    admin_name: str
    created_at: datetime.datetime
    expires_at: Optional[datetime.datetime]
    is_active: bool


class BlacklistWithRecordsType(BlacklistType):
    records: List[BlacklistRecordType]


class BlacklistRecordWithBlacklistType(BlacklistRecordType):
    blacklist: BlacklistType


class BlacklistRecordWithPlayerType(BlacklistRecordWithBlacklistType):
    player: BasicPlayerProfileType
    formatted_reason: str


class PlayerActionType(TypedDict):
    action_type: str
    reason: Optional[str]
    by: Optional[str]
    time: datetime.datetime


class DBLogLineType(TypedDict):
    id: int
    version: int
    creation_time: datetime.datetime
    event_time: datetime.datetime
    type: Optional[str]
    player1_name: Optional[str]
    player1_id: Optional[str]
    player2_name: Optional[str]
    player2_id: Optional[str]
    raw: str
    content: str
    server: str
    weapon: Optional[str]


class PlayerStatsType(TypedDict):
    id: int
    player_id: str
    player: Optional[str]
    steaminfo: Optional[SteamInfoType]
    map_id: int
    kills: Optional[int]
    kills_streak: Optional[int]
    deaths: Optional[int]
    deaths_without_kill_streak: Optional[int]
    teamkills: Optional[int]
    teamkills_streak: Optional[int]
    deaths_by_tk: Optional[int]
    deaths_by_tk_streak: Optional[int]
    nb_vote_started: Optional[int]
    nb_voted_yes: Optional[int]
    nb_voted_no: Optional[int]
    time_seconds: Optional[int]
    kills_per_minute: Optional[float]
    deaths_per_minute: Optional[float]
    kill_death_ratio: Optional[float]
    longest_life_secs: Optional[int]
    shortest_life_secs: Optional[int]
    combat: Optional[int]
    offense: Optional[int]
    defense: Optional[int]
    support: Optional[int]
    most_killed: Optional[dict]
    death_by: Optional[dict]
    weapons: Optional[dict]
    death_by_weapons: Optional[dict]


class PlayerStat(TypedDict):
    combat: int
    p_combat: int
    offense: int
    p_offense: int
    defense: int
    p_defense: int
    support: int
    p_support: int


class CachedLiveGameStats(TypedDict):
    snapshot_timestamp: datetime.datetime
    stats: PlayerStatsType
    refresh_interval_sec: int


class MapInfo(TypedDict):
    name: str
    start: float | None
    end: float | None
    guessed: bool
    player_stats: dict[str, PlayerStat]


class MapInfoISODates(TypedDict):
    name: str
    start: str | None
    end: str | None
    guessed: bool
    player_stats: dict[str, PlayerStat]


class MapsType(TypedDict):
    id: int
    creation_time: datetime.datetime
    start: datetime.datetime
    end: Optional[datetime.datetime]
    server_number: Optional[int]
    map_name: str
    result: Optional[dict[str, int]]
    player_stats: List[PlayerStatsType]


class PlayerCommentType(TypedDict):
    id: int
    player_id: str
    creation_time: datetime.datetime
    by: Optional[str]
    content: str


class PlayerAtCountType(TypedDict):
    player_id: str
    name: str
    vip: Optional[bool]


class ServerCountType(TypedDict):
    server_number: Optional[int]
    minute: datetime.datetime
    count: int
    players: List[PlayerAtCountType]
    map: str
    vip_count: int


class AdminUserType(TypedDict):
    username: str
    player_id: str


class AuditLogType(TypedDict):
    id: int
    username: str
    creation_time: datetime.datetime
    command: str
    command_arguments: Optional[str]
    command_result: Optional[str]


class PenaltyCountType(TypedDict):
    KICK: int
    PUNISH: int
    TEMPBAN: int
    PERMABAN: int


class PlayerFlagType(TypedDict):
    id: int
    flag: str
    comment: Optional[str]
    modified: datetime.datetime


class PlayerOptinsType(TypedDict):
    id: int
    optin_name: str
    optin_value: Optional[str]
    modified: datetime.datetime


class WatchListType(TypedDict):
    id: int
    modified: datetime.datetime
    player_id: str
    is_watched: bool
    reason: str
    by: str
    count: int


# TODO: Remove? Not used anywhere
class UserConfigType(TypedDict):
    key: str
    value: str


class PlayerVIPType(TypedDict):
    server_number: int
    expiration: datetime.datetime


class PlayerProfileType(BasicPlayerProfileType):
    sessions: list[PlayerSessionType]
    sessions_count: int
    total_playtime_seconds: int
    current_playtime_seconds: int
    received_actions: list[PlayerActionType]
    penalty_count: PenaltyCountType
    blacklists: list[BlacklistRecordWithBlacklistType]
    is_blacklisted: bool
    flags: list[PlayerFlagType]
    watchlist: Optional[WatchListType]
    vips: Optional[list[PlayerVIPType]]


class PlayerProfileTypeEnriched(PlayerProfileType):
    bans: list[GameServerBanType]
    comments: list[PlayerCommentType]


class GetDetailedPlayer(TypedDict):
    name: str
    player_id: str
    profile: PlayerProfileType | None
    is_vip: bool
    unit_id: Optional[int]
    unit_name: Optional[str]
    loadout: Optional[str]
    team: Optional[str]
    role: Optional[str]
    kills: int
    deaths: int
    combat: int
    offense: int
    defense: int
    support: int
    level: int


class GetDetailedPlayers(TypedDict):
    players: dict[str, GetDetailedPlayer]
    fail_count: int


class GetPlayersType(TypedDict):
    name: str
    player_id: str
    country: str | None
    steam_bans: Optional[SteamBansType]
    is_vip: bool
    profile: PlayerProfileType | None


class StructuredLogLineType(TypedDict):
    action: str
    player_name_1: str | None
    player_id_1: str | None
    player_name_2: str | None
    player_id_2: str | None
    weapon: str | None
    message: str
    sub_content: str | None


class StructuredLogLineWithMetaData(TypedDict):
    version: int
    timestamp_ms: int
    event_time: datetime.datetime
    relative_time_ms: float | None
    raw: str
    line_without_time: str | None
    action: str
    player_name_1: str | None
    player_id_1: str | None
    player_name_2: str | None
    player_id_2: str | None
    weapon: str | None
    message: str
    sub_content: str | None


class ParsedLogsType(TypedDict):
    actions: list[str]
    players: list[str]
    logs: list[StructuredLogLineWithMetaData]


class GameState(TypedDict):
    """TypedDict for Rcon.get_gamestate"""

    num_allied_players: int
    num_axis_players: int
    allied_score: int
    axis_score: int
    raw_time_remaining: str
    time_remaining: datetime.timedelta
    current_map: "LayerType"
    next_map: "LayerType"


class VACGameBansConfigType(TypedDict):
    ban_on_vac_history_days: int
    max_game_ban_threshold: int
    ban_on_vac_history_reason: str
    whitelist_flags: list[str]


class VipId(TypedDict):
    player_id: str
    name: str


class VoteMapPlayerVoteType(TypedDict):
    player_name: str
    map_name: str


class VoteMapResultType(TypedDict):
    map: Layer
    num_votes: int


# TODO: finish this typing
class VoteMapStatusType(TypedDict):
    map: Layer
    voters: dict[Layer, list[str]]


# Have to inherit from str to allow for JSON serialization w/ pydantic
class AllLogTypes(str, enum.Enum):
    """Both native (from the game server) and synthetic (created by CRCON) log types"""

    admin = "ADMIN"
    admin_anti_cheat = "ADMIN ANTI-CHEAT"
    admin_banned = "ADMIN BANNED"
    admin_idle = "ADMIN IDLE"
    admin_kicked = "ADMIN KICKED"
    admin_misc = "ADMIN MISC"
    admin_perma_banned = "ADMIN PERMA BANNED"
    allies_chat = "CHAT[Allies]"
    allies_team_chat = "CHAT[Allies][Team]"
    allies_unit_chat = "CHAT[Allies][Unit]"
    axis_chat = "CHAT[Axis]"
    axis_team_chat = "CHAT[Axis][Team]"
    axis_unit_chat = "CHAT[Axis][Unit]"
    camera = "CAMERA"
    chat = "CHAT"
    connected = "CONNECTED"
    disconnected = "DISCONNECTED"
    kill = "KILL"
    match = "MATCH"
    match_end = "MATCH ENDED"
    match_start = "MATCH START"
    team_kill = "TEAM KILL"
    team_switch = "TEAMSWITCH"
    # Automatic kicks for team kills
    tk = "TK"
    tk_auto = "TK AUTO"
    tk_auto_banned = "TK AUTO BANNED"
    tk_auto_kicked = "TK AUTO KICKED"
    # Vote kicks
    vote = "VOTE"
    vote_completed = "VOTE COMPLETED"
    vote_expired = "VOTE EXPIRED"
    vote_passed = "VOTE PASSED"
    vote_started = "VOTE STARTED"


class InvalidLogTypeError(ValueError):
    def __init__(self, log_type: str) -> None:
        super().__init__()
        self.log_type = log_type

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.log_type} must be one of ({', '.join(r for r in AllLogTypes)})"

    def asdict(self):
        return {
            "type": InvalidLogTypeError.__name__,
            "log_type": self.log_type,
            "allowed_log_types": [log for log in AllLogTypes],
        }


class PublicInfoMapType(TypedDict):
    map: LayerType
    start: float | None


class PublicInfoPlayerType(TypedDict):
    allied: int
    axis: int


class PublicInfoScoreType(TypedDict):
    allied: int
    axis: int


class PublicInfoNameType(TypedDict):
    name: str
    short_name: str
    public_stats_port: int | None
    public_stats_port_https: int | None


class PublicInfoType(TypedDict):
    """TypedDict for rcon.views.get_public_info"""

    current_map: PublicInfoMapType
    next_map: PublicInfoMapType
    player_count: int
    max_player_count: int
    player_count_by_team: PublicInfoPlayerType
    score: PublicInfoScoreType
    time_remaining: float
    vote_status: list[VoteMapStatusType]
    name: PublicInfoNameType


class SlotsType(TypedDict):
    current_players: int
    max_players: int


class DjangoPermission(TypedDict):
    permission: str
    description: str


class DjangoGroup(TypedDict):
    name: str


class DjangoUserPermissions(TypedDict):
    permissions: list[DjangoPermission]
    groups: list[DjangoGroup]
    is_superuser: bool
