from datetime import timedelta
from logging import getLogger
from typing import TypedDict

import pydantic
from pydantic import Field

import discord

logger = getLogger(__name__)

from rcon.user_config.utils import BaseUserConfig, _listType, key_check, set_user_config
from rcon.user_config.webhooks import DiscordWebhook, WebhookType

SEEDING_IN_PROGRESS_MESSAGE = "Server has reached {player_count} players"
SEEDING_COMPLETE_MESSAGE = "Server is live!"
PLAYER_COUNT_MESSAGE = "{num_allied_players} - {num_axis_players}"
REWARD_PLAYER_MESSAGE = "Thank you for helping us seed.\n\nYou've been granted {vip_reward} of VIP\n\nYour VIP currently expires: {vip_expiration}"
REWARD_PLAYER_MESSAGE_NO_VIP = "Thank you for helping us seed.\n\nThe server is now live and the regular rules apply."

PLAYER_NAME_FORMAT_NOT_CURRENT_VIP = "{player_name} - CRCON Seed VIP"


class RawBufferType(TypedDict):
    seconds: int
    minutes: int
    hours: int


class RawMinPlayTimeType(TypedDict):
    seconds: int
    minutes: int
    hours: int


class RawRequirementsType(TypedDict):
    buffer: RawBufferType
    min_allies: int
    min_axis: int
    max_allies: int
    max_axis: int
    online_when_seeded: bool
    minimum_play_time: RawMinPlayTimeType


class RawRewardTimeFrameType(TypedDict):
    minutes: int
    hours: int
    days: int
    weeks: int


class RawRewardType(TypedDict):
    forward: bool
    player_name_format_not_current_vip: str
    cumulative: bool
    timeframe: RawRewardTimeFrameType


class RawPlayerMessagesType(TypedDict):
    seeding_in_progress_message: str
    seeding_complete_message: str
    player_count_message: str
    reward_player_message: str
    reward_player_message_no_vip: str


class SeedVIPType(TypedDict):
    enabled: bool
    dry_run: bool
    language: str
    hooks: list[WebhookType]
    player_announce_thresholds: list[int]
    poll_time_seeding: int
    poll_time_seeded: int
    requirements: RawRequirementsType
    nice_time_delta: bool
    nice_expiration_date: bool
    player_messages: RawPlayerMessagesType
    reward: RawRewardType


class BufferType(pydantic.BaseModel):
    seconds: int = Field(default=0, ge=0)
    minutes: int = Field(default=10, ge=0)
    hours: int = Field(default=0, ge=0)

    @property
    def as_timedelta(self):
        return timedelta(
            seconds=self.seconds,
            minutes=self.minutes,
            hours=self.hours,
        )


class MinPlayTime(pydantic.BaseModel):
    seconds: int = Field(default=0, ge=0)
    minutes: int = Field(default=5, ge=0)
    hours: int = Field(default=0, ge=0)

    @property
    def total_seconds(self):
        return int(
            timedelta(
                seconds=self.seconds, minutes=self.minutes, hours=self.hours
            ).total_seconds()
        )


class Requirements(pydantic.BaseModel):
    buffer: BufferType = Field(default_factory=BufferType)
    min_allies: int = Field(default=0, ge=0, le=50)
    min_axis: int = Field(default=0, ge=0, le=50)
    max_allies: int = Field(default=20, ge=0, le=50)
    max_axis: int = Field(default=20, ge=0, le=50)
    online_when_seeded: bool = Field(default=True)
    minimum_play_time: MinPlayTime = Field(default_factory=MinPlayTime)


class PlayerMessages(pydantic.BaseModel):
    seeding_in_progress_message: str = Field(default=SEEDING_IN_PROGRESS_MESSAGE)
    seeding_complete_message: str = Field(default=SEEDING_COMPLETE_MESSAGE)
    player_count_message: str = Field(default=PLAYER_COUNT_MESSAGE)
    reward_player_message: str = Field(default=REWARD_PLAYER_MESSAGE)
    reward_player_message_no_vip: str = Field(default=REWARD_PLAYER_MESSAGE_NO_VIP)


class RewardTimeFrame(pydantic.BaseModel):
    minutes: int = Field(default=0, ge=0)
    hours: int = Field(default=0, ge=0)
    days: int = Field(default=1, ge=0)
    weeks: int = Field(default=0, ge=0)

    @property
    def as_timedelta(self):
        return timedelta(
            minutes=self.minutes, hours=self.hours, days=self.days, weeks=self.weeks
        )

    @property
    def total_seconds(self):
        return int(self.as_timedelta.total_seconds())


