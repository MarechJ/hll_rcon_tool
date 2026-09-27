"""Partner imports must never override a locally owned VIP entry."""

from uuid import uuid4

import pytest

from rcon.commands import HLLCommandFailedError
from rcon.models import enter_session
from rcon.vip import (
    add_record_to_vip_list,
    create_vip_list,
    delete_vip_list,
    delete_vip_list_record,
    get_effective_vip_records,
    get_player_vip_list_record,
)
from rcon.vip_import import (
    _parse_feed,
    _validate_url,
    create_import,
    set_import_record_policy,
    sync_import,
)
from rcon.vip_sharing import create_share, get_partner_feed, revoke_share


def test_partner_feed_rejects_partial_or_duplicate_data():
    valid = {
        "failed": False,
        "result": {
            "schema_version": 1,
            "records": [
                {
                    "player_id": "76561199988877765",
                    "description": None,
                    "expires_at": None,
                }
            ],
        },
    }
    assert len(_parse_feed(valid)) == 1
    with pytest.raises(ValueError, match="duplicate"):
        _parse_feed(
            {
                "failed": False,
                "result": {
                    "schema_version": 1,
                    "records": valid["result"]["records"] * 2,
                },
            }
        )


def test_partner_source_must_resolve_publicly(monkeypatch):
    monkeypatch.setattr(
        "rcon.vip_import.socket.getaddrinfo",
        lambda *_args, **_kwargs: [(None, None, None, None, ("127.0.0.1", 443))],
    )
    with pytest.raises(ValueError, match="public"):
        _validate_url("https://partner.example/api/get_shared_vip_list")


def test_partner_expiration_requires_timezone():
    with pytest.raises(ValueError, match="timezone"):
        _parse_feed(
            {
                "failed": False,
                "result": {
                    "schema_version": 1,
                    "records": [
                        {
                            "player_id": "76561199988877765",
                            "expires_at": "2030-01-01T00:00:00",
                        }
                    ],
                },
            }
        )


def test_share_is_scoped_and_revocable(monkeypatch):
    monkeypatch.setattr("rcon.vip._notify_vip_sync", lambda *_: None)
    first = create_vip_list(f"Share A {uuid4().hex}")
    second = create_vip_list(f"Share B {uuid4().hex}")
    try:
        add_record_to_vip_list("76561199988877765", first["id"], notes="internal note")
        add_record_to_vip_list("76561199988877766", second["id"])
        one = create_share(first["id"], "Partner one")
        two = create_share(first["id"], "Partner two")
        feed = get_partner_feed(one["token"])
        assert [row["player_id"] for row in feed["records"]] == ["76561199988877765"]
        assert "notes" not in feed["records"][0]
        revoke_share(one["id"])
        assert get_partner_feed(one["token"]) is None
        assert get_partner_feed(two["token"]) is not None
    finally:
        delete_vip_list(first["id"])
        delete_vip_list(second["id"])


def test_partner_approval_exclusion_and_own_list_survive_removal(monkeypatch):
    monkeypatch.setenv(
        "RCONWEB_API_SECRET", "test-secret-for-vip-import-encryption-123456"
    )
    monkeypatch.setattr("rcon.vip_import._validate_url", lambda url: url)
    monkeypatch.setattr("rcon.vip_import._notify_vip_sync", lambda *_: None)
    monkeypatch.setattr("rcon.vip._notify_vip_sync", lambda *_: None)
    monkeypatch.setattr("rcon.vip_import._send_webhook", lambda *_: None)
    player_id = "76561199988877764"
    feed = [{"player_id": player_id, "description": "Partner", "expires_at": None}]
    monkeypatch.setattr("rcon.vip_import._fetch", lambda *_: feed)
    own = create_vip_list(f"Own {uuid4().hex}")
    imported = create_import(
        f"Partner {uuid4().hex}",
        "https://partner.example/api/get_shared_vip_list",
        "vls_test",
    )
    try:
        own_record = add_record_to_vip_list(player_id, own["id"])
        assert sync_import(imported["id"])["pending"] == 1
        with pytest.raises(HLLCommandFailedError, match="read-only"):
            add_record_to_vip_list("76561199988877760", imported["id"])
        with enter_session() as sess:
            partner = get_player_vip_list_record(sess, player_id, imported["id"])
            partner_id = partner.id
            assert partner.active is False
            assert get_effective_vip_records(sess, 1)[player_id].id == own_record["id"]

        assert set_import_record_policy(partner_id, approved=True)["active"] is True
        assert set_import_record_policy(partner_id, excluded=True)["active"] is False
        with pytest.raises(HLLCommandFailedError, match="partner-removed"):
            delete_vip_list_record(partner_id)
        assert sync_import(imported["id"])["changed"] == 0
        feed.clear()
        assert sync_import(imported["id"])["deactivated"] == 1
        with enter_session() as sess:
            partner = get_player_vip_list_record(sess, player_id, imported["id"])
            assert partner.active is False and partner.partner_excluded is True
            assert get_effective_vip_records(sess, 1)[player_id].id == own_record["id"]
    finally:
        delete_vip_list(imported["id"])
        delete_vip_list(own["id"])


def test_failed_partner_fetch_keeps_existing_records(monkeypatch):
    monkeypatch.setenv(
        "RCONWEB_API_SECRET", "test-secret-for-vip-import-encryption-123456"
    )
    monkeypatch.setattr("rcon.vip_import._validate_url", lambda url: url)
    monkeypatch.setattr("rcon.vip_import._notify_vip_sync", lambda *_: None)
    monkeypatch.setattr("rcon.vip_import._send_webhook", lambda *_: None)
    feed = [{"player_id": "76561199988877763", "description": None, "expires_at": None}]
    monkeypatch.setattr("rcon.vip_import._fetch", lambda *_: feed)
    imported = create_import(
        f"Failure {uuid4().hex}",
        "https://partner.example/api/get_shared_vip_list",
        "vls_test",
        approve_new=False,
    )
    try:
        sync_import(imported["id"])

        def fail(*_):
            raise ValueError("Invalid feed")

        monkeypatch.setattr("rcon.vip_import._fetch", fail)
        with pytest.raises(ValueError, match="Invalid feed"):
            sync_import(imported["id"])
        with enter_session() as sess:
            record = get_player_vip_list_record(
                sess, feed[0]["player_id"], imported["id"]
            )
            assert record.active and record.partner_present
    finally:
        delete_vip_list(imported["id"])
