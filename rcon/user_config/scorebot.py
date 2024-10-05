import enum
from typing import Optional, TypedDict

from pydantic import BaseModel, Field, HttpUrl, field_serializer, field_validator

from rcon.types import StatTypes
from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config
from rcon.utils import get_server_number

STATS_ENDPOINT = "/api/get_live_game_stats"
INFO_ENDPOINT = "/api/get_public_info"
PAST_GAMES_ENDPOINT = "/#/gamescoreboard"

STAT_TYPES = (
    "TOP_KILLERS",
    "TOP_RATIO",
    "TOP_PERFORMANCE",
    "TRY_HARDERS",
    "TOP_STAMINA",
    "TOP_KILL_STREAK",
    "I_NEVER_GIVE_UP",
    "MOST_PATIENT",
    "I_M_CLUMSY",
    "I_NEED_GLASSES",
    "I_LOVE_VOTING",
    "WHAT_IS_A_BREAK",
    "SURVIVORS",
    "U_R_STILL_A_MAN",
)

ALL_STATS = "All stats on: "
AUTHOR_NAME = "STATS LIVE HLL FRANCE - click here"
# TODO: host this locally
AUTHOR_ICON_URL = "https://static.wixstatic.com/media/da3421_111b24ae66f64f73aa94efeb80b08f58~mv2.png/v1/fit/w_2500,h_1330,al_c/da3421_111b24ae66f64f73aa94efeb80b08f58~mv2.png"
FOOTER_ICON_URL = "https://static.wixstatic.com/media/da3421_111b24ae66f64f73aa94efeb80b08f58~mv2.png/v1/fit/w_2500,h_1330,al_c/da3421_111b24ae66f64f73aa94efeb80b08f58~mv2.png"
NO_STATS_AVAILABLE = "No stats recorded for that game yet"
FIND_PAST_STATS = "Stats of past games on: "
NEXT_MAP = "Next map"
VOTE = "vote(s)"
PLAYERS = "players"
ELAPSED_TIME = "Elapsed game time: "
ALLIED_PLAYERS = "Allied Players"
AXIS_PLAYERS = "Axis Players"
MATCH_SCORE_TITLE = "Match Score"
MATCH_SCORE = "Allied {0} : Axis {1}"
TIME_REMAINING = "Time Remaining"

TOP_KILLERS = ":knife: TOP KILLERS\n*kills*"
TOP_RATIO = ":knife: TOP RATIO\n*kills/death*"
TOP_PERFORMANCE = ":knife: TOP PERFORMANCE\n*kills/minute*"
TRY_HARDERS = ":skull: TRY HARDERS\n*deaths/minute*"
TOP_STAMINA = ":skull: TOP STAMINA\n*deaths*"
TOP_KILL_STREAK = ":knife: TOP KILL STREAK\n*kill streak*"
MOST_PATIENT = ":skull: MOST PATIENT\n*death by teamkill*"
I_NEVER_GIVE_UP = ":skull: I NEVER GIVE UP\n*death streak*"
I_M_CLUMSY = "YES I'M CLUMSY\n*teamkills*"
I_NEED_GLASSES = ":eyeglasses: I NEED GLASSES\n*teamkill streak*"
I_LOVE_VOTING = "I :heart: VOTING\n*num. votes started*"
WHAT_IS_A_BREAK = "WHAT IS A BREAK?\n*ingame time*"
SURVIVORS = ":clock1: SURVIVORS\n*longest life (min.)*"
U_R_STILL_A_MAN = "U'R STILL A MAN\n*shortest life (min.)*"


def seed_default_displays():
    return [
        StatDisplay(type=type_, display_format=format_)
        for type_, format_ in zip(
            (
                StatTypes.top_killers,
                StatTypes.top_ratio,
                StatTypes.top_performance,
                StatTypes.try_harders,
                StatTypes.top_stamina,
                StatTypes.top_kill_streak,
                StatTypes.most_patient,
                StatTypes.i_never_give_up,
                StatTypes.im_clumsy,
                StatTypes.i_need_glasses,
                StatTypes.i_love_voting,
                StatTypes.what_is_a_break,
                StatTypes.survivors,
                StatTypes.u_r_still_a_man,
            ),
            (
                TOP_KILLERS,
                TOP_RATIO,
                TOP_PERFORMANCE,
                TRY_HARDERS,
                TOP_STAMINA,
                TOP_KILL_STREAK,
                MOST_PATIENT,
                I_NEVER_GIVE_UP,
                I_M_CLUMSY,
                I_NEED_GLASSES,
                I_LOVE_VOTING,
                WHAT_IS_A_BREAK,
                SURVIVORS,
                U_R_STILL_A_MAN,
            ),
        )
    ]


class StatDisplay(BaseModel):
    type: StatTypes
    display_format: str


