from django.urls import path
from rcon.game_logs import LogStream
from rcon.utils import StreamInvalidID, StreamID
from typing import TypedDict
import asyncio


from channels.generic.websocket import AsyncJsonWebsocketConsumer
from logging import getLogger
from rcon.types import StructuredLogLineWithMetaData

logger = getLogger(__name__)


class LogStreamObject(TypedDict):
    id: StreamID
    logs: list[StructuredLogLineWithMetaData]


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
        self.conencted = False
        await super().websocket_disconnect(*args, **kwargs)

    async def receive_json(self, content, **kwargs):
        last_seen: StreamID = content.get("last_seen_id")
        log_stream = LogStream()
        while self.connected:
            try:
                logs = log_stream.logs_since(last_seen=last_seen)
                json_logs = []
                for id_, log in logs:
                    json_logs.append({"id": id_, "logs": log})
                    last_seen = id_

                if json_logs:
                    response: LogStreamResponse = {
                        "last_seen_id": last_seen,
                        "logs": json_logs,
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
            await asyncio.sleep(0.5)

    async def send_json(self, content, close=False):
        return await super().send_json(content, close)


urlpatterns = [path("ws/logs", LogStreamConsumer.as_asgi())]
