import logging
from datetime import datetime
from typing import Callable

import pytz

from rcon.audit import ingame_mods, online_mods
from rcon.commands import BrokenHllConnection, CommandFailedError
from rcon.models import PlayerID

logger = logging.getLogger(__name__)


def _get_current_map_metric(rcon):
    try:
        rcon.current_map = str(rcon.get_map())
    except (CommandFailedError, BrokenHllConnection):
        logger.exception("Failed to get current map")
    return str(rcon.current_map)


player_flags: Callable[[PlayerID], list[str]] = lambda p: [f.flag for f in p.flags]
player_id: Callable[[PlayerID], str] = lambda p: p.player_id

METRICS = {
    "player_count": lambda rcon: int(rcon.get_slots()["current_players"]),
    "online_mods": lambda: len(online_mods()),
    "ingame_mods": lambda: len(ingame_mods()),
    "current_map": _get_current_map_metric,
    "time_of_day": lambda tz: datetime.now(tz=tz),
    "player_flags": player_flags,
    "player_id": player_id,
}


def create_condition(name, **kwargs):
    kwargs["inverse"] = kwargs.get("not", False)  # Using "not" would cause issues later
    if name == "player_count":
        return PlayerCountCondition(**kwargs)
    elif name == "online_mods":
        return OnlineModsCondition(**kwargs)
    elif name == "ingame_mods":
        return IngameModsCondition(**kwargs)
    elif name == "current_map":
        return CurrentMapCondition(**kwargs)
    elif name == "time_of_day":
        return TimeOfDayCondition(**kwargs)
    elif name == "player_flag":
        return PlayerFlagCondition(**kwargs)
    elif name == "player_id":
        return PlayerIdCondition(**kwargs)
    else:
        raise ValueError("Invalid condition type: %s" % name)


class Condition:
    def __init__(self, min=0, max=100, inverse=False, *args, **kwargs):
        self.min = int(min)
        self.max = int(max)
        self.inverse = bool(inverse)

        self.metric_name = ""
        self.metric_source = "rcon"

    @property
    def metric_getter(self):
        try:
            return METRICS[self.metric_name]
        except:
            return None

    def is_valid(self, **metric_sources):
        metric_source = []
        if self.metric_source is not None:
            metric_source.append(metric_sources[self.metric_source])
        comparand = self.metric_getter(*metric_source)
        res = self.min <= comparand <= self.max
        logger.info(
            "Applying condition %s: %s <= %s <= %s = %s. Inverse: %s",
            self.metric_name,
            self.min,
            comparand,
            self.max,
            res,
            self.inverse,
        )
        if self.inverse:
            return not res
        else:
            return res


class PlayerCountCondition(Condition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metric_name = "player_count"


class OnlineModsCondition(Condition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metric_name = "online_mods"
        self.metric_source = None


class IngameModsCondition(OnlineModsCondition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metric_name = "ingame_mods"
        self.metric_source = None


class ListCondition(Condition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.values = []

    def is_valid(self, **metric_sources):
        metric_source = metric_sources[self.metric_source]
        comparand = self.metric_getter(metric_source)
        res = comparand in self.values
        logger.info(
            "Applying condition %s: %s in %s = %s. Inverse: %s",
            self.metric_name,
            comparand,
            self.values,
            res,
            self.inverse,
        )
        if self.inverse:
            return not res
        else:
            return res


class CurrentMapCondition(ListCondition):
    def __init__(self, map_names=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.values = map_names
        self.metric_name = "current_map"
        self.metric_source = "rcon"


class PlayerFlagCondition(Condition):
    def __init__(self, flags=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flags = flags
        self.metric_name = "player_flags"
        self.metric_source = "player_id"

    def is_valid(self, **metric_sources):
        metric_source = metric_sources[self.metric_source]
        if metric_source is None:
            return False
        comparand = self.metric_getter(metric_source)
        res = False
        for c in comparand:
            if res := c in self.flags:
                break
        logger.info(
            "Applying condition %s: %s in %s = %s",
            self.metric_name,
            comparand,
            self.flags,
            res,
        )
        return res


class PlayerIdCondition(ListCondition):
    def __init__(self, player_ids=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.values = player_ids
        self.metric_name = "player_id"
        self.metric_source = "player_id"


class TimeOfDayCondition(Condition):
    def __init__(
        self, min="00:00", max="23:59", timezone="utc", inverse=False, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.min = str(min)
        self.max = str(max)
        if self.max in ["24:00", "0:00"]:
            self.max = "23:59"
        self.inverse = bool(inverse)
        if timezone.lower() == "utc":
            self.tz = pytz.UTC
        else:
            self.tz = pytz.timezone(timezone)
        self.metric_name = "time_of_day"
        self.metric_source = None

    def is_valid(self, **metric_sources):
        try:
            min_h, min_m = [int(i) for i in self.min.split(":")[:2]]
            max_h, max_m = [int(i) for i in self.max.split(":")[:2]]
            min = datetime.now(tz=self.tz).replace(hour=min_h, minute=min_m)
            max = datetime.now(tz=self.tz).replace(hour=max_h, minute=max_m)
        except Exception as e:
            logger.exception("Time Of Day condition is invalid and is ignored", e)
            return False  # The condition should fail
        comparand = datetime.now(tz=self.tz)
        res = min <= comparand <= max
        logger.info(
            "Applying condition %s: %s <= %s:%s <= %s = %s. Inverse: %s",
            self.metric_name,
            self.min,
            comparand.hour,
            comparand.minute,
            self.max,
            res,
            self.inverse,
        )
        if self.inverse:
            return not res
        else:
            return res