class ScorebotConfigType(TypedDict):
    all_stats_text: str
    author_name_text: str
    author_icon_url: str
    top_limit: int
    footer_icon_url: str
    no_stats_available_text: str
    find_past_stats_text: str
    next_map_text: str
    vote_text: str
    players_text: str
    elapsed_time_text: str
    allied_players_text: str
    axis_players_text: str
    match_score_title_text: str
    match_score_text: str
    time_remaining_text: str
    refresh_time_secs: int

    stats_to_display: list[StatDisplay]

    base_api_url: HttpUrl
    base_scoreboard_url: HttpUrl

    webhook_urls: list[str]


class ScorebotUserConfig(BaseUserConfig):
    all_stats_text: str = Field(default=ALL_STATS)
    author_name_text: str = Field(default=AUTHOR_NAME)
    author_icon_url: str = Field(default=AUTHOR_ICON_URL)
    top_limit: int = Field(ge=1, le=100, default=10)
    footer_icon_url: str = Field(default=FOOTER_ICON_URL)
    no_stats_available_text: str = Field(default=NO_STATS_AVAILABLE)
    find_past_stats_text: str = Field(default=FIND_PAST_STATS)
    next_map_text: str = Field(default=NEXT_MAP)
    vote_text: str = Field(default=VOTE)
    players_text: str = Field(default=PLAYERS)
    elapsed_time_text: str = Field(default=ELAPSED_TIME)
    allied_players_text: str = Field(default=ALLIED_PLAYERS)
    axis_players_text: str = Field(default=AXIS_PLAYERS)
    match_score_title_text: str = Field(default=MATCH_SCORE_TITLE)
    match_score_text: str = Field(default=MATCH_SCORE)
    time_remaining_text: str = Field(default=TIME_REMAINING)
    refresh_time_secs: int = Field(ge=1, default=5)

    stats_to_display: list[StatDisplay] = Field(default_factory=seed_default_displays)

    base_api_url: Optional[HttpUrl] = Field(
        default=HttpUrl(f"http://frontend_{get_server_number()}/")
    )
    base_scoreboard_url: Optional[HttpUrl] = Field(default=None)

    webhook_urls: list[str] = Field(default_factory=list)

    @field_serializer("base_api_url", "base_scoreboard_url")
    def serialize_server_url(self, url: HttpUrl, _info):
        if url is not None:
            return str(url)
        else:
            return None

    @field_validator("stats_to_display")
    @classmethod
    def unique_stats(cls, vs):
        unique_types = set()
        unique = []
        for v in vs:
            if v.type not in unique_types:
                unique.append(v)
                unique_types.add(v.type)

        return unique

    @property
    def stats_url(self) -> str:
        if not self.base_api_url:
            raise ValueError("base API URL not set")

        if str(self.base_api_url).endswith("/"):
            api_url = str(self.base_api_url)[:-1]
        else:
            api_url = str(self.base_api_url)

        validated_url = api_url + STATS_ENDPOINT

        HttpUrl(validated_url)
        return validated_url

    @property
    def info_url(self) -> str:
        if not self.base_api_url:
            raise ValueError("base API URL not set")

        if str(self.base_api_url).endswith("/"):
            api_url = str(self.base_api_url)[:-1]
        else:
            api_url = str(self.base_api_url)

        validated_url = api_url + INFO_ENDPOINT
        HttpUrl(validated_url)
        return validated_url

    @property
    def past_games_url(self) -> str:
        if not self.base_scoreboard_url:
            raise ValueError("base scoreboard URL not set")

        if str(self.base_scoreboard_url).endswith("/"):
            scoreboard_url = str(self.base_scoreboard_url)[:-1]
        else:
            scoreboard_url = str(self.base_scoreboard_url)

        validated_url = scoreboard_url + PAST_GAMES_ENDPOINT
        HttpUrl(validated_url)
        return validated_url

    @staticmethod
    def save_to_db(values: ScorebotConfigType, dry_run=False):
        key_check(
            ScorebotConfigType.__required_keys__,
            ScorebotConfigType.__optional_keys__,
            values.keys(),
        )

        validated_conf = ScorebotUserConfig(
            all_stats_text=values.get("all_stats_text"),
            author_name_text=values.get("author_name_text"),
            author_icon_url=values.get("author_icon_url"),
            top_limit=values.get("top_limit"),
            footer_icon_url=values.get("footer_icon_url"),
            no_stats_available_text=values.get("no_stats_available_text"),
            find_past_stats_text=values.get("find_past_stats_text"),
            next_map_text=values.get("next_map_text"),
            vote_text=values.get("vote_text"),
            players_text=values.get("players_text"),
            elapsed_time_text=values.get("elapsed_time_text"),
            allied_players_text=values.get("allied_players_text"),
            axis_players_text=values.get("axis_players_text"),
            match_score_title_text=values.get("match_score_title_text"),
            match_score_text=values.get("match_score_text"),
            time_remaining_text=values.get("time_remaining_text"),
            refresh_time_secs=values.get("refresh_time_secs"),
            stats_to_display=values.get("stats_to_display"),
            base_api_url=values.get("base_api_url"),
            base_scoreboard_url=values.get("base_scoreboard_url"),
            webhook_urls=values.get("webhook_urls"),
        )

        if not dry_run:
            set_user_config(validated_conf.KEY(), validated_conf)
