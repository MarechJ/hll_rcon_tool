import enum
from enum import StrEnum
from logging import getLogger
from typing import Final, Literal, Optional, Self, TypedDict

from pydantic import BaseModel, Field, HttpUrl, field_serializer, field_validator

from rcon.types import PlayerStatsEnum
from rcon.user_config.legacy_scorebot import ScorebotUserConfig
from rcon.user_config.utils import BaseUserConfig, _listType, key_check, set_user_config
from rcon.user_config.webhooks import DiscordWebhook, WebhookType
from rcon.utils import get_server_number

logger = getLogger(__name__)

EMPTY_EMBED: Final = "\u200B"

MAP_LEGEND = """
Legend
🟩 - Current Map
🟨 - Next Map
⬛ - Other Maps"""


# TODO: remove this in a few releases
def _port_legacy_scorebot_urls():
    config = ScoreboardUserConfig.load_from_db()
    legacy_config = ScorebotUserConfig.load_from_db()

    modified = False
    if config.public_scoreboard_url is None:
        logger.info(f"Attempting migration of {legacy_config.base_scoreboard_url=}")
        config.public_scoreboard_url = legacy_config.base_scoreboard_url
        modified = True

    if not config.hooks:
        logger.info(f"Attempting migration of {legacy_config.webhook_urls=}")
        config.hooks = [DiscordWebhook(url=url) for url in legacy_config.webhook_urls]
        modified = True

    if modified:
        ScoreboardUserConfig.save_to_db(config.model_dump())


class EmbedType(TypedDict):
    name: str
    value: str
    inline: bool


class StatDisplayType(TypedDict):
    type: PlayerStatsEnum
    display_format: str


class StatDisplay(BaseModel):
    type: PlayerStatsEnum
    display_format: str


class ScoreboardConfigType(TypedDict):
    public_scoreboard_url: HttpUrl
    hooks: list[WebhookType]

    footer_last_refreshed_text: str

    header_gamestate_time_between_refreshes: int
    server_name: bool
    quick_connect_url: HttpUrl
    battlemetrics_url: HttpUrl
    show_map_image: bool
    objective_score_format_generic: str
    objective_score_format_ger_v_us: str
    objective_score_format_ger_v_sov: str
    objective_score_format_ger_v_uk: str
    header_gamestate_embeds: list[EmbedType]

    # Map Rotation (own message)
    map_rotation_time_between_refreshes: int
    show_map_rotation: bool
    current_map_format: str
    next_map_format: str
    other_map_format: str
    show_map_legend: bool
    map_rotation_title_text: str
    map_legend: str

    # Player Stats (own message)
    player_stats_title_text: str
    player_stats_time_between_refreshes: int
    player_stats_num_to_display: int
    player_stat_embeds: list[EmbedType]


class HeaderGameStateEmbedEnum(StrEnum):
    QUICK_CONNECT_URL = "quick_connect_url"
    BATTLEMETRICS_URL = "battlemetrics_url"
    RESERVED_VIP_SLOTS = "reserved_vip_slots"
    CURRENT_VIPS = "current_vips"
    NUM_ALLIED_PLAYERS = "num_allied_players"
    NUM_AXIS_PLAYERS = "num_axis_players"
    NUM_ALLIED_VIPS = "num_allied_vips"
    NUM_AXIS_VIPS = "num_axis_vips"
    SLOTS = "slots"
    SCORE = "score"
    TIME_REMAINING = "time_remaining"
    CURRENT_MAP = "current_map"
    NEXT_MAP = "next_map"


class HeaderGameStateEmbedTextEnum(StrEnum):
    QUICK_CONNECT_URL = "Quick Connect"
    BATTLEMETRICS_URL = "BattleMetrics"
    RESERVED_VIP_SLOTS = "Reserved VIP Slots"
    CURRENT_VIPS_TEXT = "Current VIPs"
    NUM_ALLIED_PLAYERS = "# Allied Players"
    NUM_AXIS_PLAYERS = "# Axis Players"
    NUM_ALLIED_VIPS = "# Allied VIPs"
    NUM_AXIS_VIPS = "# Axis VIPs"
    SLOTS = "Total Players"
    SCORE = "Match Score"
    TIME_REMAINING = "Time Remaining"
    CURRENT_MAP = "Current Map"
    NEXT_MAP = "Next Map"


class HeaderGameStateEmbedConfig(BaseModel):
    name: str
    value: str
    inline: bool

    @field_validator("value")
    def must_be_valid_embed(cls, v):
        if v not in HeaderGameStateEmbedEnum and v != EMPTY_EMBED:
            raise ValueError(f"Invalid header_gamestate embed {v}")

        return v


