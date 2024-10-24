import asyncio
from logging import getLogger
from typing import Generator, TypedDict

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.urls import path

from rcon.game_logs import LogStream, is_action
from rcon.types import AllLogTypes, StructuredLogLineWithMetaData
from rcon.user_config.log_stream import LogStreamUserConfig
from rcon.utils import StreamID, StreamInvalidID

logger = getLogger(__name__)


class LogStreamObject(TypedDict):
    id: StreamID
    log: list[StructuredLogLineWithMetaData]


class LogStreamResponse(TypedDict):
    logs: list[LogStreamObject]
    last_seen_id: StreamID | None
    error: str | None


class LogStreamConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connected = False

    async def websocket_connect(self, *args, **kwargs):
        self.connected = True
        await super().websocket_connect(*args, **kwargs)

    async def websocket_disconnect(self, *args, **kwargs):
        self.connected = False
        await super().websocket_disconnect(*args, **kwargs)

    async def receive_json(self, content, **kwargs):
        config = LogStreamUserConfig.load_from_db()

        if not config.enabled:
            response: LogStreamResponse = {
                "error": "Log stream is not enabled in your config",
                # TODO: should this be None?
                "last_seen_id": None,
                "logs": [],
            }
            await self.send_json(response)
            return await self.websocket_disconnect()

        last_seen: StreamID = content.get("last_seen_id")
        raw_actions: list[str] | None = content.get("actions")

        try:
            actions_filter: list[AllLogTypes]
            if raw_actions:
                actions_filter = [AllLogTypes(v.upper()) for v in raw_actions]
            else:
                actions_filter = []
        except ValueError as e:
            logger.error(e)
            response: LogStreamResponse = {
                "error": str(e),
                # TODO: should this be None?
                "last_seen_id": None,
                "logs": [],
            }
            await self.send_json(response)
            return await self.websocket_disconnect()

        send_all = False
        if len(actions_filter) == 0:
            send_all = True

        def batch_logs(
            logs: list[LogStreamObject], size=25
        ) -> Generator[list[LogStreamObject], None, None]:
            size = max(size, 1)
            return (logs[i : i + size] for i in range(0, len(logs), size))

        log_stream = LogStream()
        while self.connected:
            config = LogStreamUserConfig.load_from_db()

            if not config.enabled:
                response: LogStreamResponse = {
                    "error": "Log stream is not enabled in your config",
                    # TODO: should this be None?
                    "last_seen_id": None,
                    "logs": [],
                }
                await self.send_json(response)
                return await self.websocket_disconnect()

            try:
                logs = log_stream.logs_since(last_seen=last_seen)
                json_logs: list[LogStreamObject] = []
                if logs:
                    for id_, log in logs:
                        last_seen = id_
                        if send_all or is_action(
                            actions_filter, log["action"], exact_match=False
                        ):
                            json_logs.append({"id": id_, "log": log})

                    if json_logs:
                        for batch in batch_logs(json_logs):
                            response: LogStreamResponse = {
                                "last_seen_id": batch[-1]["id"],
                                "logs": batch,
                                "error": None,
                            }
                            await self.send_json(response)

            except StreamInvalidID as e:
                response: LogStreamResponse = {
                    "error": str(e),
                    # TODO: should this be None?
                    "last_seen_id": None,
                    "logs": [],
                }
                await self.send_json(response)
                raise
            await asyncio.sleep(0.3)

    async def send_json(self, content, close=False):
        return await super().send_json(content, close)


from api.auth import APITokenAuthMiddleware

urlpatterns = [
    path(
        "ws/logs",
        APITokenAuthMiddleware(
            app=LogStreamConsumer.as_asgi(), perms="api.can_view_structured_logs"
        ),
    )
]
