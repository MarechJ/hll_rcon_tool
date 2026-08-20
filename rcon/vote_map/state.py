"""Redis-backed votemap state."""

import pickle
from collections.abc import Callable, Iterable
from datetime import datetime
from typing import Any, cast

from rcon import maps
from rcon.cache_utils import get_redis_client
from rcon.maps import Layer
from rcon.types import (
    VoteMapHistory,
    VoteMapHistoryResult,
    VoteMapStatus,
    VoteMapVote,
)
from rcon.utils import FixedLenList

from .storage import VotemapKeys


class VotemapState:
    LATEST_REMINDER = VotemapKeys.LATEST_REMINDER
    MAP_WHITELIST = VotemapKeys.MAP_WHITELIST
    MAP_SELECTION = VotemapKeys.MAP_SELECTION
    VOTES = VotemapKeys.VOTES
    ADMIN_NEXT_MAP = VotemapKeys.ADMIN_NEXT_MAP
    PLAYER_CHOICE = VotemapKeys.PLAYER_CHOICE
    NEXT_MAP = VotemapKeys.NEXT_MAP
    RESULT_HISTORY = VotemapKeys.RESULT_HISTORY

    def __init__(
        self,
        layer_parser: Callable[[str | Layer], Layer] = maps.parse_layer,
    ) -> None:
        self.client = get_redis_client()
        self._parse_layer = layer_parser
        self.results = FixedLenList[list[VoteMapHistory]](self.RESULT_HISTORY)

    ###
    # PLAYER CHOICE
    ###
    def get_player_choice(self) -> dict[str, str] | None:
        raw = cast(dict[bytes, bytes], self.client.hgetall(self.PLAYER_CHOICE))
        if not raw:
            return None
        return {k.decode(): v.decode() for k, v in raw.items()}

    def set_player_choice(self, player_id: str, player_name: str):
        self.client.hset(
            self.PLAYER_CHOICE,
            mapping={"player_name": player_name, "player_id": player_id},
        )

    def delete_player_choice(self):
        self.client.delete(self.PLAYER_CHOICE)

    ###
    # ADMIN NEXT MAP
    # When the admin wants to guarantee the next map
    # That practically pauses the map voting
    ###
    def get_admin_next_map(self) -> Layer | None:
        raw = cast(bytes | None, self.client.hget(self.ADMIN_NEXT_MAP, "map_name"))
        if not raw:
            return None
        return self._parse_layer(raw.decode())

    def set_admin_next_map(self, map: Layer):
        self.client.hset(
            self.ADMIN_NEXT_MAP,
            key="map_name",
            value=map.id,
        )

    def delete_admin_next_map(self):
        self.client.delete(self.ADMIN_NEXT_MAP)

    ###
    # LAST REMINDER TIME
    ###
    def get_last_reminder_time(self) -> datetime | None:
        as_date: datetime | None = None
        res = self.client.get(self.LATEST_REMINDER)
        if res is not None:
            as_date = pickle.loads(res)  # type: ignore
        return as_date

    def set_last_reminder_time(self, the_time: datetime) -> None:
        self.client.set(self.LATEST_REMINDER, pickle.dumps(the_time))

    def delete_last_reminder_time(self) -> None:
        self.client.delete(self.LATEST_REMINDER)

    ###
    # VOTES
    ###
    def get_votes(self) -> list[VoteMapVote]:
        raw_votes = cast(dict[bytes, bytes], self.client.hgetall(self.VOTES))
        return [pickle.loads(vote) for _, vote in raw_votes.items()]

    def delete_votes(self):
        self.client.delete(self.VOTES)

    def get_vote(self, player_id: str) -> VoteMapVote | None:
        vote = cast(bytes | None, self.client.hget(self.VOTES, player_id))
        if not vote:
            return None
        return pickle.loads(vote)

    def add_vote(
        self, player_id: str, player_name: str, map: Layer, vote_count: int = 1
    ):
        vote = pickle.dumps(
            {
                "player_id": player_id,
                "player_name": player_name,
                "map_id": map.id,
                "vote_count": vote_count,
            }
        )
        self.client.hset(self.VOTES, player_id, cast(Any, vote))

    def delete_vote(self, player_id):
        self.client.hdel(self.VOTES, player_id)

    ###
    # MAP WHITELIST
    ###
    def get_whitelist(self) -> list[Layer]:
        raw = cast(set[bytes], self.client.smembers(self.MAP_WHITELIST))
        uniques = {item.decode() for item in raw}
        return [self._parse_layer(map_id) for map_id in uniques]

    def add_map_to_whitelist(self, map: Layer):
        self.client.sadd(self.MAP_WHITELIST, map.id)

    def remove_map_from_whitelist(self, map: Layer):
        self.client.srem(self.MAP_WHITELIST, map.id)

    def set_whitelist(self, maps: Iterable[Layer]):
        self.client.delete(self.MAP_WHITELIST)
        self.client.sadd(self.MAP_WHITELIST, *[map.id for map in maps])

    ###
    # MAP SELECTION
    ###
    def get_selection(self) -> list[Layer]:
        # Get all map ids in order
        raw = cast(set[bytes], self.client.zrange(self.MAP_SELECTION, 0, -1))
        return [self._parse_layer(item.decode()) for item in raw]

    def set_selection(self, maps: Iterable[Layer]):
        self.delete_selection()
        # Add each map_id with its index as score
        for idx, map in enumerate(maps):
            map_id = map.id
            self.client.zadd(self.MAP_SELECTION, {map_id: idx})

    def remove_map_from_selection(self, map: Layer):
        self.client.zrem(self.MAP_SELECTION, map.id)

    def delete_selection(self):
        self.client.delete(self.MAP_SELECTION)

    ###
    # NEXT MAP
    ###
    def get_next_map(self) -> Layer | None:
        next_map = cast(bytes | None, self.client.get(self.NEXT_MAP))
        if next_map is None:
            return None
        return self._parse_layer(next_map.decode())

    def set_next_map(self, map: Layer):
        self.client.set(self.NEXT_MAP, map.id)

    def delete_next_map(self):
        self.client.delete(self.NEXT_MAP)

    ###
    # RESULT HISTORY
    ###
    def get_results(self):
        history = FixedLenList[list[VoteMapHistory]](self.RESULT_HISTORY)
        return [
            {
                "map": self._parse_layer(x["map_id"]),
                "ts": x["ts"],
                "results": [
                    {
                        "map": self._parse_layer(r["map_id"]),
                        "votes_count": r["votes_count"],
                    }
                    for r in x["results"]
                ],
            }
            for x in history
        ]

    def add_result(self, status: VoteMapStatus, map_id: str, ts: int):
        results = [
            VoteMapHistoryResult(map_id=str(res["map"]), votes_count=res["votes_count"])
            for res in status["results"]
        ]
        self.results.add(VoteMapHistory(map_id=map_id, ts=ts, results=results))
