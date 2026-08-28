from datetime import UTC, datetime
from uuid import uuid4

import pytest

from rcon.commands import HLLCommandFailedError
from rcon.models import enter_session
from rcon.types import VipListSyncMethod
from rcon.vip import (
    add_record_to_vip_list,
    create_vip_list,
    delete_vip_list,
    delete_vip_list_record,
    edit_vip_list,
    edit_vip_list_record,
    get_active_vip_records,
    get_inactive_vip_records,
    get_player_vip_list_record,
    get_vip_list,
    get_vip_lists_for_server,
)


@pytest.fixture
def vip_list_ids():
    created_ids: list[int] = []
    yield created_ids

    for vip_list_id in reversed(created_ids):
        delete_vip_list(vip_list_id)


def test_vip_list_crud_and_server_scope(vip_list_ids):
    created = create_vip_list(
        name=f"Test list {uuid4().hex}",
        servers=[1, 2],
    )
    vip_list_id = created["id"]
    vip_list_ids.append(vip_list_id)

    assert created["sync"] == VipListSyncMethod.IGNORE_UNKNOWN
    assert created["servers"] == [1, 2]

    with enter_session() as sess:
        assert get_vip_list(sess, vip_list_id, strict=True) is not None
        assert vip_list_id in {item.id for item in get_vip_lists_for_server(sess, 1)}
        assert vip_list_id in {item.id for item in get_vip_lists_for_server(sess, 2)}
        assert vip_list_id not in {
            item.id for item in get_vip_lists_for_server(sess, 3)
        }

    edited = edit_vip_list(
        vip_list_id,
        name="Edited test list",
        sync=VipListSyncMethod.REMOVE_UNKNOWN,
        servers=None,
    )

    assert edited["name"] == "Edited test list"
    assert edited["sync"] == VipListSyncMethod.REMOVE_UNKNOWN
    assert edited["servers"] is None

    with enter_session() as sess:
        assert vip_list_id in {item.id for item in get_vip_lists_for_server(sess, 32)}


@pytest.mark.parametrize(
    "player_id",
    [
        "",
        "player-id",
        "88d99bf432e8de4f58c43d1c2d22",
    ],
)
def test_rejects_unsupported_player_id(vip_list_ids, player_id):
    created = create_vip_list(
        name=f"Invalid ID test {uuid4().hex}",
        servers=[1],
    )
    vip_list_id = created["id"]
    vip_list_ids.append(vip_list_id)

    with pytest.raises(ValueError, match="Player ID must be"):
        add_record_to_vip_list(
            player_id=player_id,
            vip_list_id=vip_list_id,
        )


@pytest.mark.parametrize(
    "player_id",
    [
        pytest.param("76561199999999998", id="hll-steam64"),
        pytest.param("0002" + uuid4().hex[4:], id="hllv-eos"),
    ],
)
def test_vip_record_crud_and_duplicate_protection(
    vip_list_ids,
    player_id,
):
    source = create_vip_list(
        name=f"Source {uuid4().hex}",
        servers=[1],
    )
    target = create_vip_list(
        name=f"Target {uuid4().hex}",
        servers=[2],
    )
    source_id = source["id"]
    target_id = target["id"]
    vip_list_ids.extend([source_id, target_id])

    expiration = datetime(2032, 1, 1, tzinfo=UTC)

    record = add_record_to_vip_list(
        player_id=player_id,
        vip_list_id=source_id,
        description="Public description",
        notes="Internal note",
        expires_at=expiration,
        admin_name="pytest",
    )
    record_id = record["id"]

    assert record["player_id"] == player_id
    assert record["expires_at"] == expiration
    assert record["is_active"] is True
    assert record["is_expired"] is False

    with pytest.raises(HLLCommandFailedError):
        add_record_to_vip_list(
            player_id=player_id,
            vip_list_id=source_id,
        )

    with enter_session() as sess:
        assert record_id in {
            item.id for item in get_active_vip_records(sess, source_id)
        }

    edited = edit_vip_list_record(
        record_id,
        description="Updated description",
        notes=None,
        active=False,
        admin_name="pytest editor",
    )

    assert edited["description"] == "Updated description"
    assert edited["notes"] is None
    assert edited["is_active"] is False
    assert edited["admin_name"] == "pytest editor"

    with enter_session() as sess:
        assert record_id in {
            item.id for item in get_inactive_vip_records(sess, source_id)
        }

    moved = edit_vip_list_record(
        record_id,
        vip_list_id=target_id,
        active=True,
        admin_name="pytest mover",
    )
    assert moved["vip_list_id"] == target_id

    with enter_session() as sess:
        assert (
            get_player_vip_list_record(
                sess,
                player_id,
                source_id,
            )
            is None
        )
        assert (
            get_player_vip_list_record(
                sess,
                player_id,
                target_id,
            )
            is not None
        )

    assert delete_vip_list_record(record_id) is True
    assert delete_vip_list_record(record_id) is False
