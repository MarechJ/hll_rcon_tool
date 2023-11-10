from django.urls import path
from rcon.game_logs import LogStream
from rcon.utils import StreamInvalidID, StreamID
from typing import TypedDict


from channels.generic.websocket import JsonWebsocketConsumer
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


class LogStreamConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, code):
        return super().disconnect(code)

    def receive_json(self, content, **kwargs):
        last_seen: StreamID = content.get("last_seen_id")
        log_stream = LogStream()
        try:
            while True:
                try:
                    logs = log_stream.logs_since(last_seen=last_seen)
                    json_logs = []
                    for id_, log in logs:
                        json_logs.append({"id": id_, "logs": log})
                    response: LogStreamResponse = {
                        "last_seen_id": last_seen,
                        "logs": json_logs,
                        "error": None,
                    }

                    if logs:
                        self.send_json(response)
                        last_seen = logs[-1][0]

                except StreamInvalidID as e:
                    response: LogStreamResponse = {
                        "error": str(e),
                        "last_seen_id": None,
                        "logs": [],
                    }
                    self.send_json(response)
                    raise
        except Exception as e:
            logger.exception(e)
            self.disconnect(1)

    def send_json(self, content, close=False):
        return super().send_json(content, close)


urlpatterns = [path("ws/logs", LogStreamConsumer.as_asgi())]
