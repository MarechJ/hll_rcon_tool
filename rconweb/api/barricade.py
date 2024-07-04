import asyncio
import datetime
import itertools
from django.urls import path
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer
import pydantic
from enum import Enum
from logging import getLogger

from sqlalchemy import exists

from rcon import models
from rcon.api_commands import get_rcon_api
from rcon.blacklist import BlacklistBarricadeWarnOnlineCommand, BlacklistCommand, BlacklistCommandHandler, BlacklistCommandType, add_record_to_blacklist, remove_record_from_blacklist

logger = getLogger(__name__)

GROUP_NAME = "barricade"

class ClientRequestType(str, Enum):
    BAN_PLAYERS = "ban_players"
    UNBAN_PLAYERS = "unban_players"
    NEW_REPORT = "new_report"

class ServerRequestType(str, Enum):
    ALERT_PLAYER = "alert_player"

class RequestBody(pydantic.BaseModel):
    id: int
    request: ClientRequestType | ServerRequestType
    payload: dict | None = None

    def response_ok(self, payload: dict | None = None):
        return ResponseBody(id=self.id, response=payload)

    def response_error(self, error: str):
        return ResponseBody(id=self.id, response={'error': error}, failed=True)

class ResponseBody(pydantic.BaseModel):
    id: int
    request: None = None
    response: dict | None
    failed: bool = False

class ClientConfig(pydantic.BaseModel):
    blacklist_id: int
    reason: str

class RequestPayload(pydantic.BaseModel):
    config: ClientConfig

class BanPlayersRequestPayload(RequestPayload):
    player_ids: dict[str, str | None]

class AlertPlayerRequestPayload(pydantic.BaseModel):
    player_ids: list[str]

class UnbanPlayersRequestPayload(RequestPayload):
    # Even though in theory these can all be converted to ints, we should safely
    # filter out all invalid record IDs later.
    record_ids: list[str] = pydantic.Field(alias="ban_ids")

class NewReportRequestPayloadPlayer(pydantic.BaseModel):
    player_id: int
    player_name: str
    bm_rcon_url: str | None
class NewReportRequestPayload(RequestPayload):
    created_at: datetime
    body: str
    reasons: list[str]
    attachment_urls: list[str]
    players: list[NewReportRequestPayloadPlayer]

class BarricadeRequestError(Exception):
    pass

@database_sync_to_async
def assert_blacklist_exists(blacklist_id: int):
    stmt = exists().where(models.Blacklist.id == blacklist_id)
    with models.enter_session() as sess:
        if not sess.query(stmt):
            raise BarricadeRequestError("Blacklist does not exist")

@database_sync_to_async
def ban_player(player_id: str, blacklist_id: int, reason: str):
    try:
        record = add_record_to_blacklist(
            player_id=player_id,
            blacklist_id=blacklist_id,
            reason=reason,
            admin_name="Barricade"
        )
    except:
        logger.exception("Failed to blacklist player %s", player_id)
        return None
    else:
        return record["id"]

@database_sync_to_async
def unban_player(record_id: int):
    try:
        return remove_record_from_blacklist(
            record_id=record_id
        )
    except:
        logger.exception("Failed to remove blacklist record #%s", record_id)
        return False
    

class BarricadeConsumer(AsyncJsonWebsocketConsumer):
    groups = [GROUP_NAME]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._counter = itertools.count()
        self._waiters: dict[int, asyncio.Future] = {}

    async def websocket_connect(self, *args, **kwargs):
        await super().websocket_connect(*args, **kwargs)
        logger.info("Accepted connection with Barricade client")
    
    async def websocket_disconnect(self, message):
        await super().websocket_disconnect(message)
        logger.info("Closed connection with Barricade client")

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

    async def send_request(self, request_type: ServerRequestType, payload: dict | None) -> dict | None:
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
            logger.error("Barricade returned error \"%s\" for request: %r", e, request)
            raise
        finally:
            # Remove waiter
            if request.id in self._waiters:
                del self._waiters[request.id]
        
        return response.response
        
    async def handle_request(self, request: RequestBody):
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
                    raise BarricadeRequestError("Unknown request type")
            
            response = request.response_ok(result)
                
        except pydantic.ValidationError as e:
            logger.warn("Failed to validate payload: %s", e)
            response = request.response_error("Failed to validate payload")
        except BarricadeRequestError as e:
            # These should indicate a client error...
            response = request.response_error(str(e))
        except Exception as e:
            # ...whereas these typically indicate a server error
            response = request.response_error(f"{type(e).__name__}: {e}")
        
        # Respond
        await self.send_json(response.model_dump())

    async def handle_response(self, response: ResponseBody):
        waiter = self._waiters.get(response.id)

        # Make sure response is being awaited
        if not waiter:
            logger.warning("Discarding response since it is not being awaited: %r", response)
            return
        
        # Make sure waiter is still available
        if waiter.done():
            logger.warning("Discarding response since waiter is already marked done: %r", response)
            return
        
        # Set response
        if response.failed:
            waiter.set_exception(
                BarricadeRequestError(response.response.get("error", ""))
            )
        else:
            waiter.set_result(response.response)
    
    async def handle_broadcast(self, event):
        try:
            return await self.send_request(event["request_type"], event["payload"])
        except (asyncio.TimeoutError, BarricadeRequestError):
            # These are already logged by send_request
            pass

    async def ban_players(self, payload: BanPlayersRequestPayload):
        blacklist_id = payload.config.blacklist_id
        
        await assert_blacklist_exists(blacklist_id)

        record_ids = await asyncio.gather(*[
            # The client expects strings, not ints
            str(ban_player(
                player_id=player_id,
                blacklist_id=blacklist_id,
                reason=reason,
            ))
            for player_id, reason in payload.player_ids
        ])

        return {"ban_ids": dict(zip(payload.player_ids.keys(), record_ids))}

    async def unban_players(self, payload: UnbanPlayersRequestPayload):
        successes = await asyncio.gather(*[
            unban_player(record_id)
            for record_id in payload.record_ids
        ])

        return {"ban_ids": dict(zip(payload.record_ids, successes))}

    async def new_report(self, payload: NewReportRequestPayload):
        BlacklistCommandHandler.send(
            BlacklistCommand(
                command=BlacklistCommandType.CREATE_RECORD,
                payload=BlacklistBarricadeWarnOnlineCommand(
                    player_ids=[player.player_id for player in payload.players]
                )
            )
        )


def send_to_barricade(request_type: ServerRequestType, payload: dict | None):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        GROUP_NAME,
        {
            "type": "handle_broadcast",
            "request_type": request_type.value,
            "payload": payload
        }
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
            )
        )
    )
]
