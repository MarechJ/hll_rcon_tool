import logging

import redis
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rcon.cache_utils import get_redis_client
from rcon.config import get_config
from rcon.recorded_commands import RecordedRcon
from rcon.team_shuffle import balance, shuffle
from rcon.team_shuffle.constants import (
    API_COMMAND_EVEN_TEAM_SIZES,
    API_COMMAND_SHUFFLE,
    SWAP_SUCCESSFUL_MSG,
)
from rcon.team_shuffle.models import SwapRateLimitError, TeamShuffleConfig
from rcon.team_shuffle.utils import audit
from rcon.types import TeamViewPlayerType

# Use existing connections
from rconweb.api.views import ctl

from .auth import api_response, login_required
from .utils import _get_data

logger = logging.getLogger(__name__)


@csrf_exempt
@login_required
def do_even_teams(request) -> JsonResponse:
    """Parse the incoming request, log the request and then even team sizes."""
    data = _get_data(request)

    rebalance_method: str = data.get("rebalance_method")
    immune_level: int = int(data.get("immune_level"))
    immune_roles: list[str] = data.get("immune_roles")
    immune_seconds: int = data.get("immune_seconds")
    include_teamless: bool = data.get("include_teamless")
    swap_on_death: bool = data.get("swap_on_death")

    rcon_hook: RecordedRcon = ctl
    redis_store: redis.Redis[bytes] = get_redis_client()

    failed = False

    try:
        config = TeamShuffleConfig(**get_config()["TEAM_SHUFFLE"])
    except (KeyError, ValueError) as e:
        logger.error("Invalid `TEAM_SHUFFLE` configuration in your `config.yml`: {e}")
        return api_response(
            None,
            failed=True,
            command=API_COMMAND_EVEN_TEAM_SIZES,
            arguments={
                "rebalance_method": rebalance_method,
                "immune_level": immune_level,
                "immune_roles": immune_roles,
                "immune_seconds": immune_seconds,
                "include_teamless": include_teamless,
                "swap_on_death": swap_on_death,
            },
        )

    message = f"[`{request.user.username}`] `{API_COMMAND_EVEN_TEAM_SIZES}` by `{rebalance_method}`"
    logger.info(message)
    audit(config.discord_webhook_url, message, by=request.user.username)

    original_axis: list[TeamViewPlayerType] = []
    swapped_axis: list[TeamViewPlayerType] = []
    original_allies: list[TeamViewPlayerType] = []
    swapped_allies: list[TeamViewPlayerType] = []
    original_teamless: list[TeamViewPlayerType] = []
    swapped_teamless: list[TeamViewPlayerType] = []
    try:
        (
            original_axis,
            swapped_axis,
            original_allies,
            swapped_allies,
            original_teamless,
            swapped_teamless,
        ) = balance.even_teams(
            rcon_hook,
            redis_store,
            config,
            rebalance_method=rebalance_method,
            immune_level=immune_level,
            immune_roles=immune_roles,
            immune_seconds=immune_seconds,
            include_teamless=include_teamless,
            swap_on_death=swap_on_death,
        )
    # TODO: Log specific exceptions
    except SwapRateLimitError as e:
        failed = True
        logger.error(f"{API_COMMAND_EVEN_TEAM_SIZES} failed {e}")
    except Exception as e:
        failed = True
        logger.exception(f"{API_COMMAND_EVEN_TEAM_SIZES} failed {e}")
        raise e

    if not failed:
        logger.info(
            SWAP_SUCCESSFUL_MSG.format(
                API_COMMAND_EVEN_TEAM_SIZES,
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
        command=API_COMMAND_EVEN_TEAM_SIZES,
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
def do_shuffle_teams(request) -> JsonResponse:
    """Parse the incoming request, log the request and then shuffle teams."""
    data = _get_data(request)

    shuffle_method: str = data.get("shuffle_method")

    rcon_hook: RecordedRcon = ctl
    redis_store: redis.Redis[bytes] = get_redis_client()

    failed = False

    try:
        config = TeamShuffleConfig(**get_config()["TEAM_SHUFFLE"])
    except (KeyError, ValueError) as e:
        logger.error("Invalid `TEAM_SHUFFLE` configuration in your `config.yml`: {e}")
        return api_response(
            None,
            failed=True,
            command=API_COMMAND_SHUFFLE,
            arguments={"shuffle_method": shuffle_method},
        )
    except Exception as e:
        failed = True
        logger.exception(f"{API_COMMAND_SHUFFLE} failed {e}")
        raise e

    message = (
        f"[`{request.user.username}`] `{API_COMMAND_SHUFFLE}` by `{shuffle_method}`"
    )
    logger.info(message)
    audit(config.discord_webhook_url, message, by=request.user.username)

    original_axis: list[TeamViewPlayerType] = []
    swapped_axis: list[TeamViewPlayerType] = []
    original_allies: list[TeamViewPlayerType] = []
    swapped_allies: list[TeamViewPlayerType] = []
    original_teamless: list[TeamViewPlayerType] = []
    swapped_teamless: list[TeamViewPlayerType] = []
    try:
        (
            original_axis,
            swapped_axis,
            original_allies,
            swapped_allies,
            original_teamless,
            swapped_teamless,
        ) = shuffle.shuffle_teams(rcon_hook, redis_store, config, shuffle_method)
    # TODO: Log/catch specific exceptions
    except SwapRateLimitError as e:
        failed = True
        logger.error(f"{API_COMMAND_EVEN_TEAM_SIZES} failed {e}")
    except Exception:
        failed = True
        logger.error(f"{API_COMMAND_SHUFFLE} FAILED.")
        raise

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
