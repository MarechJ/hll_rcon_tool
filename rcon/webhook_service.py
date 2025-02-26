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

# TODO: we can't expire redis list items; but we could maybe use
# a sorted set in the future so we can expire individual items
# to prevent indefinite growth without a max length,
# right now the lists are trimmed
# when adding new elements to prevent indefinite growth

# TODO: Support editing existing messages; this can only add
# new ones, so we can't use it for scorebot yet

SCOREBOARD = "scoreboard"
SCOREBOARD_BYTES = b"scoreboard"

PREFIX = "whs"
BUCKET_ID = f"{PREFIX}"
WH_ID_TO_RATE_LIMIT_BUCKET = f"{PREFIX}:wh_id_rl_bucket"
BUCKET_RL = f"{PREFIX}:rl"
BUCKET_RL_COUNT = f"{BUCKET_RL}:count"

GLOBAL_RATE_LIMIT = f"{PREFIX}:global_rl"
GLOBAL_RATE_LIMIT_RESET_AFTER = f"{GLOBAL_RATE_LIMIT}:reset_after"
# Track HTTP 401/403 errors by webhook ID
WEBHOOK_ERRORS = f"{PREFIX}:errors"

# Track failed message (HTTP 404 errors) by message ID
MESSAGE_DOES_NOT_EXIST = f"{PREFIX}:message_404"

DEFAULT_GLOBAL_RETRY_AFTER_SECS = 5 * 60

# Discord response headers
X_RATELIMIT_BUCKET = "x-ratelimit-bucket"
X_RATELIMIT_REMAINING = "x-ratelimit-remaining"
X_RATELIMIT_LIMIT = "x-ratelimit-limit"
X_RATELIMIT_RESET = "x-ratelimit-reset"
X_RATELIMIT_RESET_AFTER = "x-ratelimit-reset-after"


# Allow users to tune their local rate limit window if they really want to
try:
    LOCAL_RL_RESET_AFTER = int(os.getenv("HLL_WH_SERVICE_RL_RESET_SECS"))
except (ValueError, TypeError):
    LOCAL_RL_RESET_AFTER = 3

try:
    LOCAL_RL_REQUESTS_PER = int(os.getenv("HLL_WH_SERVICE_RL_REQUESTS_PER", 5))
except (ValueError, TypeError):
    LOCAL_RL_REQUESTS_PER = 5

# Tracks the number of rate limited requests in the last N seconds
try:
    BUCKET_RL_COUNT_RESET_SECS = int(os.getenv("HLL_WH_SERVICE_RL_RESET_SECS"))
except (ValueError, TypeError):
    BUCKET_RL_COUNT_RESET_SECS = 60 * 10


# We trim the queues (redis list) after adding messages so we don't exceed this length
# which is unlikely to happen in normal circumstances except the kill feed if turned on
# which will rapidly accumulate messages faster than we can send them to Discord
# If we trim from the left; we lose messages that we're retrying but are older, if we
# trim from the right; we lose newer messages
# We choose to trim from the left in the interest of losing older (less relevant?) messages
try:
    WH_MAX_QUEUE_LENGTH = int(os.getenv("HLL_WH_MAX_QUEUE_LENGTH"))
except (ValueError, TypeError):
    WH_MAX_QUEUE_LENGTH = 150

# Global datastructures to support associating hooks with locks
_RATE_LIMIT_BUCKETS: defaultdict[str, asyncio.Lock | None] = defaultdict(lambda: None)
_SHARED_LOCK: asyncio.Lock | None = None


def set_message_edit_404_failure(
    red: redis.StrictRedis,
    message_id: str,
    prefix: str = MESSAGE_DOES_NOT_EXIST,
    value: bool = True,
    ttl=120,
) -> None:
    """Set a flag in redis for a message ID to communicate back to a sender that the message does not exist"""
    red.set(f"{prefix}:{message_id}", b"1" if value else b"0", ex=ttl)


def get_message_edit_404_failure(
    message_id: str,
    red: redis.StrictRedis | None = None,
    prefix: str = MESSAGE_DOES_NOT_EXIST,
) -> bool:
    """Check if a specific message ID received an HTTP 404 error from Discord"""
    # Allows easier usage for enqueing from different services/sections of CRCON
    if red is None:
        url = construct_redis_url(db_number=0)
        red = get_redis_client(redis_url=url, decode_responses=False, global_pool=True)
    return red.get(f"{prefix}:{message_id}") == b"1"


def clear_queue_by_message_id(red: redis.StrictRedis, queue_id: str, message_id: str):
    """Delete all messages from a queue that have message_id

    This allows us to remove all queued edits to a message ID that no longer exists
    """

    # Traverse the list and identify all the values that contain message_id
    # and then LREM them
    for raw_message in red.lrange(queue_id, 0, -1):
        message = unpack_message(raw_message=raw_message)
        if message_id == message.payload["message_id"]:
            red.lrem(queue_id, 0, raw_message)


