import datetime
from typing import List, Optional, TypedDict


class SteamBansType(TypedDict):
    CommunityBanned: bool
    VACBanned: bool
    NumberOfVACBans: int
    DaysSinceLastBan: int
    NumberOfGameBans: int
    EconomyBan: str
    has_bans: bool


class SteamBanResultType(TypedDict):
    steam_bans: Optional[SteamBansType]


class SteamInfoType(TypedDict):
    id: int
    created: datetime.datetime
    updated: datetime.datetime
    profile: dict  # TODO
    country: str
    bans: dict  # TODO


class PlayerNameType(TypedDict):
    id: int
    name: str
    steam_id_64: str
    created: datetime.datetime
    last_seen: datetime.datetime


class PlayerSessionType(TypedDict):
    id: int
    steam_id_64: str
    start: Optional[datetime.datetime]
    end: Optional[datetime.datetime]
    created: datetime.datetime


class BlackListType(TypedDict):
    steam_id_64: str
    is_blacklisted: bool
    reason: Optional[str]
    by: Optional[str]


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
    player_name: Optional[str]
    player1_id: Optional[str]
    player2_name: Optional[str]
    player2_id: Optional[str]
    raw: str
    content: str
    server: str
    weapon: str


class PlayerStatsType(TypedDict):
    id: int
    player_id: str
    player: Optional[str]
    steaminfo: SteamInfoType
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
    most_killed: Optional[dict]
    death_by: Optional[dict]
    weapons: Optional[dict]
    death_by_weapons: Optional[dict]


class MapsType(TypedDict):
    id: int
    creation_time: datetime.datetime
    star: datetime.datetime
    end: Optional[datetime.datetime]
    server_number: Optional[int]
    map_name: str
    player_stats: List[PlayerStatsType]


class PlayerCommentType(TypedDict):
    id: int
    creation_time: datetime.datetime
    playersteamid_id: int
    by: Optional[str]
    content: str


class PlayerAtCountType(TypedDict):
    steam_id_64: str
    name: str
    vip: Optional[bool]


class ServerCountType(TypedDict):
    server_number: Optional[int]
    minute: datetime.datetime
    count: int
    players: List[PlayerAtCountType]
    map: MapsType
    vip_count: int


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
    steam_id_64: str
    is_watched: bool
    reason: str
    comment: str


class UserConfigType(TypedDict):
    key: str
    value: str


class PlayerProfileType(TypedDict):
    id: int
    steam_id_64: str
    created: datetime.datetime
    names: List[PlayerNameType]
    session: List[PlayerSessionType]
    sessions_count: int
    total_playtime_seconds: int
    current_playtime_seconds: int
    received_actions: List[PlayerActionType]
    penalty_count: PenaltyCountType
    blacklist: Optional[BlackListType]
    flags: List[PlayerFlagType]
    watchlist: Optional[WatchListType]
    steaminfo: Optional[SteamInfoType]


class GetPlayersType(TypedDict):
    name: str
    steam_id_64: str
    country: str
    steam_bans: Optional[SteamBansType]


class EnrichedGetPlayersType(GetPlayersType):
    is_vip: bool
    profile: PlayerProfileType


class StructuredLogLineType(TypedDict):
    action: str
    player: str | None
    steam_id_64_1: str | None
    player2: str | None
    steam_id_64_2: str | None
    weapon: str | None
    message: str
    sub_content: str | None


class StructuredLogLineWithMetaData(TypedDict):
    version: int
    timestamp_ms: int
    relative_time_ms: float
    raw: str
    line_without_time: str
    action: str
    player: str | None
    steam_id_64_1: str | None
    player2: str | None
    steam_id_64_2: str | None
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
    time_remaining: datetime.timedelta
    current_map: str
    next_map: str
