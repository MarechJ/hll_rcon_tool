from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from rcon.commands import HLLCommandFailedError
from rcon.models import PlayerFlag, PlayerID, PlayerName, enter_session
from rcon.player_history import remove_flag
from rcon.types import VipListSyncMethod
from rcon.vip import (
    add_record_to_vip_list,
    apply_vip_list_expiration,
    clear_default_vip_list,
    create_vip_list,
    deactivate_all_default_vip_records,
    deactivate_default_vip_record,
    delete_vip_list,
    delete_vip_list_record,
    delete_vip_list_records,
    edit_vip_list,
    edit_vip_list_record,
    edit_vip_list_records,
    get_active_vip_records,
    get_default_vip_list,
    get_effective_vip_records,
    get_inactive_vip_records,
    get_player_vip_list_record,
    get_vip_list,
    get_vip_lists_for_server,
    get_vip_record,
    set_default_vip_list,
    upsert_default_vip_record,
)


def test_list_default_duration_requires_explicit_apply_to_existing(vip_list_ids):
    player_id = "76561199988877766"
    listing = create_vip_list(f"Duration {uuid4().hex}")
    vip_list_ids.append(listing["id"])
    initial = add_record_to_vip_list(player_id, listing["id"])
    assert initial["expires_at"] is None

    edit_vip_list(listing["id"], default_expiration_seconds=86400)
    with enter_session() as sess:
        assert get_vip_record(sess, initial["id"]).expires_at is None

    assert apply_vip_list_expiration(listing["id"], 86400) == 1
    with enter_session() as sess:
        expiration = get_vip_record(sess, initial["id"]).expires_at
        assert datetime.now(UTC) + timedelta(hours=23) < expiration
        assert expiration < datetime.now(UTC) + timedelta(hours=25)

    with pytest.raises(HLLCommandFailedError, match="duration changed"):
        apply_vip_list_expiration(listing["id"], None)

    edit_vip_list_record(
        initial["id"], expires_at=datetime.now(UTC) - timedelta(days=1)
    )
    assert apply_vip_list_expiration(listing["id"], 86400) == 0
    assert apply_vip_list_expiration(listing["id"], 86400, include_expired=True) == 1


def test_no_default_and_never_expire_are_distinct(vip_list_ids):
    listing = create_vip_list(f"Duration modes {uuid4().hex}")
    vip_list_ids.append(listing["id"])
    assert listing["default_expiration_seconds"] is None
    with pytest.raises(HLLCommandFailedError, match="no default duration"):
        apply_vip_list_expiration(listing["id"], None)

    listing = edit_vip_list(listing["id"], default_expiration_seconds=0)
    assert listing["default_expiration_seconds"] == 0
    record = add_record_to_vip_list(
        "76561199988877764",
        listing["id"],
        expires_at=datetime.now(UTC) + timedelta(days=1),
    )
    assert record["expires_at"] is not None
    assert apply_vip_list_expiration(listing["id"], 0) == 1
    with enter_session() as sess:
        assert get_vip_record(sess, record["id"]).expires_at is None
    record = add_record_to_vip_list("76561199988877763", listing["id"])
    assert record["expires_at"] is None
    assert apply_vip_list_expiration(listing["id"], 0) == 0

    edit_vip_list(listing["id"], default_expiration_seconds=None)
    with pytest.raises(HLLCommandFailedError, match="duration changed"):
        apply_vip_list_expiration(listing["id"], 0)


def test_list_flags_preserve_manual_flags_and_other_lists(vip_list_ids):
    player_id = "76561199988877765"
    first = create_vip_list(f"Flag first {uuid4().hex}", flags=["🔫", "member"])
    second = create_vip_list(f"Flag second {uuid4().hex}", flags=["🔫"])
    vip_list_ids.extend([first["id"], second["id"]])

    with enter_session() as sess:
        player = sess.query(PlayerID).filter_by(player_id=player_id).one_or_none()
        if player is None:
            player = PlayerID(player_id=player_id)
            sess.add(player)
            sess.flush()
        sess.add(PlayerFlag(player=player, flag="member", comment="Manual"))

    first_record = add_record_to_vip_list(player_id, first["id"])
    second_record = add_record_to_vip_list(player_id, second["id"])
    with enter_session() as sess:
        player = sess.query(PlayerID).filter_by(player_id=player_id).one()
        flags = {flag.flag: flag for flag in player.flags}
        assert flags["member"].managed_by_vip_list is False
        assert flags["🔫"].managed_by_vip_list is True

    with pytest.raises(HLLCommandFailedError, match="managed by a VIP list"):
        remove_flag(player_id=player_id, flag="🔫")

    delete_vip_list_record(first_record["id"])
    with enter_session() as sess:
        player = sess.query(PlayerID).filter_by(player_id=player_id).one()
        assert {flag.flag for flag in player.flags} == {"member", "🔫"}

    delete_vip_list_record(second_record["id"])
    with enter_session() as sess:
        player = sess.query(PlayerID).filter_by(player_id=player_id).one()
        assert {flag.flag for flag in player.flags} == {"member"}
        for flag in player.flags:
            sess.delete(flag)


def test_expired_list_record_loses_managed_flag(vip_list_ids):
    player_id = "76561199988877764"
    listing = create_vip_list(f"Expiring flag {uuid4().hex}", flags=["🌱"])
    vip_list_ids.append(listing["id"])
    record = add_record_to_vip_list(player_id, listing["id"])

    edit_vip_list_record(
        record["id"], expires_at=datetime.now(UTC) - timedelta(seconds=1)
    )
    with enter_session() as sess:
        player = sess.query(PlayerID).filter_by(player_id=player_id).one()
        assert all(flag.flag != "🌱" for flag in player.flags)


