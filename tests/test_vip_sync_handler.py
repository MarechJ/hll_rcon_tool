from uuid import uuid4

import pytest

import rcon.vip as vip_module
import rcon.vip_sync_handler as sync_module
from rcon.models import enter_session
from rcon.vip import (
    add_record_to_vip_list,
    create_vip_list,
    delete_vip_list,
    delete_vip_list_record,
    edit_vip_list_record,
    get_vip_record,
)
from rcon.vip_sync_handler import (
    ALL_SERVERS_MASK,
    VipSyncCommand,
    VipSyncCommandHandler,
)


@pytest.mark.parametrize(
    "server_mask",
    [1, 2, 3, ALL_SERVERS_MASK],
)
def test_vip_sync_command_round_trip(server_mask):
    command = VipSyncCommand(server_mask)

    assert VipSyncCommand.decode(command.encode()) == command


def test_vip_sync_command_rejects_invalid_payload():
    with pytest.raises(
        ValueError,
        match="Invalid VIP synchronization command size",
    ):
        VipSyncCommand.decode(b"invalid")


def test_send_publishes_binary_command_and_closes_connection(monkeypatch):
    published = []

    class FakeRedis:
        closed = False

        def publish(self, channel, payload):
            published.append((channel, payload))
            return 2

        def close(self):
            self.closed = True

    fake_redis = FakeRedis()

    monkeypatch.setenv("HLL_REDIS_URL", "redis://test-redis:6379/1")
    monkeypatch.setattr(
        sync_module.redis.Redis,
        "from_url",
        lambda *args, **kwargs: fake_redis,
    )

    assert VipSyncCommandHandler.send(3) == 2
    assert fake_redis.closed is True
    assert len(published) == 1

    channel, payload = published[0]
    assert channel == VipSyncCommandHandler.CHANNEL
    assert VipSyncCommand.decode(payload).server_mask == 3


def test_handler_filters_notifications_by_server_mask(monkeypatch):
    class StopLoop(BaseException):
        pass

    class FakePubSub:
        def __init__(self):
            self.messages = [
                {"data": VipSyncCommand(1).encode()},
                {"data": VipSyncCommand(2).encode()},
            ]
            self.subscriptions = []

        def subscribe(self, channel):
            self.subscriptions.append(channel)

        def get_message(self, timeout):
            del timeout
            if self.messages:
                return self.messages.pop(0)
            raise StopLoop

    handler = object.__new__(VipSyncCommandHandler)
    handler.pubsub = FakePubSub()
    handler.server_number = 2
    handler.server_mask = 2
    handler.interval_seconds = 300

    triggers = []
    handler.synchronize = lambda trigger: triggers.append(trigger)

    monkeypatch.setattr(sync_module.time, "monotonic", lambda: 0.0)

    with pytest.raises(StopLoop):
        handler.run()

    assert handler.pubsub.subscriptions == [VipSyncCommandHandler.CHANNEL]
    assert triggers == ["startup", "notification"]


def test_handler_runs_periodic_safety_sync(monkeypatch):
    class StopLoop(BaseException):
        pass

    class FakePubSub:
        calls = 0

        def subscribe(self, channel):
            del channel

        def get_message(self, timeout):
            del timeout
            self.calls += 1
            if self.calls == 1:
                return
            raise StopLoop

    handler = object.__new__(VipSyncCommandHandler)
    handler.pubsub = FakePubSub()
    handler.server_number = 1
    handler.server_mask = 1
    handler.interval_seconds = 30

    triggers = []
    handler.synchronize = lambda trigger: triggers.append(trigger)

    timestamps = iter([0.0, 0.0, 31.0, 31.0, 31.0])
    monkeypatch.setattr(
        sync_module.time,
        "monotonic",
        lambda: next(timestamps),
    )

    with pytest.raises(StopLoop):
        handler.run()

    assert triggers == ["startup", "periodic"]


def test_notification_normalizes_and_merges_server_masks(monkeypatch):
    sent_masks = []

    monkeypatch.setattr(
        VipSyncCommandHandler,
        "send",
        lambda server_mask: sent_masks.append(server_mask) or 1,
    )

    assert vip_module._merge_vip_server_masks(1, 2) == 3
    assert vip_module._merge_vip_server_masks(1, None) == ALL_SERVERS_MASK

    vip_module._notify_vip_sync(None)
    vip_module._notify_vip_sync(3)
    vip_module._notify_vip_sync(0)

    assert sent_masks == [ALL_SERVERS_MASK, 3]


def test_record_changes_publish_affected_server_masks(monkeypatch):
    notifications = []
    source_id = None
    target_id = None

    monkeypatch.setattr(
        vip_module,
        "_notify_vip_sync",
        notifications.append,
    )

    try:
        source = create_vip_list(
            name=f"Sync source {uuid4().hex}",
            servers=[1],
        )
        target = create_vip_list(
            name=f"Sync target {uuid4().hex}",
            servers=[2],
        )
        source_id = source["id"]
        target_id = target["id"]

        record = add_record_to_vip_list(
            player_id="0002" + uuid4().hex[4:],
            vip_list_id=source_id,
            admin_name="pytest",
        )
        assert notifications[-1] == 1

        edit_vip_list_record(
            record["id"],
            vip_list_id=target_id,
            admin_name="pytest",
        )
        assert notifications[-1] == 3

        assert delete_vip_list_record(record["id"]) is True
        assert notifications[-1] == 2
    finally:
        if target_id is not None:
            delete_vip_list(target_id)
        if source_id is not None:
            delete_vip_list(source_id)


def test_redis_failure_does_not_rollback_committed_record(monkeypatch):
    vip_list_id = None
    record_id = None

    def fail_publish(server_mask):
        raise ConnectionError(f"Redis unavailable for mask {server_mask}")

    monkeypatch.setattr(
        VipSyncCommandHandler,
        "send",
        fail_publish,
    )

    try:
        created = create_vip_list(
            name=f"Redis failure {uuid4().hex}",
            servers=[1],
        )
        vip_list_id = created["id"]

        record = add_record_to_vip_list(
            player_id="0002" + uuid4().hex[4:],
            vip_list_id=vip_list_id,
            admin_name="pytest",
        )
        record_id = record["id"]

        with enter_session() as session:
            committed = get_vip_record(
                session,
                record_id,
                strict=True,
            )
            assert committed is not None
            assert committed.vip_list_id == vip_list_id
    finally:
        monkeypatch.setattr(
            vip_module,
            "_notify_vip_sync",
            lambda server_mask: None,
        )
        if vip_list_id is not None:
            delete_vip_list(vip_list_id)
