import enum
from typing import TypedDict
from pydantic import Field, BaseModel
from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config


class VoteMapType(TypedDict):
    enabled: bool
    default_method: "DefaultMethods"
    number_last_played_to_exclude: int
    num_warfare_options: int
    num_offensive_options: int
    num_skirmish_control_options: int
    consider_offensive_same_map: bool
    consider_skirmishes_as_same_map: bool
    allow_consecutive_offensives: bool
    allow_consecutive_offensives_opposite_sides: bool
    allow_default_to_offensive: bool
    allow_consecutive_skirmishes: bool
    allow_default_to_skirmish: bool
    instruction_text: str
    thank_you_text: str
    no_vote_text: str
    reminder_frequency_minutes: int
    allow_opt_out: bool
    help_text: str
    vote_flags: list["VoteFlag"]
    vote_ban_flags: list[str]
    player_choice_flags: list[str]
    player_choice_help_text: str
    vip_vote_count: int
    remind_on_match_start: bool
    remind_on_match_end: bool


# Has to inherit from str to allow JSON serialization when
# pydantic dumps the model to a dict
class DefaultMethods(str, enum.Enum):
    least_played_suggestions = "least_played_from_suggestions"
    least_played_all_maps = "least_played_from_all_map"
    random_suggestions = "random_from_suggestions"
    random_all_maps = "random_from_all_maps"

class VoteFlag(BaseModel):
    flag: str = Field(
        description="A single-character flag", 
        min_length=1, 
    )
    vote_count: int = Field(
        ge=1,
        le=100,
        description="Number of votes (must be 0 or greater)"
    )

INSTRUCTION_TEXT = """Vote for the nextmap:
Type in the chat !votemap <map number>
{map_selection}

To never see this message again type in the chat !votemap never

To renable type: !votemap allow"""
THANK_YOU_TEXT = "Thanks {player_name}, vote registered for:\n{map_name}"
NO_VOTE_TEXT = "No votes recorded yet"
HELP_TEXT = """To vote you must type in the chat (press K to open the chat) !votemap followed by the number of the map you want (from 0 to N), you must write the number without the brackets
e.g. > !votemap 0

To display the maps and their numbers
> !votemap

To add map to the selection
> !votemap add

If you want to opt-out of the votemap reminder FOREVER
> !votemap never

To opt back in
> !votemap allow

To see this message again
> !votemap help"""

PLAYER_CHOICE_HELP_TEXT="""How to add your map?

Type in the chat:
> !vm add <map_tag> [game_mode] [attackers | only if game_mode=offensive] [environment]
e.g. > !vm add car offensive axis day

You can omit some [values].
Defaults: game_mode=warfare, environment=day, attackers=allies
e.g. > !vm add car -> Carentan Warfare"""


class VoteMapUserConfig(BaseUserConfig):
    enabled: bool = Field(default=False)
    default_method: DefaultMethods = Field(
        default=DefaultMethods.least_played_suggestions
    )
    number_last_played_to_exclude: int = Field(ge=0, default=3)
    num_warfare_options: int = Field(ge=0, default=4)
    num_offensive_options: int = Field(ge=0, default=2)
    num_skirmish_control_options: int = Field(ge=0, default=1)
    consider_offensive_same_map: bool = Field(default=True)
    consider_skirmishes_as_same_map: bool = Field(default=True)
    allow_consecutive_offensives: bool = Field(default=True)
    allow_consecutive_offensives_opposite_sides: bool = Field(default=False)
    allow_default_to_offensive: bool = Field(default=False)
    allow_consecutive_skirmishes: bool = Field(default=False)
    allow_default_to_skirmish: bool = Field(default=False)
    instruction_text: str = Field(default=INSTRUCTION_TEXT)
    thank_you_text: str = Field(default=THANK_YOU_TEXT)
    no_vote_text: str = Field(default=NO_VOTE_TEXT)
    reminder_frequency_minutes: int = Field(ge=0, default=20)
    allow_opt_out: bool = Field(default=True)
    help_text: str = Field(default=HELP_TEXT)
    vote_flags: list[VoteFlag] = Field(default_factory=list, title="Vote Flags", description="Players with a listed flag have their vote counted n times (use highest value if multiple flags or vip; 1 <= n <= 100).")
    vote_ban_flags: list[str] = Field(default_factory=list, title="Vote Ban Flags", description="Players having one of these flags are banned from voting.")
    player_choice_flags: list[str] = Field(default_factory=list, title="Player Choice Flags", description="Players having one of these flags are allowed to run `!vm add` commands. When no flags provided, everyone can run it.")
    player_choice_help_text: str = Field(default=PLAYER_CHOICE_HELP_TEXT)
    vip_vote_count: int = Field(default=1, ge=1, le=100, title="VIP Vote Counts", description="VIP Players have their vote counted n times (use highest value if multiple flags or vip; 1 <= n <= 100).")
    remind_on_match_start: bool = Field(default=False)
    remind_on_match_end: bool = Field(default=True)

    @staticmethod
    def save_to_db(values: VoteMapType, dry_run=False):
        key_check(
            VoteMapType.__required_keys__, VoteMapType.__optional_keys__, values.keys()
        )

        # model_fields = VoteMapUserConfig.model_fields.keys()
        # filtered_values = {k: v for k, v in values.items() if k in model_fields}
        # validated_conf = VoteMapUserConfig(**filtered_values) # type: ignore

        validated_conf = VoteMapUserConfig(
            enabled=values.get("enabled"),
            default_method=values.get("default_method"),
            num_warfare_options=values.get("num_warfare_options"),
            num_offensive_options=values.get("num_offensive_options"),
            num_skirmish_control_options=values.get("num_skirmish_control_options"),
            number_last_played_to_exclude=values.get("number_last_played_to_exclude"),
            consider_offensive_same_map=values.get("consider_offensive_same_map"),
            consider_skirmishes_as_same_map=values.get(
                "consider_skirmishes_as_same_map"
            ),
            allow_consecutive_offensives=values.get("allow_consecutive_offensives"),
            allow_consecutive_offensives_opposite_sides=values.get(
                "allow_consecutive_offensives_opposite_sides"
            ),
            allow_default_to_offensive=values.get("allow_default_to_offensive"),
            allow_consecutive_skirmishes=values.get("allow_consecutive_skirmishes"),
            allow_default_to_skirmish=values.get("allow_default_to_skirmish"),
            instruction_text=values.get("instruction_text"),
            thank_you_text=values.get("thank_you_text"),
            no_vote_text=values.get("no_vote_text"),
            reminder_frequency_minutes=values.get("reminder_frequency_minutes"),
            allow_opt_out=values.get("allow_opt_out"),
            help_text=values.get("help_text"),
            vote_flags=values.get("vote_flags"),
            vote_ban_flags=values.get("vote_ban_flags"),
            player_choice_flags=values.get("player_choice_flags"),
            player_choice_help_text=values.get("player_choice_help_text"),
            vip_vote_count=values.get("vip_vote_count"),
            remind_on_match_start=values.get("remind_on_match_start"),
            remind_on_match_end=values.get("remind_on_match_end"),
        )

        if not dry_run:
            set_user_config(VoteMapUserConfig.KEY(), validated_conf)