def get_shared_lock() -> asyncio.Lock:
    """Singleton instance for our shared lock that is used before a rate limit bucket is determined"""
    global _SHARED_LOCK
    if _SHARED_LOCK is None:
        _SHARED_LOCK = asyncio.Lock()
        logger.debug("Creating shared lock %s", _SHARED_LOCK)

    return _SHARED_LOCK


class WebhookType(StrEnum):
    """The type of service the webhook is for (discord, etc.)"""

    DISCORD = "discord"


class DiscordErrorResponse(TypedDict):
    """Discord will return 401 for invalid webhook IDs; 403 for invalid tokens"""

    http_401: bool
    http_403: bool
    http_404: bool


class WebhookMessageType(StrEnum):
    """The underlying type a webhook message is for (log, audit, scorebot, etc.)

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


@dataclass
class QueueParts:
    """The individual components of a queue ID key"""

    prefix: str
    server_number: str
    wh_type: WebhookType
    msg_type: WebhookMessageType
    id: str


@dataclass
class ScoreboardQueueParts:
    """The individual components of a scoreboard key"""

    prefix: str
    server_number: str
    wh_type: WebhookType
    msg_type: WebhookMessageType
    id: str
    message_key: str


class QueueStatus(TypedDict):
    """Overview of a message queue"""

    server_number: int
    id: str
    webhook_type: WebhookType
    message_type: WebhookMessageType
    length: int
    rate_limit_bucket: str | None
    rate_limited: bool
    redis_key: str


class ScoreboardMessageStatus(TypedDict):
    """Overview of a scoreboard message"""

    server_number: int
    id: str
    webhook_type: WebhookType
    message_type: WebhookMessageType
    rate_limit_bucket: str | None
    rate_limited: bool
    message_key: str
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


class DiscordRateLimitData(BaseModel):
    """Discord rate limit header data"""

    webhook_type: WebhookType | None = Field(default=None)
    id: str | None = Field(default=None)
    remaining_requests: int | None = Field(default=None)
    reset_after_secs: int | None = Field(default=None)
    reset_timestamp: int | None = Field(default=None)
    rate_limited: bool = Field(default=False)


def update_bucket_rate_limit(
    red: redis.StrictRedis,
    bucket_id: str,
    webhook_type: WebhookType,
    prefix: str = BUCKET_RL_COUNT,
    reset_seconds: int = BUCKET_RL_COUNT_RESET_SECS,
):
    """If a bucket is rate limited; set a key in a Redis hash that will expire

    This allows us to easily track the number of rate limits in the last N seconds
    by simply counting the number of entries in the hash
    """
    hash_name = f"{prefix}:{webhook_type}:{bucket_id}"
    # We can set this to whatever; we're just counting the number of hash entries
    # but using the timestamp should make it unique
    key = str(datetime.now().timestamp())
    value = "1"
    red.hset(hash_name, key, value)
    red.hexpire(hash_name, reset_seconds, key)


def count_bucket_rate_limits(
    red: redis.StrictRedis, bucket_id: str, prefix: str = BUCKET_RL_COUNT
) -> int:
    """The rate limit bucket hash length; the number of times it was rate limited in the window"""
    hash_name = f"{prefix}:{bucket_id}"
    return red.hlen(hash_name)  # type: ignore


def is_bucket_local_rate_limited(
    red: redis.StrictRedis,
    bucket_id: str,
    webhook_type: WebhookType | None,
    seconds: int = LOCAL_RL_RESET_AFTER,
    requests_per: int = LOCAL_RL_REQUESTS_PER,
    prefix: str = BUCKET_RL,
) -> bool:
    """Track our local rate limit (fixed window) per bucket to reduce external rate limiting

    This uses a fixed window rate limit algorithm
    """
    key = f"{prefix}:{webhook_type}:{bucket_id}"
    limited: bool = True
    try:
        res: bytes = red.get(key)  # type: ignore
        value = int(res.decode())
    except (TypeError, AttributeError):
        value = 0

    if value < requests_per:
        pipe = red.pipeline()
        limited = False
        pipe.incr(key)
        pipe.expire(key, seconds)
        pipe.execute()

    return limited


def is_globally_rate_limited(red: redis.StrictRedis) -> bool:
    """Check Redis to determine if we are globally rate limited"""
    limit = get_global_rate_limit_reset_after(red=red)

    return limit is not None


def get_global_rate_limit_reset_after(red: redis.StrictRedis) -> datetime | None:
    """Return the datetime the global rate limit expires at if any"""
    limit: datetime | None = None

    try:
        raw: bytes = red.get(GLOBAL_RATE_LIMIT_RESET_AFTER)  # type: ignore
        limit = datetime.fromtimestamp(float(raw.decode()))
    except (AttributeError, TypeError) as e:
        logger.debug("Unable to parse the global rate limit reset after time: %s", e)

    return limit


def set_global_rate_limit_reset_after(red: redis.StrictRedis, limit: float) -> None:
    """Set the timestamp the global rate limit expires in Redis"""
    seconds = limit - datetime.now().timestamp()
    if seconds > 0:
        pipe = red.pipeline()
        pipe.set(GLOBAL_RATE_LIMIT_RESET_AFTER, limit)
        pipe.expire(GLOBAL_RATE_LIMIT_RESET_AFTER, time=int(seconds))
        pipe.execute()


def get_webhook_rate_limit_bucket(
    red: redis.StrictRedis,
    queue_id: str,
    hash_name: str = WH_ID_TO_RATE_LIMIT_BUCKET,
) -> str | None:
    """Get the Discord rate limit bucket a webhook is associated with"""
    # There is a very low but non 0 chance of colliding on queue IDs
    # between services once we expand to support other webhook types than Discord
    # but for now to simplify the service without having to pass in details
    # of the message that we don't know when we GET it, skip the webhook type
    res: bytes = red.hget(hash_name, f"{queue_id}")  # type: ignore
    return res.decode()


def set_webhook_rate_limit_bucket(
    red: redis.StrictRedis,
    bucket_id: str,
    queue_id: str,
    hash_name: str = WH_ID_TO_RATE_LIMIT_BUCKET,
) -> None:
    """Associate a queue ID with its rate limit bucket"""
    logger.debug("Setting %s to %s", queue_id, bucket_id)
    red.hset(hash_name, queue_id, bucket_id)


def get_rate_limit_bucket_data(
    red: redis.StrictRedis, bucket_id: str, prefix: str = BUCKET_ID
) -> DiscordRateLimitData:
    """Return the data for a specific rate limit bucket"""
    name = f"{prefix}:{bucket_id}"
    raw_value = red.get(name)
    if raw_value is None:
        return DiscordRateLimitData()
    else:
        return DiscordRateLimitData.model_validate_json(orjson.loads(raw_value))  # type: ignore


def set_rate_limit_bucket_data(
    red: redis.StrictRedis, bucket: DiscordRateLimitData, prefix: str = BUCKET_ID
) -> None:
    """Set the data for a specific rate limit bucket"""
    # There is a very low but non 0 chance of colliding on rate limit bucket IDs
    # between services once we expand to support other webhook types than Discord
    # but for now to simplify the service without having to pass in details
    # of the message that we don't know when we GET it, skip the webhook type
    name = f"{prefix}:{bucket.id}"
    red.set(name, orjson.dumps(bucket.model_dump_json()))


def get_bucket_lock(
    red: redis.StrictRedis,
    bucket_id: str,
) -> tuple[DiscordRateLimitData, asyncio.Lock | None]:
    """Get the lock for a rate limit bucket"""
    bucket_data = get_rate_limit_bucket_data(red=red, bucket_id=bucket_id)

    global _RATE_LIMIT_BUCKETS
    return bucket_data, _RATE_LIMIT_BUCKETS[bucket_id]


def set_bucket_data(
    red: redis.StrictRedis, bucket: DiscordRateLimitData, lock: asyncio.Lock
) -> None:
    """Set the bucket data and lock using the bucket ID"""
    logger.debug("Updating bucket data: %s", bucket)
    global _RATE_LIMIT_BUCKETS

    if bucket.id:
        _RATE_LIMIT_BUCKETS[bucket.id] = lock
        set_rate_limit_bucket_data(red=red, bucket=bucket)
    else:
        logger.error("Received a None bucket ID: %s", bucket)


def set_webhook_error(
    red: redis.StrictRedis,
    webhook_id: str,
    webhook_type: WebhookType,
    auth_401: bool = False,
    auth_403: bool = False,
    _404: bool = False,
    prefix: str = WEBHOOK_ERRORS,
):
    """Store the last error received for a webhook; cleared after a successful request"""
    key = f"{prefix}:{webhook_type}:{webhook_id}"
    # can't send a bool to redis
    payload: DiscordErrorResponse = {
        "http_401": int(auth_401),  # type: ignore
        "http_403": int(auth_403),  # type: ignore
        "http_404": int(_404),  # type: ignore
    }
    red.hset(key, mapping=payload)  # type: ignore


def get_webhook_error(
    red: redis.StrictRedis,
    webhook_id: str,
    webhook_type: WebhookType,
    prefix: str = WEBHOOK_ERRORS,
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


def clear_webhook_errors(
    red: redis.StrictRedis, webhook_id: str, webhook_type: WebhookType
):
    """Reset the errors (HTTP 401/403) for a webhook ID"""
    # TODO: likely have to tweak this when we support other webhook types in the future
    set_webhook_error(
        red=red,
        webhook_id=webhook_id,
        webhook_type=webhook_type,
        auth_401=False,
        auth_403=False,
    )


def enqueue_scoreboard_message(
    message: WebhookMessage,
    message_key: str,
    red: redis.StrictRedis | None = None,
    prefix: str = PREFIX,
    ttl: int = 120,
):
    """Accept a WebhookMessage and scorebot message key to only store the most recent update"""
    logger.info("Enqueuing %s: %s", message_key, message)

    # Allows easier usage for enqueing from different services/sections of CRCON
    if red is None:
        url = construct_redis_url(db_number=0)
        red = get_redis_client(redis_url=url, decode_responses=False, global_pool=True)

    # Scoreboard messages are inherently temporary since they change often;
    # there is no point in retaining old messages
    # So instead of using a list as a message queue; save the payload at
    # a unique key for this scoreboard message key (header/gamestate, map rotation, player stats)
    # overwriting anything that was there before so only the most recently queued
    # update is used
    key = f"{prefix}:{get_server_number()}:{message.webhook_type}:{message.message_type}:{message.payload['webhook_id']}:{message_key}"
    red.set(key, orjson.dumps(message.model_dump_json()), ex=ttl)


def enqueue_message(
    message: WebhookMessage, red: redis.StrictRedis | None = None, prefix: str = PREFIX
):
    """Accept a WebhookMessage and insert it in Redis

    Queues are independently tracked by the webhook ID (Discord snowflake)
    """
    logger.debug("Enqueuing %s", message)

    # Allows easier usage for enqueing from different services/sections of CRCON
    if red is None:
        url = construct_redis_url(db_number=0)
        red = get_redis_client(redis_url=url, decode_responses=False, global_pool=True)

    if not isinstance(message, WebhookMessage):
        raise ValueError(f"{message} must be a WebhookMessage instance")

    # Because we use lists; each type of message gets its own queue so that we can
    # more efficiently purge types of messages (for instance all kill log lines)
    # without having to scan/decode every element in a list which might be thousands
    # of elements long
    queue_id = f"{prefix}:{get_server_number()}:{message.webhook_type}:{message.message_type}:{message.payload['webhook_id']}"
    red.rpush(queue_id, orjson.dumps(message.model_dump_json()))


def construct_webhook(
    payload: DiscordWebhookDict, webhook_type: WebhookType
) -> AsyncDiscordWebhook:
    if webhook_type == WebhookType.DISCORD:
        unpacked: DiscordWebhookDict = payload  # type: ignore
        wh = AsyncDiscordWebhook(**unpacked)
    else:
        raise TypeError(f"{webhook_type} is an unsupported webhook type")

    return wh


def unpack_message(raw_message: bytes) -> WebhookMessage:
    message = WebhookMessage.model_validate_json(orjson.loads(raw_message))
    return message


async def dequeue_message(
    red: redis.StrictRedis,
    client: httpx.AsyncClient,
    queue_id: str,
    bucket_data: DiscordRateLimitData | None,
    lock: asyncio.Lock,
):
    """Parse a dequeued message from redis, validate and send to Discord, requeuing if needed"""

    if bucket_data is None:
        bucket_data = DiscordRateLimitData()

    async def _dequeue_message(
        red: redis.StrictRedis,
        client: httpx.AsyncClient,
        queue_id: str,
        bucket_data: DiscordRateLimitData,
        lock: asyncio.Lock,
    ):
        logger.debug("Dequeueing from %s", queue_id)

        # Scoreboard messages are stored as key/value pairs and not a list
        if SCOREBOARD in queue_id:
            # Old style messages may still be in the redis queue and we can't GET those
            try:
                raw_message: bytes = red.get(queue_id)  # type: ignore
                # If we don't get a message at all; return
                # this is validated by Pydantic later
                if raw_message is None:
                    return
                red.delete(queue_id)
            except redis.exceptions.ResponseError:
                # If we don't remove this; it will be stuck in the queue and block it forever
                # until the redis cache is otherwise cleared
                logger.warning(f"Discarding wrong message type: {queue_id}")
                red.lpop(queue_id)
                return
        else:
            raw_message: bytes = red.lpop(queue_id)  # type: ignore

        message = unpack_message(raw_message=raw_message)
        wh = construct_webhook(
            payload=message.payload, webhook_type=message.webhook_type
        )

        if message.edit:
            res: httpx.Response = await wh.edit(client=client)
        else:
            res: httpx.Response = await wh.execute(client=client)  # type: ignore

        # If a webhook ID is incorrect it will return 401 which we already handle
        # but if a message ID doesn't exist it will return 404 and not have rate
        # limit headers
        # Technically we could make this fixable and re-enqueue the messages but
        # the only thing we do edits for are the scoreboard and those messages
        # are inherently transient; so we will set the error status for the webhook ID
        # and drop the message
        if res.status_code == 404:
            logger.error(
                f"Received HTTP 404 from the webhook with webhook ID: {message.payload.get('webhook_id')} message ID: {message.payload.get('message_id')} purging the queue for this message ID"
            )
            # Mark this specific message ID as a 404 failure
            set_message_edit_404_failure(
                red=red, message_id=message.payload["message_id"]
            )
            clear_queue_by_message_id(
                red=red, queue_id=queue_id, message_id=message.payload["message_id"]
            )
            # Flag this webhook as having an error
            set_webhook_error(
                red=red,
                webhook_id=wh.webhook_id,
                webhook_type=message.webhook_type,
                _404=True,
            )

            return

        # 400 is rather rare; but if someone has misconfigured a URL
        # e.g. a URL that looks like this https://discord.com/api/webhooks/.../...
        # it will occur
        if res.status_code == 400:
            logger.error("%s is not a valid webhook URL", wh.url)
            return

        # We handle these status codes below; we want an error message if
        # we encounter an unknown status code so we can update this appropriately
        if res.status_code not in (200, 401, 403, 429):
            logger.error(
                "Received HTTP %s from Discord, headers:%s: %s",
                res.headers,
                res.status_code,
                message.model_dump(),
            )
            return

        bucket_data.webhook_type = message.webhook_type
        bucket_data.id = res.headers[X_RATELIMIT_BUCKET]
        bucket_data.remaining_requests = int(res.headers[X_RATELIMIT_REMAINING])
        bucket_data.reset_after_secs = int(res.headers[X_RATELIMIT_RESET_AFTER])
        bucket_data.reset_timestamp = math.ceil(
            datetime.now().timestamp() + bucket_data.reset_after_secs
        )

        if lock == get_shared_lock():
            # Once we get a response for a webhook we know what rate limit bucket it's in and we can
            # associate it with a lock so that all shared limits use the same lock and don't process
            # concurrently
            # TODO: what if we add another webhook after that then shares a rate limit bucket with one
            # that's already been created, will it find it?
            lock = asyncio.Lock()
            logger.debug("Created %s for %s", lock, queue_id)

        if res.status_code == 429:
            bucket_data.rate_limited = True
            update_bucket_rate_limit(
                red=red, bucket_id=bucket_data.id, webhook_type=message.webhook_type
            )
            body = res.json()
            if body.get("global"):
                # We're globally rate limited, parse out the relevant data and set it
                # This can get stepped on in multiple tasks because it isn't locked
                try:
                    retry_after_secs = float(body.get("retry_after"))
                except TypeError:
                    retry_after_secs = DEFAULT_GLOBAL_RETRY_AFTER_SECS
                    logger.error(
                        "Unable to parse retry_after: %s, falling back to %s seconds",
                        body.get("retry_after"),
                        retry_after_secs,
                    )
                discord_message = body.get("message")
                logger.warning(
                    "Your IP is currently globally rate limited by discord: Retrying after %s, %s",
                    datetime.now() + timedelta(seconds=retry_after_secs),
                    discord_message,
                )
                set_global_rate_limit_reset_after(
                    red=red,
                    limit=(
                        datetime.now() + timedelta(seconds=math.ceil(retry_after_secs))
                    ).timestamp(),
                )

            logger.warning(
                "Rate limited HTTP %s for %s %s resets after %s",
                res.status_code,
                wh.webhook_id,
                message.webhook_type,
                datetime.fromtimestamp(bucket_data.reset_timestamp),
            )

            if not message.discardable:
                logger.info(
                    "Re-enqueing webhook ID: %s due to rate limit",
                    message.payload["webhook_id"],
                )
                message.retry_attempts += 1
                red.lpush(queue_id, orjson.dumps(message.model_dump_json()))  # type: ignore
                red.ltrim(queue_id, 0, WH_MAX_QUEUE_LENGTH - 1)
        elif res.status_code == 401:
            set_webhook_error(
                red=red,
                webhook_id=wh.webhook_id,
                webhook_type=message.webhook_type,
                auth_401=True,
            )
            logger.error(
                "%s does not appear to be a valid webhook (unknown ID); check the URL",
                wh.url,
            )
        elif res.status_code == 403:
            set_webhook_error(
                red=red,
                webhook_id=wh.webhook_id,
                webhook_type=message.webhook_type,
                auth_403=True,
            )
            logger.error(
                "%s does not appear to be a valid webhook (invalid token); check the URL",
                wh.url,
            )
        elif res.status_code == 200:
            bucket_data.rate_limited = False
            clear_webhook_errors(
                red=red,
                webhook_id=wh.webhook_id,
                webhook_type=message.webhook_type,
            )
        else:
            logger.error(
                f"Received edit={message.edit} discardable={message.discardable} {res.status_code} for: {wh.json}"
            )

        set_bucket_data(red=red, bucket=bucket_data, lock=lock)
        set_webhook_rate_limit_bucket(
            red=red,
            queue_id=queue_id,
            bucket_id=bucket_data.id,
        )

    async with lock:
        try:
            await _dequeue_message(
                red=red,
                client=client,
                queue_id=queue_id,
                bucket_data=bucket_data,
                lock=lock,
            )
            logger.debug("finished with %s", lock)
        except pydantic.ValidationError as e:
            logger.exception(e)


def get_all_queue_keys(
    red: redis.StrictRedis | None = None, prefix: str = PREFIX
) -> list[str]:
    """Retrieve every queue key in redis that matches the service prefix"""
    logger.debug("Getting all queue IDs from %s", PREFIX)
    if red is None:
        red = get_redis_client(decode_responses=False, global_pool=True)

    queue_ids: list[str] = [
        queue_id.decode()
        for queue_id in red.scan_iter(match=f"{prefix}*", _type="list")
    ]
    return queue_ids


def get_all_scoreboard_message_keys(
    red: redis.StrictRedis | None = None, prefix: str = PREFIX
) -> list[str]:
    """Retrieve each scoreboard key which acts as a queue_id"""
    # Scoreboard messages which are stored as individual key/value pairs
    scoreboard_messages: list[str] = [
        queue_id.decode()
        for queue_id in red.scan_iter(match=f"{prefix}*", _type="string")
        if SCOREBOARD_BYTES in queue_id
    ]

    return scoreboard_messages


def get_all_queue_keys_and_lengths(
    red: redis.StrictRedis, prefix: str = PREFIX
) -> list[tuple[str, int]]:
    """Return each queue key and the number of elements in its queue"""
    return [(queue_id, red.llen(queue_id)) for queue_id in get_all_queue_keys(red=red, prefix=prefix)]  # type: ignore


def get_all_queue_keys_not_empty(
    red: redis.StrictRedis, prefix: str = PREFIX
) -> list[str]:
    """Scan for all the queues (identified by prefix)"""
    logger.debug("Getting all queue IDs with items from %s", PREFIX)
    populated_queues = [queue_id for queue_id in get_all_queue_keys(red=red, prefix=prefix) if red.llen(queue_id) > 0]  # type: ignore
    populated_scoreboard_messages = get_all_scoreboard_message_keys(
        red=red, prefix=prefix
    )
    return populated_queues + populated_scoreboard_messages


def get_scoreboard_message_overview(
    queue_id: str,
    red: redis.StrictRedis | None,
) -> ScoreboardMessageStatus | None:
    parts = _split_scoreboard_key(queue_id=queue_id)

    if not parts:
        return

    if red is None:
        red = get_redis_client(decode_responses=False, global_pool=True)

    bucket_data: DiscordRateLimitData | None = None
    bucket_id = get_webhook_rate_limit_bucket(red=red, queue_id=queue_id)
    if bucket_id:
        bucket_data = get_rate_limit_bucket_data(red=red, bucket_id=bucket_id)

    overview: ScoreboardMessageStatus = {
        "server_number": int(parts.server_number),
        "id": parts.id,
        "webhook_type": parts.wh_type,
        "message_type": parts.msg_type,
        "rate_limit_bucket": bucket_id,
        "rate_limited": bucket_data.rate_limited if bucket_data else False,
        "message_key": parts.message_key,
        "redis_key": queue_id,
    }
    return overview


def get_queue_overview(
    queue_id: str, red: redis.StrictRedis | None = None
) -> QueueStatus | None:
    """Return a summary of a queue if it exists"""
    parts = _split_queue_id(queue_id=queue_id)

    if not parts:
        return

    if red is None:
        red = get_redis_client(decode_responses=False, global_pool=True)

    length: int = red.llen(queue_id)  # type: ignore
    bucket_data: DiscordRateLimitData | None = None
    bucket_id = get_webhook_rate_limit_bucket(red=red, queue_id=queue_id)
    if bucket_id:
        bucket_data = get_rate_limit_bucket_data(red=red, bucket_id=bucket_id)

    overview: QueueStatus = {
        "server_number": int(parts.server_number),
        "id": parts.id,
        "webhook_type": parts.wh_type,
        "message_type": parts.msg_type,
        "length": length,
        "rate_limit_bucket": bucket_data.id if bucket_data else None,
        "rate_limited": bucket_data.rate_limited if bucket_data else False,
        "redis_key": queue_id,
    }
    return overview


def get_next_queue_id(queue_ids: list[str]) -> str | None:
    """Get the next queue to process (if any) and re-add queue to the end"""
    logger.debug("Getting a random queue ID from %s", queue_ids)
    # People can add/remove webhooks in CRCON at any point, after we've scanned Redis
    # for queues, pick one at random instead of trying to track the previous one we did
    # this should be random enough that over time no queue gets priority and if any
    # one queue has a weird error, we shouldn't get stuck trying to reprocess it
    return random.choice(queue_ids) if queue_ids else None


def webhook_service_summary(red: redis.StrictRedis | None = None):
    """Return a queue overview for all queues, by server number, webhook type and message type"""
    if red is None:
        red = get_redis_client(decode_responses=False, global_pool=True)

    # Get the global rate limit status/expiration
    # Get each queue, by webhook type (discord, etc.) and the number of messages

    data = {}

    data["is_globally_rate_limited"] = is_globally_rate_limited(red=red)
    data["global_rate_limit_reset_after"] = get_global_rate_limit_reset_after(red=red)

    queue_ids = get_all_queue_keys(red=red)
    queues: defaultdict[int, dict[str, dict[str, list[QueueStatus]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )
    for qid in queue_ids:
        overview: QueueStatus | None = get_queue_overview(red=red, queue_id=qid)
        if overview:
            queues[overview["server_number"]][overview["webhook_type"]][
                overview["message_type"]
            ].append(overview)

    data["queues"] = queues

    scoreboard_messages: defaultdict[
        int, dict[str, dict[str, list[ScoreboardMessageStatus]]]
    ] = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for key in get_all_scoreboard_message_keys(red=red):
        scoreboard_overview: ScoreboardMessageStatus | None = (
            get_scoreboard_message_overview(red=red, queue_id=key)
        )

        if scoreboard_overview:
            scoreboard_messages[scoreboard_overview["server_number"]][
                scoreboard_overview["webhook_type"]
            ][scoreboard_overview["message_type"]].append(scoreboard_overview)

    data["scoreboard_messages"] = scoreboard_messages
    return data


def reset_all_queues_for_server_number(
    server_number: int | str, red: redis.StrictRedis | None = None
) -> int:
    """Delete each queue associated with the specified server number"""
    if red is None:
        red = get_redis_client(decode_responses=False, global_pool=True)

    queue_ids = get_all_queue_keys(red=red)
    deleted: int = 0
    for queue_id in queue_ids:
        try:
            parts = _split_queue_id(queue_id=queue_id)
            # server numbers should be ints; but redis keys are strings
            if parts and parts.server_number == str(server_number):
                deleted += red.delete(queue_id)  # type: ignore
        except ValueError:
            logger.error("Unable to parse %s received an invalid key", queue_id)

    return deleted


def reset_webhook_queues(red: redis.StrictRedis | None = None) -> int:
    """Delete each queue; unprocessed messages may be lost depending on timing"""
    if red is None:
        red = get_redis_client(decode_responses=False, global_pool=True)

    keys = get_all_queue_keys(red=red)
    return red.delete(*keys)  # type: ignore


def reset_queue(queue_id: str, red: redis.StrictRedis | None = None) -> bool:
    """Delete the specified queue; returning if it deleted any entries"""
    if red is None:
        red = get_redis_client(decode_responses=False, global_pool=True)

    # TODO: this could cause conflicts in the future if we start supporting other webhooks
    # than just discord; it's possible but unlikely that their queue IDs could conflict
    # we could use the entire redis key instead of just the component pieces
    return red.delete(queue_id) != 0  # type: ignore


def reset_queue_type(
    webhook_type: WebhookType | str, red: redis.StrictRedis | None = None
) -> int:
    """Delete each queue of wh_type (discord, etc.) returning the number of deleted queues"""
    if red is None:
        red = get_redis_client(decode_responses=False, global_pool=True)

    if isinstance(webhook_type, str):
        webhook_type = WebhookType(webhook_type)

    queue_ids = get_all_queue_keys(red=red)
    deleted: int = 0
    for queue_id in queue_ids:
        parts = _split_queue_id(queue_id)
        if parts and parts.wh_type == webhook_type:
            deleted += red.delete(queue_id)  # type: ignore

    return deleted


def reset_message_type(
    message_type: WebhookMessageType | str, red: redis.StrictRedis | None = None
) -> int:
    """Delete each queue of wh_type (discord, etc.) returning the number of deleted queues"""
    if red is None:
        red = get_redis_client(decode_responses=False, global_pool=True)

    if isinstance(message_type, str):
        message_type = WebhookMessageType(message_type)

    queue_ids = get_all_queue_keys(red=red)
    deleted: int = 0
    for queue_id in queue_ids:
        parts = _split_queue_id(queue_id)
        if parts and parts.msg_type == message_type:
            deleted += red.delete(queue_id)  # type: ignore

    return deleted


def _split_queue_id(queue_id: str) -> QueueParts | None:
    """Parse a queue ID int its component parts (prefix, server number, webhook type, message type and ID)"""
    try:
        prefix, server_number, wh_type, msg_type, qid = queue_id.split(":")
        return QueueParts(
            prefix=prefix,
            server_number=server_number,
            wh_type=WebhookType(wh_type),
            msg_type=WebhookMessageType(msg_type),
            id=qid,
        )
    except ValueError:
        logger.error("Unable to parse %s received an invalid key", queue_id)
        return


def _split_scoreboard_key(queue_id: str) -> ScoreboardQueueParts | None:
    try:
        prefix, server_number, wh_type, msg_type, qid, message_key = queue_id.split(":")
        return ScoreboardQueueParts(
            prefix=prefix,
            server_number=server_number,
            wh_type=WebhookType(wh_type),
            msg_type=WebhookMessageType(msg_type),
            id=qid,
            message_key=message_key,
        )
    except ValueError:
        logger.error("Unable to parse %s received an invalid key", queue_id)
        return


async def main():

    # Essentially we want to connect to redis, monitor the set of queues of discord messages
    # by webhook queue
    # and (within the max concurrent process limit) block, get the next queue to process
    # and dequeue a message off the queue (adding this queue to the end of the queue of queues)
    # create a new process and pass it the data from the queue so it can construct/send the
    # webhook
    # this lets each webhook process 1 message at a time in order (unfair to webhooks that send infrequently)

    # if the webhook is rate limited and it isn't an ephemeral message;
    # re-queue the message (at the end of the queue so it is re-processed immediately-ish
    # Also check for other errors like excessively long messages, anything that would block
    # discord from accepting it and mitigate it if possible
    # global rate limits, so forth

    # if it is ephemeral and we're rate limited; we just drop the message no big deal

    # Grab the top message off each queue and send them off

    logger.info("Starting webhook service")
    url = construct_redis_url()
    red = get_redis_client(redis_url=url, decode_responses=False, global_pool=True)

    client = httpx.AsyncClient()
    lock: asyncio.Lock | None = None
    continue_logged = False

    # Create a file to use for the docker health check
    from pathlib import Path

    path = Path("/code") / Path("webhook-service-healthy")
    path.touch()

    while True:
        # Check each loop to pick up new queues that have been added since last iteration
        queue_ids = get_all_queue_keys_not_empty(red=red)

        # Keep each message queue under its max, dropping the oldest messages first
        for queue_id in queue_ids:
            # Can't trim scoreboard messages which are stored as simple KEY/VALUE pairs
            if SCOREBOARD not in queue_id:
                red.ltrim(queue_id, 0, WH_MAX_QUEUE_LENGTH - 1)

        logger.debug("queue_ids=%s", queue_ids)
        queue_id: str | None = get_next_queue_id(queue_ids=queue_ids)
        logger.debug("queue_id=%s", queue_id)
        bucket_data: DiscordRateLimitData | None = None

        if queue_id:
            bucket_id: str | None = get_webhook_rate_limit_bucket(
                red=red, queue_id=queue_id
            )
            # If we don't know the rate limit bucket; use the shared one further below
            if bucket_id:
                bucket_data, lock = get_bucket_lock(red=red, bucket_id=bucket_id)
                if lock and lock.locked():
                    logger.debug("%s locked", lock)
                    await asyncio.sleep(0)
                    continue
                ts = int(datetime.now(tz=timezone.utc).timestamp())

                # Even with Discords headers, and using a local rate limit, I still have issues with
                # hooks getting rate limited during testing, if we rate limit a bucket, pad it an extra
                # second before re-using it to reduce the chance of further rate limits
                if (
                    is_globally_rate_limited(red=red)
                    or (
                        bucket_data.rate_limited
                        and bucket_data.reset_timestamp is not None
                        and ts <= bucket_data.reset_timestamp + 1
                    )
                    or is_bucket_local_rate_limited(
                        red=red,
                        bucket_id=bucket_id,
                        webhook_type=bucket_data.webhook_type,
                    )
                ):
                    if not continue_logged:
                        logger.debug(
                            "Skipping %s due to rate limit now=%s reset_after=%s",
                            queue_id,
                            ts,
                            bucket_data.reset_timestamp,
                        )
                        continue_logged = True
                    continue

            continue_logged = False
            logger.debug("Starting asyncio task for %s", queue_id)
            if lock is None or lock == get_shared_lock():
                logger.debug("using shared lock")
                lock = get_shared_lock()
                task = asyncio.create_task(
                    dequeue_message(
                        red=red,
                        client=client,
                        queue_id=queue_id,
                        bucket_data=bucket_data,
                        lock=lock,
                    )
                )
                logger.debug("Waiting for %s", task)
                await task
            else:
                logger.debug("using bucket lock")
                task = asyncio.create_task(
                    dequeue_message(
                        red=red,
                        client=client,
                        queue_id=queue_id,
                        bucket_data=bucket_data,
                        lock=lock,
                    )
                )

        # If we never await something we never allow any of the tasks to run
        # but sleeping a specific amount of time can prevent queues from emptying
        # faster than CRCON can fill them up
        # however sleeping `0` seconds  gives the event loop an opportunity for
        # tasks to run; this does cause CPU usage to increase because this loop
        # runs far more often; we've limited the CPU usage by default to 1 core in
        # the webhook service definition in `docker-compose-common-components.yaml`
        # https://docs.python.org/3/library/asyncio-task.html#sleeping
        await asyncio.sleep(0)


if __name__ == "__main__":
    # main()
    asyncio.run(main())
