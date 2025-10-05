import asyncio
import math
import os
import random
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from logging import getLogger
from typing import TypedDict

import httpx
import orjson
import pydantic
import redis
from discord_webhook import AsyncDiscordWebhook, DiscordWebhookDict
from pydantic import BaseModel, Field

import redis.exceptions
from rcon.cache_utils import construct_redis_url, get_redis_client
from rcon.utils import get_server_number

logger = getLogger(__name__)


class WebhookType(StrEnum):
    """The type of service the webhook is for (discord, etc.)"""

    DISCORD = "discord"


class DiscordErrorResponse(TypedDict):
    """Discord will return 401 for invalid webhook IDs; 403 for invalid tokens"""

    http_401: bool
    http_403: bool
    http_404: bool


class WebhookMessageType(StrEnum):
    """The underlying type a webhook message is for (log, audit, scoreboard, etc.)

    This allows us to selectively remove messages from a queue
    """

    # TODO: Add the other log types in a more general fashion
    LOG_LINE = "log_line"
    LOG_LINE_CHAT = "log_line_chat"
    LOG_LINE_KILL = "log_line_kill"
    LOG_LINE_TEAMKILL = "log_line_teamkill"
    ADMIN_PING = "admin_ping"
    SCOREBOARD = "scoreboard"
    AUDIT = "audit"
    OTHER = "other"


class QueueStatus(TypedDict):
    """Overview of a message queue"""

    webhook_id: str
    length: int
    errors: DiscordErrorResponse
    window_rate_limits: int
    redis_key: str


class WebhookMessage(BaseModel):
    """Format for enqueing messages into Redis for the webhook service"""

    server_number: int = Field(description="The server that generated this message")
    discardable: bool = Field(
        default=False,
        description="Use for messages that don't need to be retried (scorebot, etc)",
    )
    edit: bool = Field(
        default=False,
        description="Edit an existing message; the ID field must already be set in the payload",
    )

    sent_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
        description="The original UTC time the message was attempted to be sent",
    )
    retry_attempts: int = Field(
        default=0,
        ge=0,
        description="The number of retry attempts if the message was rate limited",
    )
    payload_type: None = Field(
        default=None,
        description="For future use for bundling similar types of messages",
    )

    # TODO: support other types of webhooks in the future
    webhook_type: WebhookType = Field(description="The type of webhook (discord, etc.)")
    message_type: WebhookMessageType = Field()

    payload: DiscordWebhookDict = Field(
        description="The parameters that will be used to construct the webhook of appropriate type by the service"
    )


def enqueue_transient_message(
    message: WebhookMessage,
    message_group_key: str,
    red: redis.StrictRedis | None = None,
    key: str = "discord_webhook_transient:channel",
):
    """Accept a WebhookMessage and message_group_key to only store the most recent update

    This method should only be used for types of messages that are transient
    and impermanent; such as a Scoreboard message update. These messages are
    not stored as a queue; enqueueing future messages will overwrite any past ones
    use `enqueue_message` for messages that should be stored in a queue so they are
    # all (attempted but not guaranteed) to be sent to the remote service (Discord, etc.)
    """
    logger.debug("Enqueuing %s: %s", message_group_key, message)

    # Allows easier usage for enqueing from different services/sections of CRCON
    if red is None:
        url = construct_redis_url(db_number=0)
        red = get_redis_client(redis_url=url, decode_responses=False, global_pool=True)
    red.publish(key, message.model_dump_json())


def enqueue_message(
    message: WebhookMessage,
    red: redis.StrictRedis | None = None,
    key: str = "discord_webhook_queue:input",
):
    """Accept a WebhookMessage and insert it in Redis

    The webhook service will route it to the appropriate queue after determining
    the rate limit bucket
    """
    logger.debug("Enqueuing %s", message)

    # Allows easier usage for enqueing from different services/sections of CRCON
    if red is None:
        url = construct_redis_url(db_number=0)
        red = get_redis_client(redis_url=url, decode_responses=False, global_pool=True)

    if not isinstance(message, WebhookMessage):
        raise ValueError(f"{message} must be a WebhookMessage instance")
    red.rpush(key, orjson.dumps(message.model_dump_json()))
    # Keep our queue from growing unbounded in case the service is down
    # but without having to force users to update their compose files to
    # pass in the actual value; if someone's desired queue size is this large
    # they should know what they're doing and can come fix this on their own build
    red.ltrim(key, 0, 1000)


def get_message_edit_404_failure(
    message_id: str,
    red: redis.StrictRedis | None = None,
    prefix: str = "discord_webhook:message_404",
) -> bool:
    """Check if a specific message ID received an HTTP 404 error from Discord"""
    # Allows easier usage for enqueing from different services/sections of CRCON
    if red is None:
        url = construct_redis_url(db_number=0)
        red = get_redis_client(redis_url=url, decode_responses=False, global_pool=True)
    return red.get(f"{prefix}:{message_id}") == b"1"


def count_bucket_rate_limits(
    red: redis.StrictRedis,
    bucket_id: str,
    hash_name: str = "discord_webhook_bucket_rl_count",
) -> int:
    """The rate limit bucket hash length; the number of times it was rate limited in the window"""
    hash_name = f"{hash_name}:{bucket_id}"
    return red.hlen(hash_name)  # type: ignore


