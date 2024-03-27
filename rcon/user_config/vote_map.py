import enum
from typing import TypedDict

from pydantic import Field

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
    thank_you_text: str | None
    no_vote_text: str
    reminder_frequency_minutes: int
    allow_opt_out: bool
    help_text: str | None


# Has to inherit from str to allow JSON serialization when
# pydantic dumps the model to a dict
class DefaultMethods(str, enum.Enum):
    least_played_suggestions = "least_played_from_suggestions"
    least_played_all_maps = "least_played_from_all_map"
    random_suggestions = "random_from_suggestions"
    random_all_maps = "random_from_all_maps"


INSTRUCTION_TEXT = """Vote for the nextmap:
Type in the chat !votemap <map number>
{map_selection}

To never see this message again type in the chat !votemap never

To renable type: !votemap allow"""
THANK_YOU_TEXT = "Thanks {player_name}, vote registered for:\n{map_name}"
NO_VOTE_TEXT = "No votes recorded yet"
HELP_TEXT = """To vote you must type in the chat (press K to open the chat) !votemap followed by the number of the map you want (from 0 to N), you must write the number without the brackets, e.g.: !votemap 0

The map numbers appear in the reminder message you get once in a while or if you type !votemap without a number.

If you want to opt-out of the votemap reminder FOREVER type !votemap never

To opt back in again type !votemap allow

To see the select type !votemap

To see this message again type !votemap help"""


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
    thank_you_text: str | None = Field(default=THANK_YOU_TEXT)
    no_vote_text: str = Field(default=NO_VOTE_TEXT)
    reminder_frequency_minutes: int = Field(ge=0, default=20)
    allow_opt_out: bool = Field(default=True)
    help_text: str | None = Field(default="")

    @staticmethod
    def save_to_db(values: VoteMapType, dry_run=False):
        key_check(VoteMapType.__required_keys__, values.keys())

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
        )

        if not dry_run:
            set_user_config(VoteMapUserConfig.KEY(), validated_conf.model_dump())
