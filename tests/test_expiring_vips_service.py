from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

import rcon.expiring_vips.service as service_module
from rcon.models import enter_session
from rcon.vip import (
    add_record_to_vip_list,
    create_vip_list,
    delete_vip_list,
    get_player_vip_list_record,
    set_default_vip_list,
)


class FakeRcon:
    def __init__(self, vips):
        self.vips = dict(vips)
        self.added = []
        self.removed = []

    def get_vip_ids(self):
        return [
            {
                "player_id": player_id,
                "name": description,
                "vip_expiration": None,
            }
            for player_id, description in self.vips.items()
        ]

    def add_vip_to_gameserver(self, player_id, description):
        self.vips[player_id] = description
        self.added.append((player_id, description))
        return True

    def remove_vip_from_gameserver(self, player_id):
        self.vips.pop(player_id, None)
        self.removed.append(player_id)
        return True


@pytest.fixture
def created_vip_lists():
    created_ids = []
    yield created_ids

    for vip_list_id in reversed(created_ids):
        delete_vip_list(vip_list_id)


def test_expired_service_preserves_vip_granted_by_another_list(
    monkeypatch,
    created_vip_lists,
):
    default_list = create_vip_list(
        name=f"Expiry default {uuid4().hex}",
        servers=[32],
    )
    secondary_list = create_vip_list(
        name=f"Expiry secondary {uuid4().hex}",
        servers=[32],
    )
    created_vip_lists.extend([default_list["id"], secondary_list["id"]])
    set_default_vip_list(32, default_list["id"])

    preserved_player_id = "0002" + uuid4().hex[4:]
    removed_player_id = "0002" + uuid4().hex[4:]
    expired_at = datetime.now(tz=UTC) - timedelta(minutes=5)

    preserved_default = add_record_to_vip_list(
        player_id=preserved_player_id,
        vip_list_id=default_list["id"],
        description="Expired default source",
        expires_at=expired_at,
        admin_name="pytest",
    )
    removed_default = add_record_to_vip_list(
        player_id=removed_player_id,
        vip_list_id=default_list["id"],
        description="Expired only source",
        expires_at=expired_at,
        admin_name="pytest",
    )
    secondary_record = add_record_to_vip_list(
        player_id=preserved_player_id,
        vip_list_id=secondary_list["id"],
        description="Secondary source",
        expires_at=None,
        admin_name="pytest",
    )

    fake_rcon = FakeRcon(
        {
            preserved_player_id: "Old description",
            removed_player_id: "Expired only source",
        }
    )
    audits = []

    monkeypatch.setattr(
        service_module,
        "get_server_number",
        lambda: 32,
    )
    monkeypatch.setattr(
        service_module,
        "send_to_discord_audit",
        lambda **kwargs: audits.append(kwargs),
    )

    service_module.remove_expired_vips(fake_rcon)

    with enter_session() as sess:
        preserved_default_record = get_player_vip_list_record(
            sess,
            player_id=preserved_player_id,
            vip_list_id=default_list["id"],
        )
        removed_default_record = get_player_vip_list_record(
            sess,
            player_id=removed_player_id,
            vip_list_id=default_list["id"],
        )
        remaining_secondary_record = get_player_vip_list_record(
            sess,
            player_id=preserved_player_id,
            vip_list_id=secondary_list["id"],
        )

        assert preserved_default_record is not None
        assert removed_default_record is not None
        assert remaining_secondary_record is not None

        assert preserved_default_record.id == preserved_default["id"]
        assert removed_default_record.id == removed_default["id"]
        assert remaining_secondary_record.id == secondary_record["id"]

        assert preserved_default_record.active is False
        assert removed_default_record.active is False
        assert remaining_secondary_record.active is True

    assert preserved_player_id in fake_rcon.vips
    assert removed_player_id not in fake_rcon.vips
    assert fake_rcon.removed == [removed_player_id]
    assert len(audits) == 2
