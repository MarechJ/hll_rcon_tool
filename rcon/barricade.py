from datetime import datetime
from enum import Enum

import os
import pydantic
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.conf import settings as django_settings
django_settings.configure(CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                {
                    "address": os.getenv("HLL_REDIS_URL"),
                }
            ],
        },
    },
})

GROUP_NAME = "barricade"


class ClientRequestType(str, Enum):
    BAN_PLAYERS = "ban_players"
    UNBAN_PLAYERS = "unban_players"
    NEW_REPORT = "new_report"


class ServerRequestType(str, Enum):
    SCAN_PLAYERS = "scan_players"


class RequestBody(pydantic.BaseModel):
    id: int
    request: ClientRequestType | ServerRequestType
    payload: dict | None = None

    def response_ok(self, payload: dict | None = None):
        return ResponseBody(id=self.id, response=payload)

    def response_error(self, error: str, **kwargs: str):
        return ResponseBody(
            id=self.id, response={"error": error, **kwargs}, failed=True
        )


class ResponseBody(pydantic.BaseModel):
    id: int
    request: None = None
    response: dict | None
    failed: bool = False


class UnbanPlayersRequestConfigPayload(pydantic.BaseModel):
    banlist_id: str


class BanPlayersRequestConfigPayload(UnbanPlayersRequestConfigPayload):
    reason: str


class BanPlayersRequestPayload(pydantic.BaseModel):
    player_ids: dict[str, str | None]
    config: BanPlayersRequestConfigPayload


class ScanPlayersRequestPayload(pydantic.BaseModel):
    player_ids: list[str]


class UnbanPlayersRequestPayload(pydantic.BaseModel):
    # Even though in theory these can all be converted to ints, we should safely
    # filter out all invalid record IDs later.
    record_ids: list[str] = pydantic.Field(alias="ban_ids")
    config: UnbanPlayersRequestConfigPayload


class NewReportRequestPayloadPlayer(pydantic.BaseModel):
    player_id: str
    player_name: str
    bm_rcon_url: str | None


class NewReportRequestPayload(pydantic.BaseModel):
    created_at: datetime
    body: str
    reasons: list[str]
    attachment_urls: list[str]
    players: list[NewReportRequestPayloadPlayer]


class BarricadeRequestError(Exception):
    def __init__(self, error: str, **kwargs: str) -> None:
        self.error = error
        self.kwargs = kwargs

    def __str__(self) -> str:
        return self.error


def send_to_barricade(request_type: ServerRequestType, payload: dict | None):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        GROUP_NAME,
        {
            "type": "handle_broadcast",
            "request_type": request_type.value,
            "payload": payload,
        },
    )
