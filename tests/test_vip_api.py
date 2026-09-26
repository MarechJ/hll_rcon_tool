from datetime import UTC, datetime
from uuid import uuid4

from rcon.api_commands import RconAPI
from rcon.types import VipListSyncMethod


def test_vip_list_api_crud(isolated_default_vip_lists):
    api = object.__new__(RconAPI)
    player_id = "0002" + uuid4().hex[4:]
    list_id = None
    target_list_id = None
    record_id = None

    try:
        created = api.create_vip_list(
            name=f"API Test {uuid4().hex}",
            sync=VipListSyncMethod.IGNORE_UNKNOWN,
            servers=[1],
        )
        list_id = created["id"]

        assert api.get_vip_list(list_id) == created
        assert created in api.get_vip_lists()
        assert created in api.get_vip_lists_for_server(server_number=1)
        assert created not in api.get_vip_lists_for_server(server_number=2)

        edited_list = api.edit_vip_list(
            vip_list_id=list_id,
            name="API Test Edited",
            sync=VipListSyncMethod.REMOVE_UNKNOWN,
            servers=[1, 2],
        )
        assert edited_list["name"] == "API Test Edited"
        assert edited_list["sync"] == VipListSyncMethod.REMOVE_UNKNOWN
        assert edited_list["servers"] == [1, 2]

        assert api.get_default_vip_list(server_number=1) is None
        assert (
            api.set_default_vip_list(
                vip_list_id=list_id,
                server_number=1,
            )
            == edited_list
        )
        assert api.get_default_vip_list(server_number=1) == edited_list
        assert api.clear_default_vip_list(server_number=1) is True
        assert api.clear_default_vip_list(server_number=1) is False
        assert api.get_default_vip_list(server_number=1) is None

        record = api.add_vip_list_record(
            player_id=player_id,
            vip_list_id=list_id,
            description="API integration test",
            notes="Created through RconAPI",
            admin_name="pytest",
        )
        record_id = record["id"]

        assert api.get_vip_list_record(record_id) == record
        assert api.get_player_vip_list_record(player_id, list_id) == record
        assert record in api.get_player_vip_records(player_id)
        assert record in api.get_active_vip_records(list_id)

        edited_record = api.edit_vip_list_record(
            record_id=record_id,
            active=False,
            notes="Inactive through RconAPI",
            admin_name="pytest",
        )
        assert edited_record["is_active"] is False
        assert edited_record["notes"] == "Inactive through RconAPI"
        assert edited_record in api.get_inactive_vip_records(list_id)

        bulk_edited = api.edit_vip_list_records(
            record_ids=[record_id],
            active=True,
            notes="Bulk edit through RconAPI",
            admin_name="pytest bulk",
        )
        assert len(bulk_edited) == 1
        assert bulk_edited[0]["is_active"] is True
        assert bulk_edited[0]["notes"] == "Bulk edit through RconAPI"

        target_list = api.create_vip_list(
            name=f"API Target {uuid4().hex}",
            sync=VipListSyncMethod.IGNORE_UNKNOWN,
            servers=[1],
        )
        target_list_id = target_list["id"]

        bulk_moved = api.edit_vip_list_records(
            record_ids=[record_id],
            vip_list_id=target_list_id,
            admin_name="pytest move",
        )
        assert bulk_moved[0]["vip_list_id"] == target_list_id
        assert bulk_moved[0]["notes"] == "Bulk edit through RconAPI"

        second_record = api.add_vip_list_record(
            player_id="0002" + uuid4().hex[4:],
            vip_list_id=list_id,
            description="Bulk delete API test",
            admin_name="pytest",
        )
        assert api.delete_vip_list_records([record_id, second_record["id"]]) == 2
        record_id = None

        assert api.get_player_vip_list_record(player_id, list_id) is None

        third_record = api.add_vip_list_record(
            player_id="0002" + uuid4().hex[4:],
            vip_list_id=list_id,
            description="Single delete API test",
            admin_name="pytest",
        )
        record_id = third_record["id"]

        assert api.delete_vip_list_record(record_id) is True
        record_id = None
        assert api.get_player_vip_list_record(player_id, list_id) is None

        assert api.delete_vip_list(list_id) is True
        list_id = None

    finally:
        if record_id is not None:
            api.delete_vip_list_record(record_id)
        if list_id is not None:
            api.delete_vip_list(list_id)
        if target_list_id is not None:
            api.delete_vip_list(target_list_id)


def test_vip_list_record_upsert_reactivates_without_duplicate(
    isolated_default_vip_lists,
):
    api = object.__new__(RconAPI)
    player_id = "0002" + uuid4().hex[4:]
    list_id = None
    record_id = None

    first_expiration = datetime(2035, 1, 1, 12, 0, tzinfo=UTC)
    second_expiration = datetime(2036, 2, 2, 13, 30, tzinfo=UTC)

    try:
        vip_list = api.create_vip_list(
            name=f"API Upsert Test {uuid4().hex}",
            sync=VipListSyncMethod.IGNORE_UNKNOWN,
            servers=[1],
        )
        list_id = vip_list["id"]

        created = api.upsert_vip_list_record(
            player_id=player_id,
            vip_list_id=list_id,
            description="Seed VIP integration test",
            expires_at=first_expiration,
            notes="Initial Seed VIP reward",
            admin_name="Seed VIP Reward",
        )
        record_id = created["id"]

        assert created["vip_list_id"] == list_id
        assert created["player_id"] == player_id
        assert created["is_active"] is True
        assert created["expires_at"] == first_expiration
        assert created["notes"] == "Initial Seed VIP reward"
        assert created["admin_name"] == "Seed VIP Reward"

        deactivated = api.edit_vip_list_record(
            record_id=record_id,
            active=False,
            notes="Temporarily inactive",
            admin_name="pytest",
        )
        assert deactivated["is_active"] is False

        reactivated = api.upsert_vip_list_record(
            player_id=player_id,
            vip_list_id=list_id,
            description="Updated Seed VIP integration test",
            expires_at=second_expiration,
            notes="Renewed Seed VIP reward",
            admin_name="Seed VIP Reward",
        )

        assert reactivated["id"] == record_id
        assert reactivated["vip_list_id"] == list_id
        assert reactivated["player_id"] == player_id
        assert reactivated["is_active"] is True
        assert reactivated["expires_at"] == second_expiration
        assert reactivated["notes"] == "Renewed Seed VIP reward"
        assert reactivated["admin_name"] == "Seed VIP Reward"

        matching_records = [
            record
            for record in api.get_player_vip_records(player_id)
            if record["vip_list_id"] == list_id
        ]
        assert len(matching_records) == 1
        assert matching_records[0]["id"] == record_id

    finally:
        if record_id is not None:
            api.delete_vip_list_record(record_id)
        if list_id is not None:
            api.delete_vip_list(list_id)
