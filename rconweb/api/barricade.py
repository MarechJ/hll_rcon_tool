import asyncio
import itertools
from cachetools import TTLCache
from datetime import datetime
from django.urls import path
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
import pydantic
from logging import getLogger

from sqlalchemy import exists, func

from rcon import models
from rcon.blacklist import (
    BlacklistBarricadeWarnOnlineCommand,
    BlacklistCommand,
    BlacklistCommandHandler,
    BlacklistCommandType,
    add_record_to_blacklist,
    get_player_blacklist_records,
    remove_record_from_blacklist,
)
from rcon.barricade import *

logger = getLogger("rconweb")


@database_sync_to_async
def assert_blacklist_exists(blacklist_id: int):
    stmt = exists().where(models.Blacklist.id == blacklist_id)
    with models.enter_session() as sess:
        if not sess.query(stmt):
            raise BarricadeRequestError("Blacklist does not exist")


@database_sync_to_async
def ban_player(player_id: str, blacklist_id: int, reason: str):
    try:
        with models.enter_session() as sess:
            current_records = get_player_blacklist_records(
                sess=sess,
                player_id=player_id,
                include_expired=True,
                include_other_servers=True,
            )
            if current_records:
                return current_records[0].id

        record = add_record_to_blacklist(
            player_id=player_id,
            blacklist_id=blacklist_id,
            reason=reason,
            admin_name="Barricade",
        )
    except:
        logger.exception("Failed to blacklist player %s", player_id)
        return None
    else:
        return str(record["id"])


@database_sync_to_async
def unban_player(record_id: int):
    try:
        remove_record_from_blacklist(record_id=record_id)
        return True
    except:
        logger.exception("Failed to remove blacklist record #%s", record_id)
        return False


@database_sync_to_async
def get_joined_players_since(since: datetime):
    with models.enter_session() as sess:
        rows = (
            sess.query(models.PlayerID.player_id, models.PlayerSession.start)
            .filter(models.PlayerSession.start > since)
            .filter(models.PlayerSession.end.is_(None))
            .order_by(models.PlayerSession.start)
            .join(models.PlayerSession.player)
            .all()
        )
        return rows


@database_sync_to_async
def get_most_recent_session_date():
    with models.enter_session() as sess:
        return sess.query(func.max(models.PlayerSession.start)).scalar()


