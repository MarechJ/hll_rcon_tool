import asyncio
import itertools
from django.urls import path
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer
import pydantic
from enum import Enum
from logging import getLogger

logger = getLogger(__name__)

GROUP_NAME = "barricade"

class ClientRequestType(str, Enum):
    BAN_PLAYERS = "ban_players"
    UNBAN_PLAYERS = "unban_players"
    NEW_REPORT = "new_report"

class ServerRequestType(str, Enum):
    # Make sure the values are method names of BarricadeConsumer
    pass

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

class BarricadeRequestError(Exception):
    pass


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
        match request.request:
            case ClientRequestType.BAN_PLAYERS:
                pass
            case ClientRequestType.UNBAN_PLAYERS:
                pass
            case ClientRequestType.NEW_REPORT:
                pass
            case _:
                logger.warn("Ignoring unknown client request type %s", request.request)
        await self.send_json(request.response_ok().model_dump())

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
