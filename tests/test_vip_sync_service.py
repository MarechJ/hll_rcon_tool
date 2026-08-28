from datetime import UTC, datetime
from types import SimpleNamespace

from rcon.vip_sync_service import (
    database_record_to_sync_record,
    get_record_player_name,
    read_gameserver_vips,
)


NOW = datetime(2030, 1, 1, tzinfo=UTC)


def database_record(*, names, description="Supporter"):
    return SimpleNamespace(
        player=SimpleNamespace(
            player_id="player-1",
            names=[SimpleNamespace(name=name) for name in names],
        ),
        description=description,
        active=True,
        created_at=NOW,
        expires_at=None,
    )


class FakeRcon:
    def __init__(self, vips):
        self.vips = vips

    def get_vip_ids(self):
        return self.vips


def test_uses_first_database_name():
    record = database_record(names=["Newest", "Older"])

    assert get_record_player_name(record) == "Newest"


def test_missing_database_name_returns_empty_string():
    record = database_record(names=[])

    assert get_record_player_name(record) == ""


def test_database_record_conversion():
    record = database_record(names=["Player"])

    converted = database_record_to_sync_record(record)

    assert converted.player_id == "player-1"
    assert converted.player_name == "Player"
    assert converted.description == "Supporter"
    assert converted.active is True
    assert converted.created_at == NOW
    assert converted.expires_at is None


def test_reads_hll_gameserver_vips():
    rcon = FakeRcon(
        [
            {
                "player_id": "76561198080212634",
                "name": "Player",
                "vip_expiration": None,
            }
        ]
    )

    assert read_gameserver_vips(rcon) == {"76561198080212634": "Player"}


def test_reads_empty_hllv_comment():
    rcon = FakeRcon(
        [
            {
                "player_id": "00025182eb1149fabc454d25847b690e",
                "name": "",
                "vip_expiration": None,
            }
        ]
    )

    assert read_gameserver_vips(rcon) == {"00025182eb1149fabc454d25847b690e": ""}