def seed_default_header_gamestate_displays() -> list[HeaderGameStateEmbedConfig]:
    embeds = (
        HeaderGameStateEmbedEnum.NUM_ALLIED_PLAYERS,
        HeaderGameStateEmbedEnum.NUM_AXIS_PLAYERS,
        HeaderGameStateEmbedEnum.SLOTS,
        EMPTY_EMBED,
        HeaderGameStateEmbedEnum.NUM_ALLIED_VIPS,
        HeaderGameStateEmbedEnum.NUM_AXIS_VIPS,
        EMPTY_EMBED,
        HeaderGameStateEmbedEnum.SCORE,
        HeaderGameStateEmbedEnum.TIME_REMAINING,
        EMPTY_EMBED,
        HeaderGameStateEmbedEnum.CURRENT_MAP,
        HeaderGameStateEmbedEnum.NEXT_MAP,
    )

    embeds_as_config: list[HeaderGameStateEmbedConfig] = []
    for embed in embeds:
        if isinstance(embed, HeaderGameStateEmbedEnum):
            name = HeaderGameStateEmbedTextEnum[embed.value.upper()]
            inline = True
        else:
            name = "EMPTY"
            inline = False

        embeds_as_config.append(
            HeaderGameStateEmbedConfig(name=name, value=embed, inline=inline)
        )

    return embeds_as_config


class PlayerStatEmbedConfig(BaseModel):
    name: str
    value: str
    inline: bool

    @field_validator("value")
    def must_be_valid_embed(cls, v):
        if v not in PlayerStatsEnum and v != EMPTY_EMBED:
            raise ValueError(f"Invalid header_gamestate embed {v}")

        return v


class PlayerStatsTextEnum(StrEnum):
    KILLS = ":knife: Highest Kills"
    KILLS_STREAK = ":knife: Kill Streak"
    DEATHS = ":skull: Highest Deaths"
    DEATHS_WITHOUT_KILL_STREAK = ":skull: Death Streak"
    TEAMKILLS = ":skull: Highest Team Kills"
    TEAMKILLS_STREAK = ":no_entry: Team Kill Streak"
    DEATHS_BY_TK = ":no_entry: Highest Team Kill Deaths"
    DEATHS_BY_TK_STREAK = ":no_entry: Highest Team Kill Death Streak"
    NB_VOTE_STARTED = "Votes Started"
    LONGEST_LIFE_SECS = ":clock9: Longest Life"
    SHORTEST_LIFE_SECS = ":clock1: Shortest Life"
    KILL_DEATH_RATIO = ":knife: Highest KDR"
    KILLS_PER_MINUTE = ":knife: Kills/Minute"
    DEATHS_PER_MINUTE = ":skull: Deaths/Minute"
    TIME_SECONDS = ":clock1: In Game Time"


def seed_default_player_stat_displays():
    embeds = (
        PlayerStatsEnum.KILLS,
        PlayerStatsEnum.DEATHS,
        EMPTY_EMBED,
        PlayerStatsEnum.TEAMKILLS,
        PlayerStatsEnum.KILL_DEATH_RATIO,
        EMPTY_EMBED,
        PlayerStatsEnum.KILLS_PER_MINUTE,
        PlayerStatsEnum.DEATHS_PER_MINUTE,
        EMPTY_EMBED,
        PlayerStatsEnum.KILLS_STREAK,
        PlayerStatsEnum.DEATHS_WITHOUT_KILL_STREAK,
        EMPTY_EMBED,
        PlayerStatsEnum.TEAMKILLS_STREAK,
        PlayerStatsEnum.DEATHS_BY_TK,
        EMPTY_EMBED,
        PlayerStatsEnum.LONGEST_LIFE_SECS,
        PlayerStatsEnum.SHORTEST_LIFE_SECS,
        EMPTY_EMBED,
        PlayerStatsEnum.TIME_SECONDS,
        PlayerStatsEnum.NB_VOTE_STARTED,
    )

    embeds_as_config: list[PlayerStatEmbedConfig] = []
    for embed in embeds:
        if isinstance(embed, PlayerStatsEnum):
            name = PlayerStatsTextEnum[embed.value.upper()]
            inline = True
        else:
            name = "EMPTY"
            inline = False

        embeds_as_config.append(
            PlayerStatEmbedConfig(name=name, value=embed, inline=inline)
        )

    return embeds_as_config


