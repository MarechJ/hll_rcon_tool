from typing import Optional, TypedDict
from pydantic import Field
from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config
from rcon.user_config.webhooks import DiscordMentionWebhook, WebhookMentionType


class WatchKillRateType(TypedDict):
    match_start_cooldown_secs: int
    watch_interval_secs: int
    report_cooldown_mins: int
    min_kills: int
    killrate_threshold: float
    killrate_threshold_armor: float
    killrate_threshold_artillery: float
    killrate_threshold_mg: float
    only_report_once_per_match: bool
    whitelist_flags: list[str]
    whitelist_armor: bool
    whitelist_artillery: bool
    whitelist_mg: bool
    author: str
    webhooks: list[WebhookMentionType]


class WatchKillRateUserConfig(BaseUserConfig):
    match_start_cooldown_secs: int = Field(default=180, ge=0)
    watch_interval_secs: int = Field(default=60, ge=2)
    report_cooldown_mins: int = Field(default=15, ge=1)
    min_kills: int = Field(default=25)
    killrate_threshold: float = Field(default=1.25)
    killrate_threshold_armor: float = Field(default=2.0)
    killrate_threshold_artillery: float = Field(default=3.0)
    killrate_threshold_mg: float = Field(default=1.5)
    only_report_once_per_match: bool = Field(default=True)
    whitelist_flags: list[str] = Field(default_factory=list)
    whitelist_armor: bool = Field(default=True)
    whitelist_artillery: bool = Field(default=True)
    whitelist_mg: bool = Field(default=True)
    author: str = Field(default="CRCON Watch KillRate")
    webhooks: list[DiscordMentionWebhook] = Field(default_factory=list)

    @staticmethod
    def save_to_db(values: WatchKillRateType, dry_run=False):
        key_check(
            WatchKillRateType.__required_keys__,
            WatchKillRateType.__optional_keys__,
            values.keys(),
        )

        raw_webhooks = values.get("webhooks")
        validated_webhooks: list[DiscordMentionWebhook] = []
        for hook in raw_webhooks:
            validated_webhooks.append(
                DiscordMentionWebhook(
                    url=hook.get("url"),
                    user_mentions=hook.get("user_mentions"),
                    role_mentions=hook.get("role_mentions"),
                )
            )

        validated_conf = WatchKillRateUserConfig(
            match_start_cooldown_secs=values.get("match_start_cooldown_secs"),
            watch_interval_secs=values.get("watch_interval_secs"),
            report_cooldown_mins=values.get("report_cooldown_mins"),
            min_kills=values.get("min_kills"),
            killrate_threshold=values.get("killrate_threshold"),
            killrate_threshold_armor=values.get("killrate_threshold_armor"),
            killrate_threshold_artillery=values.get("killrate_threshold_artillery"),
            killrate_threshold_mg=values.get("killrate_threshold_mg"),
            only_report_once_per_match=values.get("only_report_once_per_match"),
            whitelist_flags=values.get("whitelist_flags"),
            whitelist_armor=values.get("whitelist_armor"),
            whitelist_artillery=values.get("whitelist_artillery"),
            whitelist_mg=values.get("whitelist_mg"),
            author=values.get("author"),
            webhooks=validated_webhooks,
        )

        if not dry_run:
            set_user_config(WatchKillRateUserConfig.KEY(), validated_conf)