class Reward(pydantic.BaseModel):
    forward: bool = Field(default=False)
    player_name_format_not_current_vip: str = Field(
        default=PLAYER_NAME_FORMAT_NOT_CURRENT_VIP
    )
    cumulative: bool = Field(default=True)
    timeframe: RewardTimeFrame = Field(default_factory=RewardTimeFrame)


class SeedVIPUserConfig(BaseUserConfig):
    enabled: bool = Field(default=False)
    dry_run: bool = Field(default=True)
    language: str | None = Field(default="en_US")
    hooks: list[DiscordWebhook] = Field(default_factory=list)
    player_announce_thresholds: list[int] = Field(default=[10, 20, 30])
    poll_time_seeding: int = Field(default=30, ge=0)
    poll_time_seeded: int = Field(default=300, ge=0)
    nice_time_delta: bool = Field(default=True)
    nice_expiration_date: bool = Field(default=True)
    requirements: Requirements = Field(default_factory=Requirements)
    player_messages: PlayerMessages = Field(default_factory=PlayerMessages)
    reward: Reward = Field(default_factory=Reward)

    @staticmethod
    def save_to_db(values: SeedVIPType, dry_run=False):
        # logger.info(f"{values=}")
        key_check(SeedVIPType.__required_keys__, values.keys())
        logger.info(f"after key_check")

        raw_hooks: list[WebhookType] = values.get("hooks")
        _listType(values=raw_hooks)

        logger.info(f"after listType check")
        for obj in raw_hooks:
            key_check(WebhookType.__required_keys__, obj.keys())

        logger.info(f"after key_check for webhooks")
        validated_hooks = [DiscordWebhook(url=obj.get("url")) for obj in raw_hooks]

        logger.info(f"after hooks validated")
        raw_player_messages = values.get("player_messages")
        raw_requirements = values.get("requirements")
        raw_buffer = raw_requirements.get("buffer")
        raw_min_play_time = raw_requirements.get("minimum_play_time")
        raw_reward = values.get("reward")
        raw_reward_time_frame = raw_reward.get("timeframe")

        validated_player_messages = PlayerMessages(
            seeding_in_progress_message=raw_player_messages.get(
                "seeding_in_progress_message"
            ),
            seeding_complete_message=raw_player_messages.get(
                "seeding_complete_message"
            ),
            player_count_message=raw_player_messages.get("player_count_message"),
            reward_player_message=raw_player_messages.get("reward_player_message"),
            reward_player_message_no_vip=raw_player_messages.get(
                "reward_player_message_no_vip"
            ),
        )

        validated_requirements = Requirements(
            buffer=BufferType(
                seconds=raw_buffer.get("seconds"),
                minutes=raw_buffer.get("minutes"),
                hours=raw_buffer.get("hours"),
            ),
            min_allies=raw_requirements.get("min_allies"),
            max_allies=raw_requirements.get("max_allies"),
            min_axis=raw_requirements.get("min_axis"),
            max_axis=raw_requirements.get("max_axis"),
            online_when_seeded=raw_requirements.get("online_when_seeded"),
            minimum_play_time=MinPlayTime(
                seconds=raw_min_play_time.get("seconds"),
                minutes=raw_min_play_time.get("minutes"),
                hours=raw_min_play_time.get("hours"),
            ),
        )

        validated_reward_time_frame = RewardTimeFrame(
            minutes=raw_reward_time_frame.get("minutes"),
            hours=raw_reward_time_frame.get("hours"),
            days=raw_reward_time_frame.get("days"),
            weeks=raw_reward_time_frame.get("weeks"),
        )

        validated_reward = Reward(
            forward=raw_reward.get("forward"),
            player_name_format_not_current_vip=raw_reward.get(
                "player_name_format_not_current_vip"
            ),
            cumulative=raw_reward.get("cumulative"),
            timeframe=validated_reward_time_frame,
        )

        validated_conf = SeedVIPUserConfig(
            enabled=values.get("enabled"),
            dry_run=values.get("dry_run"),
            language=values.get("language"),
            hooks=validated_hooks,
            player_announce_thresholds=values.get("player_announce_thresholds"),
            poll_time_seeding=values.get("poll_time_seeding"),
            poll_time_seeded=values.get("poll_time_seeded"),
            nice_time_delta=values.get("nice_time_delta"),
            nice_expiration_date=values.get("nice_expiration_date"),
            requirements=validated_requirements,
            player_messages=validated_player_messages,
            reward=validated_reward,
        )

        if not dry_run:
            logger.info(f"setting {validated_conf=}")
            set_user_config(SeedVIPUserConfig.KEY(), validated_conf)
