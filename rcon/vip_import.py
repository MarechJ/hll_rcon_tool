"""Import partner-owned VIP lists without modifying locally owned lists."""

import base64
import hashlib
import http.client
import ipaddress
import json
import logging
import os
import socket
import ssl
from datetime import UTC, datetime, timedelta
from urllib.parse import urlsplit

import httpx
from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import select, text

from rcon.commands import HLLCommandFailedError
from rcon.models import VipList, VipListImport, VipListRecord, enter_session
from rcon.player_history import _get_set_player
from rcon.player_id_utils import is_supported_player_id
from rcon.types import VipListSyncMethod
from rcon.vip import _notify_vip_sync, reconcile_vip_list_flags

MAX_FEED_BYTES = 2_000_000
MAX_RECORDS = 5_000
logger = logging.getLogger(__name__)


def _cipher() -> Fernet:
    secret = os.getenv("RCONWEB_API_SECRET")
    if not secret or len(secret) < 16:
        raise ValueError("Set RCONWEB_API_SECRET before importing partner lists")
    key = base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest())
    return Fernet(key)


def _validate_url(url: str) -> tuple[str, str]:
    if not isinstance(url, str) or len(url) > 2048:
        raise ValueError("Invalid partner URL")
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.fragment
        or parsed.query
        or parsed.port not in (None, 443)
    ):
        raise ValueError("Partner URL must be public HTTPS on port 443")
    if not parsed.path.endswith("/api/get_shared_vip_list"):
        raise ValueError("Partner URL must point to the shared VIP list endpoint")
    try:
        addresses = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise ValueError("Partner hostname could not be resolved") from exc
    if not addresses or any(
        not ipaddress.ip_address(address[4][0]).is_global for address in addresses
    ):
        raise ValueError("Partner URL must resolve only to public addresses")
    return url, addresses[0][4][0]


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    """Connect to the validated IP while checking TLS against the hostname."""

    def __init__(self, hostname: str, address: str):
        super().__init__(
            hostname, 443, timeout=10, context=ssl.create_default_context()
        )
        self._address = address

    def connect(self):
        self.sock = self._create_connection((self._address, self.port), self.timeout)
        self.sock = self._context.wrap_socket(self.sock, server_hostname=self.host)


def _validate_webhook(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.hostname != "discord.com"
        or parsed.port not in (None, 443)
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or not parsed.path.startswith("/api/webhooks/")
    ):
        raise ValueError("Discord webhook URL must use discord.com/api/webhooks/")
    return url


def _send_webhook(encrypted_url: str | None, message: str) -> None:
    if not encrypted_url:
        return
    try:
        url = _cipher().decrypt(encrypted_url.encode()).decode()
        with httpx.Client(timeout=5, follow_redirects=False, trust_env=False) as client:
            client.post(
                url, json={"content": message, "allowed_mentions": {"parse": []}}
            ).raise_for_status()
    except (httpx.HTTPError, InvalidToken, ValueError):
        # HTTP errors can include the webhook URL, which contains a secret.
        logger.warning("Unable to send partner VIP notification")


def _parse_feed(payload: object) -> list[dict]:
    if not isinstance(payload, dict) or payload.get("failed") is not False:
        raise ValueError("Partner feed returned an error")
    result = payload.get("result")
    if not isinstance(result, dict) or result.get("schema_version") != 1:
        raise ValueError("Unsupported partner feed version")
    rows = result.get("records")
    if not isinstance(rows, list) or len(rows) > MAX_RECORDS:
        raise ValueError("Partner feed has too many records or an invalid format")
    parsed = []
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            raise TypeError("Invalid partner VIP record")
        player_id = row.get("player_id")
        if (
            not isinstance(player_id, str)
            or not is_supported_player_id(player_id)
            or player_id in seen
        ):
            raise ValueError("Invalid or duplicate player ID in partner feed")
        seen.add(player_id)
        description = row.get("description")
        if description is not None and (
            not isinstance(description, str) or len(description) > 255
        ):
            raise ValueError("Invalid partner VIP description")
        expiration = row.get("expires_at")
        if expiration is not None:
            if not isinstance(expiration, str):
                raise ValueError("Invalid partner VIP expiration")
            expiration = datetime.fromisoformat(expiration)
            if expiration.tzinfo is None:
                raise ValueError("Partner VIP expiration requires a timezone")
        parsed.append(
            {
                "player_id": player_id,
                "description": description,
                "expires_at": expiration,
            }
        )
    return parsed