class BarricadeConsumer(AsyncJsonWebsocketConsumer):
    groups = [GROUP_NAME]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._counter = itertools.count()
        self._waiters: dict[int, asyncio.Future] = {}
        self._processing: set[int] = set()
        self._resp_cache = TTLCache(9999, ttl=60)
        self._last_seen_session = datetime.utcnow()
        self._scan_players_task = None

    async def websocket_connect(self, *args, **kwargs):
        await super().websocket_connect(*args, **kwargs)
        logger.info("Accepted connection with Barricade client")

        if self._scan_players_task and not self._scan_players_task.done():
            self._scan_players_task.cancel()
        self._scan_players_task = asyncio.create_task(self._scan_players_loop())

    async def websocket_disconnect(self, message):
        await super().websocket_disconnect(message)
        logger.info("Closed connection with Barricade client")

        if self._scan_players_task and not self._scan_players_task.done():
            self._scan_players_task.cancel()

    async def _scan_players_loop(self):
        self._last_seen_session = await get_most_recent_session_date()

        while True:
            await asyncio.sleep(60)

            try:
                rows = await get_joined_players_since(self._last_seen_session)
                if not rows:
                    continue

                self._last_seen_session = rows[-1][1]
                await self.send_request(
                    ServerRequestType.SCAN_PLAYERS,
                    ScanPlayersRequestPayload(player_ids=[row[0] for row in rows]),
                )
            except Exception:
                logger.exception("Failed to perform scan_players task")

    async def receive_json(self, content, **kwargs):
        try:
            request = content["request"]
        except KeyError:
            logger.error("Received malformed Barricade request: %s", content)
            return

        try:
            if request:
                await self.handle_request(RequestBody.model_validate(content))
            else:
                await self.handle_response(ResponseBody.model_validate(content))
        except pydantic.ValidationError:
            logger.error("Received malformed Barricade request: %s", content)
            return

    async def send_request(
        self, request_type: ServerRequestType, payload: dict | None
    ) -> dict | None:
        # Send request
        request = RequestBody(
            id=next(self._counter),
            request=request_type,
            payload=payload,
        )
        await self.send_json(request.model_dump())

        # Allocate response waiter
        fut = asyncio.Future()
        self._waiters[request.id] = fut

        try:
            # Wait for response
            response: ResponseBody = await asyncio.wait_for(fut, timeout=10)
        except asyncio.TimeoutError:
            logger.error("Barricade did not respond in time to request: %r", request)
            raise
        except BarricadeRequestError as e:
            logger.error(
                'Barricade returned error "%s" %s for request: %r',
                e.error,
                e.kwargs,
                request,
            )
            raise
        finally:
            # Remove waiter
            if request.id in self._waiters:
                del self._waiters[request.id]

        return response.response

    async def handle_request(self, request: RequestBody):
        if request.id in self._processing:
            return

        if cached_response := self._resp_cache.get(request.id):
            await self.send_json(cached_response)
            return

        try:
            self._processing.add(request.id)

            try:
                result = None

                match request.request:
                    case ClientRequestType.BAN_PLAYERS:
                        result = await self.ban_players(
                            BanPlayersRequestPayload.model_validate(request.payload)
                        )
                    case ClientRequestType.UNBAN_PLAYERS:
                        result = await self.unban_players(
                            UnbanPlayersRequestPayload.model_validate(request.payload)
                        )
                    case ClientRequestType.NEW_REPORT:
                        result = await self.new_report(
                            NewReportRequestPayload.model_validate(request.payload)
                        )
                    case _:
                        raise BarricadeRequestError("No such command")

                response = request.response_ok(result)

            except pydantic.ValidationError as e:
                logger.warn("Failed to validate payload: %s", e)
                response = request.response_error("Failed to validate payload")
            except BarricadeRequestError as e:
                # These should indicate a client error...
                response = request.response_error(e.error, **e.kwargs)
            except Exception as e:
                # ...whereas these typically indicate a server error
                logger.error(
                    "Internal error when handling Barricade request: %r",
                    request,
                    exc_info=e,
                )
                response = request.response_error(f"{type(e).__name__}: {e}")

            # Respond
            dumped_response = response.model_dump()
            self._resp_cache[response.id] = dumped_response
            await self.send_json(dumped_response)

        finally:
            self._processing.remove(request.id)

    async def handle_response(self, response: ResponseBody):
        waiter = self._waiters.get(response.id)

        # Make sure response is being awaited
        if not waiter:
            logger.warning(
                "Discarding response since it is not being awaited: %r", response
            )
            return

        # Make sure waiter is still available
        if waiter.done():
            logger.warning(
                "Discarding response since waiter is already marked done: %r", response
            )
            return

        # Set response
        if response.failed:
            waiter.set_exception(BarricadeRequestError(**response.response))
        else:
            waiter.set_result(response.response)

    async def handle_broadcast(self, event):
        try:
            return await self.send_request(event["request_type"], event["payload"])
        except (asyncio.TimeoutError, BarricadeRequestError):
            # These are already logged by send_request
            pass

    async def ban_players(self, payload: BanPlayersRequestPayload):
        if payload.config.banlist_id is None:
            raise BarricadeRequestError("Missing config.banlist_id")

        try:
            blacklist_id = int(payload.config.banlist_id)
        except ValueError:
            raise BarricadeRequestError("Invalid banlist ID")

        await assert_blacklist_exists(blacklist_id)

        record_ids = await asyncio.gather(
            *[
                # The client expects strings, not ints
                ban_player(
                    player_id=player_id,
                    blacklist_id=blacklist_id,
                    reason=reason or payload.config.reason,
                )
                for player_id, reason in payload.player_ids.items()
            ]
        )

        return {"ban_ids": dict(zip(payload.player_ids.keys(), record_ids))}

    async def unban_players(self, payload: UnbanPlayersRequestPayload):
        record_ids = []
        for record_id in payload.record_ids:
            try:
                record_id = int(record_id)
            except ValueError:
                continue
            record_ids.append(record_id)

        successes = await asyncio.gather(
            *[unban_player(record_id) for record_id in record_ids]
        )

        successful_record_ids = [
            record_id
            for record_id, success in zip(payload.record_ids, successes)
            if success
        ]

        response = {"ban_ids": successful_record_ids}

        if len(successful_record_ids) != len(payload.record_ids):
            raise BarricadeRequestError("Could not unban all players", **response)
        else:
            return response

    async def new_report(self, payload: NewReportRequestPayload):
        BlacklistCommandHandler.send(
            BlacklistCommand(
                command=BlacklistCommandType.BARRICADE_WARN_ONLINE,
                server_mask=None,
                payload=BlacklistBarricadeWarnOnlineCommand(
                    player_ids=[player.player_id for player in payload.players]
                ).model_dump(),
            )
        )


from api.auth import APITokenAuthMiddleware

urlpatterns = [
    path(
        "ws/barricade",
        APITokenAuthMiddleware(
            app=BarricadeConsumer.as_asgi(),
            perms=(
                "api.can_view_blacklists",
                "api.can_create_blacklists",
                "api.can_add_blacklist_records",
                "api.can_change_blacklist_records",
                "api.can_delete_blacklist_records",
            ),
        ),
    )
]
