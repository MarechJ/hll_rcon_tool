from django.apps import AppConfig
from rcon.cache_utils import invalidates
import django.db.utils
from logging import getLogger

logger = getLogger(__name__)


class ApiConfig(AppConfig):
    name = "api"

    def ready(self):
        from rcon.audit import set_registered_mods

        # Can't import from rconweb.api until Django is ready
        from .auth import get_moderators_accounts

        # Invalidate the cache on start up because you can modify Django
        # records while CRCON is offline (through the CLI, etc.)
        with invalidates(get_moderators_accounts):
            # Register active admin accounts on startup for the ingame/online mods feature
            try:
                set_registered_mods(get_moderators_accounts())
            except django.db.utils.ProgrammingError as e:
                logger.exception(e)