def _fetch(url: str, token: str) -> list[dict]:
    _, address = _validate_url(url)
    parsed = urlsplit(url)
    connection = _PinnedHTTPSConnection(parsed.hostname, address)
    try:
        connection.request(
            "GET",
            parsed.path,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        )
        response = connection.getresponse()
        if response.status != 200:
            raise ValueError("Partner feed unavailable or share key rejected")
        body = response.read(MAX_FEED_BYTES + 1)
        if len(body) > MAX_FEED_BYTES:
            raise ValueError("Partner feed is too large")
    except (OSError, http.client.HTTPException) as exc:
        raise ValueError("Partner feed unavailable or share key rejected") from exc
    finally:
        connection.close()
    return _parse_feed(json.loads(body))


def create_import(
    name: str,
    source_url: str,
    token: str,
    approve_new: bool = True,
    servers: list[int] | None = None,
    webhook_url: str | None = None,
    retention_days: int | None = None,
) -> dict:
    if not isinstance(name, str):
        raise TypeError("Import name must be a string")
    name = name.strip()
    if not name or len(name) > 128 or not isinstance(approve_new, bool):
        raise ValueError("Invalid import name or approval setting")
    if not isinstance(token, str) or not token.startswith("vls_") or len(token) > 128:
        raise ValueError("Invalid partner share token")
    if retention_days is not None and (
        isinstance(retention_days, bool)
        or not isinstance(retention_days, int)
        or not 0 <= retention_days <= 3650
    ):
        raise ValueError("Retention must be between 0 and 3650 days")
    _validate_url(source_url)
    webhook_url = _validate_webhook(webhook_url)
    cipher = _cipher()
    # Check the credential and format before creating a managed list.
    _fetch(source_url, token)
    with enter_session() as sess:
        vip_list = VipList(
            name=name,
            sync=VipListSyncMethod.IGNORE_UNKNOWN,
            flags=[],
            expired_retention_days=retention_days,
        )
        vip_list.set_server_numbers(servers)
        sess.add(vip_list)
        sess.flush()
        vip_list.partner_import = VipListImport(
            source_url=source_url,
            encrypted_token=cipher.encrypt(token.encode()).decode(),
            encrypted_webhook_url=cipher.encrypt(webhook_url.encode()).decode()
            if webhook_url
            else None,
            approve_new=approve_new,
        )
        result = vip_list.to_dict()
    return result


def get_imports() -> list[dict]:
    with enter_session() as sess:
        return [
            {
                "vip_list_id": source.vip_list_id,
                "name": source.vip_list.name,
                "source_url": source.source_url,
                "approve_new": source.approve_new,
                "last_success_at": source.last_success_at,
                "webhook_configured": source.encrypted_webhook_url is not None,
            }
            for source in sess.scalars(
                select(VipListImport).order_by(VipListImport.vip_list_id)
            )
        ]


def update_import_settings(
    vip_list_id: int,
    *,
    approve_new: bool,
    retention_days: int | None,
    webhook_url: str | None = None,
    clear_webhook: bool = False,
) -> dict:
    if not isinstance(approve_new, bool):
        raise TypeError("Approval setting must be a boolean")
    if retention_days is not None and (
        isinstance(retention_days, bool)
        or not isinstance(retention_days, int)
        or not 0 <= retention_days <= 3650
    ):
        raise ValueError("Retention must be between 0 and 3650 days")
    if webhook_url and clear_webhook:
        raise ValueError("Cannot set and clear a webhook at the same time")
    if not isinstance(clear_webhook, bool):
        raise TypeError("Clear webhook must be a boolean")
    webhook_url = _validate_webhook(webhook_url)
    with enter_session() as sess:
        source = sess.get(VipListImport, vip_list_id)
        if source is None:
            raise ValueError("Imported VIP list not found")
        source.approve_new = approve_new
        source.vip_list.expired_retention_days = retention_days
        if clear_webhook:
            source.encrypted_webhook_url = None
        elif webhook_url:
            source.encrypted_webhook_url = (
                _cipher().encrypt(webhook_url.encode()).decode()
            )
        return {
            "vip_list_id": vip_list_id,
            "approve_new": source.approve_new,
            "retention_days": source.vip_list.expired_retention_days,
            "webhook_configured": source.encrypted_webhook_url is not None,
        }