class ScoreboardUserConfig(BaseUserConfig):
    public_scoreboard_url: HttpUrl | None = Field(default=None)
    hooks: list[DiscordWebhook] = Field(default_factory=list)

    footer_last_refreshed_text: str = Field(default="Last Refreshed")

    # Header / Gamestate (own message)
    header_gamestate_time_between_refreshes: int = Field(default=5)
    server_name: bool = Field(default=True)
    quick_connect_url: HttpUrl | None = Field(default=None)
    battlemetrics_url: HttpUrl | None = Field(default=None)
    show_map_image: bool = Field(default=True)
    objective_score_format_generic: str = Field(default="Allied {0}: Axis {1}")
    objective_score_format_ger_v_us: str = Field(
        default="<:icoT_US:1060219985215094804> {0} : <:icoT_GER:1060219972871278602> {1}"
    )
    objective_score_format_ger_v_sov: str = Field(
        default="<:icoT_RUS:1060217170455433286> {0} : <:icoT_GER:1060219972871278602> {1}"
    )
    objective_score_format_ger_v_uk: str = Field(
        default="<:icoT_UK:1114060867068235807> {0} : <:icoT_GER:1060219972871278602> {1}"
    )
    header_gamestate_embeds: list[HeaderGameStateEmbedConfig] = Field(
        default_factory=seed_default_header_gamestate_displays
    )

    # Map Rotation (own message)
    map_rotation_time_between_refreshes: int = Field(default=30)
    show_map_rotation: bool = Field(default=True)
    current_map_format: str = Field(default="🟩 {1}. **{0}**")
    next_map_format: str = Field(default="🟨 {1}. {0}")
    other_map_format: str = Field(default="⬛ {1}. {0}")
    show_map_legend: bool = Field(default=True)
    map_rotation_title_text: str = Field(default="Map Rotation")
    map_legend: str = Field(default=MAP_LEGEND)

    # Player Stats (own message)
    player_stats_title_text: str = Field(default="Player Stats")
    player_stats_time_between_refreshes: int = Field(default=5)
    player_stats_num_to_display: int = Field(default=5)
    player_stat_embeds: list[PlayerStatEmbedConfig] = Field(
        default_factory=seed_default_player_stat_displays
    )

    @field_serializer("quick_connect_url", "battlemetrics_url", "public_scoreboard_url")
    def serialize_server_url(self, url: HttpUrl, _info):
        if url is not None:
            return str(url)
        else:
            return None

    @staticmethod
    def save_to_db(values: ScoreboardConfigType, dry_run=False):
        key_check(
            ScoreboardConfigType.__required_keys__,
            ScoreboardConfigType.__optional_keys__,
            values.keys(),
        )
        raw_hooks: list[WebhookType] = values.get("hooks")
        raw_stat_types: list[EmbedType] = values.get("player_stat_embeds")
        raw_header_gamestate_embeds: list[EmbedType] = values.get(
            "header_gamestate_embeds"
        )
        _listType(values=raw_hooks)
        _listType(values=raw_stat_types)

        validated_hooks = [DiscordWebhook(url=obj.get("url")) for obj in raw_hooks]
        validated_header_gamestate_embeds = [
            HeaderGameStateEmbedConfig(
                name=obj.get("name"), value=obj.get("value"), inline=obj.get("inline")
            )
            for obj in raw_header_gamestate_embeds
        ]
        validated_stat_types = [
            PlayerStatEmbedConfig(
                name=obj.get("name"), value=obj.get("value"), inline=obj.get("inline")
            )
            for obj in raw_stat_types
        ]

        validated_conf = ScoreboardUserConfig(
            public_scoreboard_url=values.get("public_scoreboard_url"),
            hooks=validated_hooks,
            footer_last_refreshed_text=values.get("footer_last_refreshed_text"),
            header_gamestate_time_between_refreshes=values.get(
                "header_gamestate_time_between_refreshes"
            ),
            server_name=values.get("server_name"),
            quick_connect_url=values.get("quick_connect_url"),
            battlemetrics_url=values.get("battlemetrics_url"),
            show_map_image=values.get("show_map_image"),
            objective_score_format_generic=values.get("objective_score_format_generic"),
            objective_score_format_ger_v_us=values.get(
                "objective_score_format_ger_v_us"
            ),
            objective_score_format_ger_v_sov=values.get(
                "objective_score_format_ger_v_sov"
            ),
            objective_score_format_ger_v_uk=values.get(
                "objective_score_format_ger_v_uk"
            ),
            header_gamestate_embeds=validated_header_gamestate_embeds,
            map_rotation_time_between_refreshes=values.get(
                "map_rotation_time_between_refreshes"
            ),
            show_map_rotation=values.get("show_map_rotation"),
            current_map_format=values.get("current_map_format"),
            next_map_format=values.get("next_map_format"),
            other_map_format=values.get("other_map_format"),
            show_map_legend=values.get("show_map_legend"),
            map_rotation_title_text=values.get("map_rotation_title_text"),
            map_legend=values.get("map_legend"),
            player_stats_title_text=values.get("player_stats_title_text"),
            player_stats_time_between_refreshes=values.get(
                "player_stats_time_between_refreshes"
            ),
            player_stats_num_to_display=values.get("player_stats_num_to_display"),
            player_stat_embeds=validated_stat_types,
        )

        if not dry_run:
            set_user_config(validated_conf.KEY(), validated_conf)
