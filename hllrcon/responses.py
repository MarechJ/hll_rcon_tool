from datetime import datetime
from enum import IntEnum, StrEnum
from typing import Annotated, Literal, TypeAlias

from pydantic import AfterValidator, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from hllrcon.data import Faction, GameMode, Layer, Role, TimeOfDay

EmptyStringToNoneValidator = AfterValidator(lambda v: v or None)


class Response(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
    )


# TODO: Add console platforms
class PlayerPlatform(StrEnum):
    STEAM = "steam"
    """Steam"""

    EPIC = "epic"
    """Epic Games Store"""

    XBL = "xbl"
    """Xbox Game Pass"""

    PSN = "psn"
    """PlayStation Network"""

    PS5 = "ps5"
    """PlayStation 5"""

    XSX = "xsx"
    """Xbox Series X|S"""


# TODO: Add console platforms
class SupportedPlatform(StrEnum):
    STEAM = "Steam"
    PC_XBOX = "WinGDK"
    EPIC = "eos"


class PlayerFactionId(IntEnum):
    GER = 0
    US = 1
    SOV = 2
    CW = 3
    DAK = 4
    B8A = 5
    UNASSIGNED = 6


class PlayerRoleId(IntEnum):
    RIFLEMAN = 0
    ASSAULT = 1
    AUTOMATIC_RIFLEMAN = 2
    MEDIC = 3
    SPOTTER = 4
    SUPPORT = 5
    MACHINE_GUNNER = 6
    ANTI_TANK = 7
    ENGINEER = 8
    OFFICER = 9
    SNIPER = 10
    CREWMAN = 11
    TANK_COMMANDER = 12
    COMMANDER = 13


class ForceMode(IntEnum):
    IMMEDIATE = 0
    """Force the player to be switched immediately, killing them if currently alive."""

    # TODO: Verify behavior when player is already dead
    AFTER_DEATH = 1
    """Force the player to be switched upon death."""


class GetAdminLogResponseEntry(Response):
    timestamp: datetime
    message: str


class GetAdminLogResponse(Response):
    entries: list[GetAdminLogResponseEntry]


class GetCommandsResponseEntry(Response):
    id: str = Field(validation_alias="iD")
    friendly_name: str
    is_client_supported: bool


class GetCommandsResponse(Response):
    entries: list[GetCommandsResponseEntry]


class GetAdminGroupsResponse(Response):
    group_names: list[str]


class GetAdminUsersResponseEntry(Response):
    user_id: str
    group: str
    comment: str


class GetAdminUsersResponse(Response):
    admin_users: list[GetAdminUsersResponseEntry]


class GetBansResponseEntry(Response):
    user_id: str
    user_name: str
    time_of_banning: str
    duration_hours: int
    ban_reason: str
    admin_name: str


class GetBansResponse(Response):
    ban_list: list[GetBansResponseEntry]


class GetPlayerResponseScoreData(Response):
    combat: int = Field(validation_alias="cOMBAT")
    offense: int
    defense: int
    support: int


class GetPlayerResponseWorldPosition(Response):
    x: float
    """The east-west horizontal axis. Between -100000 and 100000."""

    y: float
    """The north-south horizontal axis. Between -100000 and 100000."""

    z: float
    """The vertical axis."""


class GetPlayerResponse(Response):
    name: str
    """The player's name"""

    clan_tag: Annotated[str | None, EmptyStringToNoneValidator]
    """The player's clan tag. Empty string if none."""

    id: str = Field(validation_alias="iD")
    """The player's ID"""

    platform: PlayerPlatform
    """The player's platform"""

    eos_id: str = Field(validation_alias="eosId")
    """The player's Epic Online Services ID"""

    level: int
    """The player's level"""

    faction_id: PlayerFactionId = Field(validation_alias="team")
    """The ID of the player's faction."""

    role_id: PlayerRoleId | int = Field(validation_alias="role")
    """The ID of the player's role."""

    platoon: Annotated[str | None, EmptyStringToNoneValidator]
    """The name of the player's squad."""

    loadout: str
    """The player's current loadout. Might not be accurate if not spawned in."""

    kills: int
    """The player's kills"""

    deaths: int
    """The player's deaths"""

    score_data: GetPlayerResponseScoreData
    """The player's score"""

    world_position: GetPlayerResponseWorldPosition
    """The player's position in centimeters"""

    @property
    def faction(self) -> Faction | None:
        return Faction.by_id(self.faction_id)

    @property
    def role(self) -> Role:
        return Role.by_id(self.role_id)