def get_webhook_error(
    red: redis.StrictRedis,
    webhook_id: str,
    webhook_type: WebhookType,
    prefix: str = "discord_webhook_queue:webhook_id_errors",
) -> DiscordErrorResponse:
    """Retrieve the current webhook error response for a webhook"""
    # TODO: likely have to tweak this when we support other webhook types in the future
    key = f"{prefix}:{webhook_type}:{webhook_id}"
    raw: dict[bytes, int] = red.hgetall(key)  # type: ignore
    values: DiscordErrorResponse = {
        "http_401": True if raw.get(b"http_401") == b"1" else False,
        "http_403": True if raw.get(b"http_403") == b"1" else False,
        "http_404": True if raw.get(b"http_404") == b"1" else False,
    }
    return values


def get_webhook_rl_buckets(
    red: redis.StrictRedis | None, bucket_hash: str = "discord_webhook:webhook_buckets"
) -> dict[str, str]:
    if red is None:
        red = get_redis_client(decode_responses=False, global_pool=True)

    # webhookID : bucketID
    bucket_ids = red.hgetall(bucket_hash)
    return {k.decode(): v.decode() for k, v in bucket_ids.items()}


def get_queue_keys(
    red: redis.StrictRedis | None = None,
    prefix: str = "discord_webhook_queue:bucket",
) -> list[str]:
    """Return all the queue keys from Redis (queues are by rl bucket)"""
    logger.debug("Getting all queue IDs from %s", prefix)
    if red is None:
        red = get_redis_client(decode_responses=False, global_pool=True)

    # webhookID : bucketID
    bucket_ids = get_webhook_rl_buckets(red)
    # The fully formed queue ID by RL bucket
    queue_keys: list[str] = [f"{prefix}:{value}" for value in set(bucket_ids.values())]
    return queue_keys


def get_webhook_ids(red: redis.StrictRedis | None) -> list[str]:
    """Return all the webhook IDs stored in Redis"""
    if red is None:
        red = get_redis_client(decode_responses=False, global_pool=True)
    # webhookID : bucketID
    bucket_ids = get_webhook_rl_buckets(red)
    return [key for key in bucket_ids.keys()]


def get_queue_length(queue_id: str, red: redis.StrictRedis | None = None) -> int:
    """Return a summary of a queue if it exists"""
    if red is None:
        red = get_redis_client(decode_responses=False, global_pool=True)

    length: int = red.llen(queue_id)  # type: ignore
    return length


def get_webhook_queue_overview(
    queue_key: str,
    rl_bucket_to_webhook_id: dict[str, str] | None = None,
    red: redis.StrictRedis | None = None,
) -> QueueStatus:
    if red is None:
        red = get_redis_client(decode_responses=False, global_pool=True)

    if rl_bucket_to_webhook_id is None:
        rl_bucket_to_webhook_id = get_webhook_rl_buckets(red)
    _, _, rl_bucket = queue_key.split(":")
    length = get_queue_length(queue_key, red)
    webhook_id = rl_bucket_to_webhook_id[rl_bucket]
    errors = get_webhook_error(red, webhook_id, WebhookType.DISCORD)

    return {
        "webhook_id": webhook_id,
        "length": length,
        "errors": errors,
        "window_rate_limits": count_bucket_rate_limits(red, rl_bucket),
        "redis_key": queue_key,
    }


def webhook_service_summary(red: redis.StrictRedis | None = None):
    """Return a queue overview for all queues"""
    if red is None:
        red = get_redis_client(decode_responses=False, global_pool=True)

    data = {}
    data["is_globally_rate_limited"] = is_globally_rate_limited(red=red)
    data["global_rate_limit_reset_after"] = get_global_rate_limit_reset_after(red=red)

    data["input_queue"] = {
        "length": get_queue_length("discord_webhook_queue:input", red),
        "redis_key": "discord_webhook_queue:input",
    }

    data["first_time_queue"] = {
        "length": get_queue_length("discord_webhook_queue:first_time", red),
        "redis_key": "discord_webhook_queue:first_time",
    }

    data["queues"] = list()
    bucket_ids = get_webhook_rl_buckets(red)
    rl_bucket_to_webhook_id = {v: k for k, v in bucket_ids.items()}
    queue_keys = get_queue_keys(red)
    logger.info(f"{queue_keys=}")
    for qkey in queue_keys:
        data["queues"].append(
            get_webhook_queue_overview(qkey, rl_bucket_to_webhook_id, red)
        )

    return data


def reset_webhook_queues(red: redis.StrictRedis | None = None) -> int:
    """Delete each queue; unprocessed messages may be lost depending on timing"""
    if red is None:
        red = get_redis_client(decode_responses=False, global_pool=True)

    keys = get_queue_keys(red=red)
    return red.delete(*keys)  # type: ignore


def reset_queue(queue_id: str, red: redis.StrictRedis | None = None) -> bool:
    """Delete the specified queue; returning if it deleted any entries"""
    if red is None:
        red = get_redis_client(decode_responses=False, global_pool=True)

    # TODO: this could cause conflicts in the future if we start supporting other webhooks
    # than just discord; it's possible but unlikely that their queue IDs could conflict
    # we could use the entire redis key instead of just the component pieces
    return red.delete(queue_id) != 0  # type: ignore


def is_globally_rate_limited(red: redis.StrictRedis) -> bool:
    """Check Redis to determine if we are globally rate limited"""
    limit = get_global_rate_limit_reset_after(red=red)

    return limit is not None


def get_global_rate_limit_reset_after(
    red: redis.StrictRedis, key: str = "discord_webhook:global_rate_limited"
) -> datetime | None:
    """Return the datetime the global rate limit expires at if any"""
    limit: datetime | None = None

    try:
        raw: bytes = red.get(key)  # type: ignore
        limit = datetime.fromtimestamp(float(raw.decode()))
    except (AttributeError, TypeError) as e:
        logger.debug("Unable to parse the global rate limit reset after time: %s", e)

    return limit