def test_list_default_duration_applies_only_when_expiration_is_omitted(vip_list_ids):
    listing = create_vip_list(
        f"New VIP duration {uuid4().hex}", default_expiration_seconds=7200
    )
    vip_list_ids.append(listing["id"])
    default_record = add_record_to_vip_list("76561199988877763", listing["id"])
    override_record = add_record_to_vip_list(
        "76561199988877762", listing["id"], expires_at=None
    )
    assert default_record["expires_at"] > datetime.now(UTC) + timedelta(hours=1)
    assert override_record["expires_at"] is None


def test_legacy_default_list_membership_updates_managed_flags(vip_list_ids):
    player_id = "76561199988877761"
    listing = create_vip_list(f"Legacy flags {uuid4().hex}", flags=["legacy-member"])
    vip_list_ids.append(listing["id"])
    with enter_session() as sess:
        previous_default = get_default_vip_list(sess, 32)
        previous_default_id = previous_default.id if previous_default else None
    set_default_vip_list(32, listing["id"])
    try:
        upsert_default_vip_record(player_id, 32)
        with enter_session() as sess:
            player = sess.query(PlayerID).filter_by(player_id=player_id).one()
            assert "legacy-member" in {flag.flag for flag in player.flags}

        deactivate_default_vip_record(player_id, 32)
        with enter_session() as sess:
            player = sess.query(PlayerID).filter_by(player_id=player_id).one()
            assert "legacy-member" not in {flag.flag for flag in player.flags}
    finally:
        if previous_default_id is None:
            clear_default_vip_list(32)
        else:
            set_default_vip_list(32, previous_default_id)


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
        assert vip_list_id in {item.id for item in get_vip_lists_for_server(sess, "1")}
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


def test_default_vip_list_per_server(
    vip_list_ids,
    isolated_default_vip_lists,
):
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


def test_default_vip_record_compatibility_helpers(
    vip_list_ids,
    isolated_default_vip_lists,
):
    default_list = create_vip_list(
        name=f"Default compatibility {uuid4().hex}",
        servers=[1],
    )
    secondary_list = create_vip_list(
        name=f"Secondary compatibility {uuid4().hex}",
        servers=[1],
    )
    vip_list_ids.extend([default_list["id"], secondary_list["id"]])
    set_default_vip_list(1, default_list["id"])

    player_id = "0002" + uuid4().hex[4:]
    finite_expiration = datetime(2030, 1, 1, tzinfo=UTC)

    created = upsert_default_vip_record(
        player_id=player_id,
        server_number=1,
        description="Legacy API",
        expires_at=finite_expiration,
    )
    updated = upsert_default_vip_record(
        player_id=player_id,
        server_number=1,
        description="Legacy API updated",
        expires_at=finite_expiration,
    )

    assert updated["id"] == created["id"]
    assert updated["is_active"] is True

    add_record_to_vip_list(
        player_id=player_id,
        vip_list_id=secondary_list["id"],
        expires_at=None,
        admin_name="Secondary source",
    )

    with enter_session() as sess:
        effective = get_effective_vip_records(
            sess,
            server_number=1,
        )
        assert effective[player_id].vip_list_id == secondary_list["id"]

    assert deactivate_default_vip_record(player_id, 1) is True

    with enter_session() as sess:
        default_record = get_player_vip_list_record(
            sess,
            player_id=player_id,
            vip_list_id=default_list["id"],
        )
        assert default_record is not None
        assert default_record.active is False

        effective = get_effective_vip_records(
            sess,
            server_number=1,
        )
        assert effective[player_id].vip_list_id == secondary_list["id"]

    upsert_default_vip_record(
        player_id=player_id,
        server_number=1,
        expires_at=finite_expiration,
    )
    assert deactivate_all_default_vip_records(1) == 1
    assert deactivate_all_default_vip_records(1) == 0


def test_expired_record_cleanup_respects_each_list_policy(vip_list_ids):
    from datetime import timedelta

    from rcon.vip import cleanup_expired_vip_records

    now = datetime.now(UTC)
    keep = create_vip_list(f"Keep {uuid4().hex}")
    cleanup = create_vip_list(f"Cleanup {uuid4().hex}", expired_retention_days=1)
    vip_list_ids.extend([keep["id"], cleanup["id"]])
    assert keep["expired_retention_days"] is None
    assert cleanup["expired_retention_days"] == 1

    old = add_record_to_vip_list(
        "0002" + uuid4().hex[4:],
        cleanup["id"],
        expires_at=now - timedelta(days=2),
    )
    recent = add_record_to_vip_list(
        "0002" + uuid4().hex[4:],
        cleanup["id"],
        expires_at=now - timedelta(hours=1),
    )
    retained = add_record_to_vip_list(
        "0002" + uuid4().hex[4:],
        keep["id"],
        expires_at=now - timedelta(days=2),
    )
    assert cleanup_expired_vip_records(now=now) == 1

    with enter_session() as sess:
        assert get_vip_record(sess, old["id"]) is None
        assert get_vip_record(sess, recent["id"]) is not None
        assert get_vip_record(sess, retained["id"]) is not None

    edited = edit_vip_list(cleanup["id"], expired_retention_days=0)
    assert edited["expired_retention_days"] == 0
    assert cleanup_expired_vip_records(now=now) == 1

    with enter_session() as sess:
        assert get_vip_record(sess, recent["id"]) is None
        assert get_vip_record(sess, retained["id"]) is not None


@pytest.mark.parametrize("invalid", [-1, 3651, True, "1"])
def test_expired_record_retention_rejects_invalid_values(vip_list_ids, invalid):
    with pytest.raises(ValueError, match="retention"):
        create_vip_list(f"Invalid {uuid4().hex}", expired_retention_days=invalid)
