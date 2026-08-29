from datetime import UTC, datetime
from uuid import uuid4

import pytest

from rcon.commands import HLLCommandFailedError
from rcon.models import PlayerID, PlayerName, enter_session
from rcon.types import VipListSyncMethod
from rcon.vip import (
    add_record_to_vip_list,
    clear_default_vip_list,
    create_vip_list,
    delete_vip_list,
    delete_vip_list_record,
    delete_vip_list_records,
    edit_vip_list,
    edit_vip_list_record,
    edit_vip_list_records,
    get_active_vip_records,
    get_default_vip_list,
    get_inactive_vip_records,
    get_player_vip_list_record,
    get_vip_list,
    get_vip_lists_for_server,
    get_vip_record,
    set_default_vip_list,
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


def test_vip_record_uses_known_player_name(vip_list_ids):
    created = create_vip_list(
        name=f"Known player name {uuid4().hex}",
        servers=[1],
    )
    vip_list_id = created["id"]
    vip_list_ids.append(vip_list_id)
    player_id = "0002" + uuid4().hex[4:]

    with enter_session() as sess:
        player = PlayerID(player_id=player_id)
        sess.add(player)
        sess.flush()
        sess.add(
            PlayerName(
                player=player,
                name="Known Player",
            )
        )

    record = add_record_to_vip_list(
        player_id=player_id,
        vip_list_id=vip_list_id,
        description="Manual fallback must not be used",
        admin_name="pytest",
    )

    assert record["player_name"] == "Known Player"
    assert record["description"] is None

    with pytest.raises(
        HLLCommandFailedError,
        match="known player name",
    ):
        edit_vip_list_record(
            record_id=record["id"],
            description="Not allowed",
        )

    with pytest.raises(
        HLLCommandFailedError,
        match="known player name",
    ):
        edit_vip_list_records(
            [record["id"]],
            description="Not allowed in bulk",
        )


def test_bulk_vip_record_operations_are_atomic(vip_list_ids):
    created = create_vip_list(
        name=f"Bulk operations {uuid4().hex}",
        servers=[1],
    )
    vip_list_id = created["id"]
    vip_list_ids.append(vip_list_id)

    records = [
        add_record_to_vip_list(
            player_id="0002" + uuid4().hex[4:],
            vip_list_id=vip_list_id,
            description=f"Original {index}",
            notes=f"Original note {index}",
            admin_name="pytest",
        )
        for index in range(2)
    ]
    record_ids = [record["id"] for record in records]
    missing_id = max(record_ids) + 1_000_000

    target = create_vip_list(
        name=f"Bulk target {uuid4().hex}",
        servers=[1],
    )
    target_id = target["id"]
    vip_list_ids.append(target_id)

    with pytest.raises(HLLCommandFailedError, match=str(missing_id)):
        edit_vip_list_records(
            [record_ids[0], missing_id],
            active=False,
            notes="Must not be applied",
            admin_name="pytest bulk",
        )

    with enter_session() as sess:
        unchanged = get_vip_record(sess, record_ids[0], strict=True)
        assert unchanged is not None
        assert unchanged.active is True
        assert unchanged.notes == "Original note 0"

    expiration = datetime(2035, 1, 1, tzinfo=UTC)
    edited = edit_vip_list_records(
        record_ids,
        description="Bulk description",
        active=False,
        expires_at=expiration,
        notes="Bulk note",
        admin_name="pytest bulk",
    )

    assert [record["id"] for record in edited] == record_ids
    assert all(record["description"] == "Bulk description" for record in edited)
    assert all(record["is_active"] is False for record in edited)
    assert all(record["expires_at"] == expiration for record in edited)
    assert all(record["notes"] == "Bulk note" for record in edited)
    assert all(record["admin_name"] == "pytest bulk" for record in edited)

    duplicate = add_record_to_vip_list(
        player_id=records[0]["player_id"],
        vip_list_id=target_id,
        description="Target duplicate",
        admin_name="pytest",
    )

    with pytest.raises(
        HLLCommandFailedError,
        match="already have records",
    ):
        edit_vip_list_records(
            record_ids,
            vip_list_id=target_id,
            admin_name="pytest move",
        )

    with enter_session() as sess:
        assert all(
            get_vip_record(sess, record_id, strict=True).vip_list_id == vip_list_id
            for record_id in record_ids
        )

    assert delete_vip_list_record(duplicate["id"]) is True

    moved = edit_vip_list_records(
        record_ids,
        vip_list_id=target_id,
        admin_name="pytest move",
    )
    assert all(record["vip_list_id"] == target_id for record in moved)
    assert all(record["description"] == "Bulk description" for record in moved)
    assert all(record["notes"] == "Bulk note" for record in moved)
    assert all(record["is_active"] is False for record in moved)
    assert all(record["admin_name"] == "pytest move" for record in moved)

    with pytest.raises(HLLCommandFailedError, match=str(missing_id)):
        delete_vip_list_records([record_ids[0], missing_id])

    with enter_session() as sess:
        assert get_vip_record(sess, record_ids[0]) is not None
        assert get_vip_record(sess, record_ids[1]) is not None

    assert delete_vip_list_records(record_ids) == 2

    with enter_session() as sess:
        assert get_vip_record(sess, record_ids[0]) is None
        assert get_vip_record(sess, record_ids[1]) is None


def test_default_vip_list_per_server(vip_list_ids):
    first = create_vip_list(
        name=f"Default first {uuid4().hex}",
        servers=[1],
    )
    second = create_vip_list(
        name=f"Default second {uuid4().hex}",
        servers=[1, 2],
    )
    incompatible = create_vip_list(
        name=f"Default incompatible {uuid4().hex}",
        servers=[2],
    )
    first_id = first["id"]
    second_id = second["id"]
    incompatible_id = incompatible["id"]
    vip_list_ids.extend([first_id, second_id, incompatible_id])

    with enter_session() as sess:
        assert get_default_vip_list(sess, 1) is None

    assert set_default_vip_list(1, first_id) == first

    with enter_session() as sess:
        default = get_default_vip_list(sess, 1)
        assert default is not None
        assert default.id == first_id

    assert set_default_vip_list(1, second_id) == second
    assert set_default_vip_list(2, second_id) == second

    with enter_session() as sess:
        server_one_default = get_default_vip_list(sess, 1)
        server_two_default = get_default_vip_list(sess, 2)
        assert server_one_default is not None
        assert server_two_default is not None
        assert server_one_default.id == second_id
        assert server_two_default.id == second_id

    with pytest.raises(
        HLLCommandFailedError,
        match="default for server #2",
    ):
        edit_vip_list(
            second_id,
            servers=[1],
        )

    with enter_session() as sess:
        unchanged_default_list = get_vip_list(
            sess,
            second_id,
            strict=True,
        )
        assert unchanged_default_list is not None
        assert unchanged_default_list.get_server_numbers() == {1, 2}

    with pytest.raises(
        HLLCommandFailedError,
        match="does not apply to server 1",
    ):
        set_default_vip_list(1, incompatible_id)

    with pytest.raises(
        HLLCommandFailedError,
        match="does not apply to server 2",
    ):
        set_default_vip_list(2, first_id)

    with pytest.raises(ValueError, match="between 1 and 32"):
        set_default_vip_list(0, first_id)

    with pytest.raises(ValueError, match="between 1 and 32"):
        set_default_vip_list(33, first_id)

    assert clear_default_vip_list(1) is True
    assert clear_default_vip_list(1) is False

    with enter_session() as sess:
        assert get_default_vip_list(sess, 1) is None
        default = get_default_vip_list(sess, 2)
        assert default is not None
        assert default.id == second_id

    assert delete_vip_list(second_id) is True

    with enter_session() as sess:
        assert get_default_vip_list(sess, 2) is None