def sync_import(vip_list_id: int, *, force: bool = True) -> dict:
    """Fetch and apply a complete feed under a cross-process database lock."""
    counts = {"new": 0, "changed": 0, "deactivated": 0, "pending": 0}
    with enter_session() as sess:
        locked = sess.scalar(
            text("SELECT pg_try_advisory_xact_lock(764839, :list_id)"),
            {"list_id": vip_list_id},
        )
        if not locked:
            return {**counts, "skipped": "already syncing"}
        source = sess.get(VipListImport, vip_list_id)
        if source is None:
            raise ValueError("Imported VIP list not found")
        now = datetime.now(UTC)
        if (
            not force
            and source.last_success_at is not None
            and source.last_success_at > now - timedelta(minutes=15)
        ):
            return {**counts, "skipped": "recently synchronized"}
        token = _cipher().decrypt(source.encrypted_token.encode()).decode()
        # An invalid or incomplete feed rolls back; nothing is deactivated.
        rows = _fetch(source.source_url, token)
        incoming = {row["player_id"]: row for row in rows}
        current = {
            record.player.player_id: record
            for record in sess.scalars(
                select(VipListRecord).where(VipListRecord.vip_list_id == vip_list_id)
            )
        }
        affected = set()
        for player_id, row in incoming.items():
            record = current.get(player_id)
            if record is None:
                player = _get_set_player(sess, player_id)
                record = VipListRecord(
                    player=player,
                    vip_list=source.vip_list,
                    admin_name="Partner import",
                    partner_approved=not source.approve_new,
                    partner_present=True,
                    partner_excluded=False,
                    active=not source.approve_new,
                    description=row["description"] if not player.names else None,
                    expires_at=row["expires_at"],
                )
                sess.add(record)
                counts["new"] += 1
                if source.approve_new:
                    counts["pending"] += 1
            else:
                old_state = (
                    record.active,
                    record.expires_at,
                    record.description,
                    record.partner_present,
                )
                record.partner_present = True
                record.partner_deactivated_at = None
                record.expires_at = row["expires_at"]
                record.description = (
                    row["description"] if not record.player.names else None
                )
                record.active = record.partner_approved and not record.partner_excluded
                if old_state != (
                    record.active,
                    record.expires_at,
                    record.description,
                    record.partner_present,
                ):
                    counts["changed"] += 1
            affected.add(record.player.id)
        for player_id, record in current.items():
            if player_id not in incoming and record.partner_present:
                record.partner_present = False
                record.active = False
                record.partner_deactivated_at = now
                affected.add(record.player.id)
                counts["deactivated"] += 1
        source.last_success_at = now
        source.last_error_notified_at = None
        reconcile_vip_list_flags(sess, affected)
        server_mask = source.vip_list.servers
        list_name = source.vip_list.name
        encrypted_webhook = source.encrypted_webhook_url
        sess.commit()
    if any(counts.values()):
        _notify_vip_sync(server_mask)
        _send_webhook(
            encrypted_webhook,
            f"VIP partner list **{list_name}**: {counts['new']} new "
            f"({counts['pending']} awaiting approval), {counts['changed']} changed, "
            f"{counts['deactivated']} deactivated. Review in CRCON: /records/vip-lists",
        )
    return counts


def notify_import_error(vip_list_id: int) -> None:
    """Notify at most once per hour while a source remains unavailable."""
    with enter_session() as sess:
        source = sess.get(VipListImport, vip_list_id)
        if source is None or source.encrypted_webhook_url is None:
            return
        now = datetime.now(UTC)
        if (
            source.last_error_notified_at
            and source.last_error_notified_at > now - timedelta(hours=1)
        ):
            return
        source.last_error_notified_at = now
        encrypted_webhook = source.encrypted_webhook_url
        list_name = source.vip_list.name
    _send_webhook(
        encrypted_webhook,
        f"VIP partner list **{list_name}** could not be synchronized. "
        "Existing VIP entries were kept. Check the source and credential in CRCON.",
    )


def set_import_record_policy(
    record_id: int, *, approved: bool | None = None, excluded: bool | None = None
) -> dict:
    if approved is None and excluded is None:
        raise ValueError("Specify approval or exclusion")
    if any(
        value is not None and not isinstance(value, bool)
        for value in (approved, excluded)
    ):
        raise ValueError("Approval and exclusion must be booleans")
    with enter_session() as sess:
        record = sess.get(VipListRecord, record_id)
        if record is None or record.vip_list.partner_import is None:
            raise HLLCommandFailedError("Imported VIP entry not found")
        if approved is not None:
            record.partner_approved = approved
        if excluded is not None:
            record.partner_excluded = excluded
        record.active = (
            record.partner_present
            and record.partner_approved
            and not record.partner_excluded
        )
        reconcile_vip_list_flags(sess, {record.player_id_id})
        server_mask = record.vip_list.servers
        result = {
            "id": record.id,
            "approved": record.partner_approved,
            "excluded": record.partner_excluded,
            "active": record.active,
        }
        sess.commit()
    _notify_vip_sync(server_mask)
    return result
