from logging import getLogger

import django.db.utils
from django.apps import AppConfig
from django.conf import settings

from rcon.cache_utils import RedisCached, get_redis_pool, invalidates

logger = getLogger(__name__)


class ApiConfig(AppConfig):
    name = "api"

    def ready(self):
        from rcon.audit import set_registered_mods

        # Can't import from rconweb.api until Django is ready
        from .auth import get_moderators_accounts

        # Cached values can outlive several development server reloads. Clear
        # them on startup so code changes are immediately visible.
        if settings.DEBUG:
            RedisCached.clear_all_caches(get_redis_pool())

        # Invalidate the cache on start up because you can modify Django
        # records while CRCON is offline (through the CLI, etc.)
        with invalidates(get_moderators_accounts):
            try:
                # Register active admin accounts on startup for the ingame/online mods feature
                set_registered_mods(get_moderators_accounts())

            # This doesn't happen in production; only in the test environment
            # when running github actions
            except django.db.utils.ProgrammingError:
                logger.exception("programming error")
