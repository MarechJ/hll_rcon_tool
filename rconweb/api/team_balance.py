import logging
from typing import List, Sequence

import redis
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rcon.cache_utils import get_redis_client
from rcon.discord import send_to_discord_audit
from rcon.recorded_commands import RecordedRcon
from rcon.settings import SERVER_INFO
from rcon.team_shuffle import balance, shuffle
from rcon.team_shuffle.constants import (
    API_COMMAND_BALANCE,
    API_COMMAND_SHUFFLE,
    COMMAND_FAILED_ERROR_MSG,
    DISCORD_BALANCE_SHUFFLE_WEBHOOK,
    SWAP_SUCCESSFUL_MSG,
)
from rcon.team_shuffle.models import DetailedPlayerInfo, SwapRateLimitError
from rcon.team_shuffle.utils import audit

from .auth import api_response, login_required
from .utils import _get_data

logger = logging.getLogger(__name__)


@csrf_exempt
@login_required
def balance_teams(request) -> JsonResponse:
    """Parse the incoming request, log the request and then balance teams."""
    data = _get_data(request)

    rebalance_method: str = data.get("rebalance_method")
    immune_level: int = int(data.get("immune_level"))
    immune_roles: Sequence[str] = data.get("immune_roles")
    immune_seconds: int = data.get("immune_seconds")
    include_teamless: bool = data.get("include_teamless")
    swap_on_death: bool = data.get("swap_on_death")

    rcon_hook: RecordedRcon = RecordedRcon(SERVER_INFO)
    redis_store: redis.Redis[bytes] = get_redis_client()

    failed = False

    message = (
        f"[`{request.user.username}`] `{API_COMMAND_BALANCE}` by `{rebalance_method}`"
    )
    logger.info(message)
    audit(
        DISCORD_BALANCE_SHUFFLE_WEBHOOK,
        message,
    )
    # This is double logging, but in case someone isn't using DISCORD_BALANCE_SHUFFLE_WEBHOOK they'll
    # still see in in their regular audit webhook
    send_to_discord_audit(API_COMMAND_BALANCE, by=request.user.username)

    original_axis: List[DetailedPlayerInfo] = []
    swapped_axis: List[DetailedPlayerInfo] = []
    original_allies: List[DetailedPlayerInfo] = []
    swapped_allies: List[DetailedPlayerInfo] = []
    original_teamless: List[DetailedPlayerInfo] = []
    swapped_teamless: List[DetailedPlayerInfo] = []
    try:
        (
            original_axis,
            swapped_axis,
            original_allies,
            swapped_allies,
            original_teamless,
            swapped_teamless,
        ) = balance.autobalance_teams(
            rcon_hook,
            redis_store,
            rebalance_method=rebalance_method,
            immune_level=immune_level,
            immune_roles=immune_roles,
            immune_seconds=immune_seconds,
            include_teamless=include_teamless,
            swap_on_death=swap_on_death,
        )
    # TODO: Log/ specific exceptions
    except SwapRateLimitError as e:
        failed = True
        message = f"{API_COMMAND_BALANCE} failed {e}"
        logger.exception(message)
        audit(
            DISCORD_BALANCE_SHUFFLE_WEBHOOK,
            message,
        )
    except:
        failed = True
        logger.exception(f"{API_COMMAND_BALANCE} FAILED.")
        audit(
            DISCORD_BALANCE_SHUFFLE_WEBHOOK,
            COMMAND_FAILED_ERROR_MSG.format(API_COMMAND_BALANCE),
        )

    logger.info(
        SWAP_SUCCESSFUL_MSG.format(
            API_COMMAND_BALANCE,
            len(swapped_axis),
            len(original_axis),
            len(swapped_allies),
            len(original_allies),
            len(swapped_teamless),
            len(original_teamless),
        )
    )

    return api_response(
        None,
        failed=failed,
        command=API_COMMAND_BALANCE,
        arguments={
            "rebalance_method": rebalance_method,
            "immune_level": immune_level,
            "immune_roles": immune_roles,
            "immune_seconds": immune_seconds,
            "include_teamless": include_teamless,
            "swap_on_death": swap_on_death,
        },
    )


@csrf_exempt
@login_required
def shuffle_teams(request) -> JsonResponse:
    """Parse the incoming request, log the request and then shuffle teams."""
    data = _get_data(request)

    shuffle_method: str = data.get("shuffle_method")

    rcon_hook: RecordedRcon = RecordedRcon(SERVER_INFO)
    redis_store: redis.Redis[bytes] = get_redis_client()

    failed = False

    message = (
        f"[`{request.user.username}`] `{API_COMMAND_SHUFFLE}` by `{shuffle_method}`"
    )
    logger.info(message)
    audit(
        DISCORD_BALANCE_SHUFFLE_WEBHOOK,
        message,
    )
    # This is double logging, but in case someone isn't using DISCORD_BALANCE_SHUFFLE_WEBHOOK they'll
    # still see in in their regular audit webhook
    send_to_discord_audit(API_COMMAND_SHUFFLE, by=request.user.username)

    original_axis: List[DetailedPlayerInfo] = []
    swapped_axis: List[DetailedPlayerInfo] = []
    original_allies: List[DetailedPlayerInfo] = []
    swapped_allies: List[DetailedPlayerInfo] = []
    original_teamless: List[DetailedPlayerInfo] = []
    swapped_teamless: List[DetailedPlayerInfo] = []
    try:
        (
            original_axis,
            swapped_axis,
            original_allies,
            swapped_allies,
            original_teamless,
            swapped_teamless,
        ) = shuffle.shuffle_teams(rcon_hook, redis_store, shuffle_method)
    # TODO: Log/catch specific exceptions
    except SwapRateLimitError as e:
        failed = True
        message = f"{API_COMMAND_BALANCE} failed {e}"
        logger.exception(message)
        audit(
            DISCORD_BALANCE_SHUFFLE_WEBHOOK,
            message,
        )
    except:
        failed = True
        logger.exception(f"{API_COMMAND_SHUFFLE} FAILED.")
        audit(
            DISCORD_BALANCE_SHUFFLE_WEBHOOK,
            COMMAND_FAILED_ERROR_MSG.format(API_COMMAND_BALANCE),
        )

    logger.info(
        SWAP_SUCCESSFUL_MSG.format(
            API_COMMAND_SHUFFLE,
            len(swapped_axis),
            len(original_axis),
            len(swapped_allies),
            len(original_allies),
            len(swapped_teamless),
            len(original_teamless),
        )
    )

    return api_response(
        None,
        failed=failed,
        command=API_COMMAND_SHUFFLE,
        arguments={"shuffle_method": shuffle_method},
    )