class GetPlayersResponse(Response):
    players: list[GetPlayerResponse]


class GetMapRotationResponseEntry(Response):
    name: str
    game_mode_id: str = Field(validation_alias="gameMode")
    time_of_day: TimeOfDay | str
    id: str = Field(validation_alias="iD")
    position: int

    @property
    def game_mode(self) -> GameMode:
        return GameMode.by_id(self.game_mode_id)

    def find_layer(self, *, strict: bool = True) -> Layer:
        """Attempt to find the layer associated with this map rotation entry.

        Parameters
        ----------
        strict : bool, optional
            Whether to raise an exception if no such layer is known. If set to `False`,
            will attempt to generate a fallback value based on the ID. By default
            `True`.

        Returns
        -------
        Layer
            The layer associated with this map rotation entry.

        Raises
        ------
        ValueError
            No layer information is known about this entry.

        """
        return Layer.by_id(self.id, strict=strict)


class GetMapRotationResponse(Response):
    maps: list[GetMapRotationResponseEntry] = Field(validation_alias="mAPS")


class GetServerSessionResponse(Response):
    server_name: str
    map_name: str
    game_mode_id: str = Field(validation_alias="gameMode")
    remaining_match_time: int
    match_time: int
    allied_score: int
    axis_score: int
    player_count: int
    allied_player_count: int
    axis_player_count: int
    max_player_count: int
    queue_count: int
    max_queue_count: int
    vip_queue_count: int
    max_vip_queue_count: int

    @property
    def game_mode(self) -> GameMode:
        return GameMode.by_id(self.game_mode_id)


class GetServerConfigResponse(Response):
    server_name: str
    build_number: str
    build_revision: str
    supported_platforms: list[SupportedPlatform]
    password_protected: bool


class GetBannedWordsResponse(Response):
    banned_words: list[str]


class GetCommandDetailsResponseComboParameter(Response):
    type: Literal["Combo"]
    """The type of parameter"""

    name: str
    """The user-friendly name of the parameter"""

    id: str = Field(validation_alias="iD")
    """The name of the parameter"""

    display_member: str
    """A comma-separated list of user-friendly values for this parameter. An empty
    string if `type` is not \"Combo\""""

    value_member: str
    """A comma-separated list of values for this parameter. An empty string if `type` is
    not \"Combo\""""


class GetCommandDetailsResponseTextParameter(Response):
    type: Literal["Text", "Number"]
    """The type of parameter"""

    name: str
    """The user-friendly name of the parameter"""

    id: str = Field(validation_alias="iD")
    """The name of the parameter"""

    display_member: Literal[""]
    """A comma-separated list of user-friendly values for this parameter. An empty
    string if `type` is not \"Combo\""""

    value_member: Literal[""]
    """A comma-separated list of values for this parameter. An empty string if `type` is
    not \"Combo\""""


GetCommandDetailsResponseParameter: TypeAlias = (
    GetCommandDetailsResponseComboParameter | GetCommandDetailsResponseTextParameter
)


class GetCommandDetailsResponse(Response):
    name: str
    """Name of the command"""

    text: str
    """User-friendly name of the command"""

    description: str
    """Description of the command"""

    dialogue_parameters: list[GetCommandDetailsResponseParameter]
    """A list of parameters for this command"""