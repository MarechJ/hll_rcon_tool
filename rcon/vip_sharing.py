"""List-scoped sharing credentials and a deliberately small partner feed."""

import hashlib
import secrets
from datetime import UTC, datetime

from sqlalchemy import select

from rcon.models import VipList, VipListShare, enter_session
from rcon.vip import get_active_vip_records


def _share_info(share: VipListShare) -> dict:
    return {
        "id": share.id,
        "vip_list_id": share.vip_list_id,
        "name": share.name,
        "created_at": share.created_at,
        "expires_at": share.expires_at,
        "revoked_at": share.revoked_at,
        "revoked_by": share.revoked_by,
        "last_used_at": share.last_used_at,
    }


def create_share(
    vip_list_id: int, name: str, expires_at: datetime | None = None
) -> dict:
    if not isinstance(name, str):
        raise TypeError("Share name must be a string")
    name = name.strip()
    if not name or len(name) > 128:
        raise ValueError("Share name must contain 1 to 128 characters")
    if expires_at is not None and (
        expires_at.tzinfo is None or expires_at <= datetime.now(UTC)
    ):
        raise ValueError("Expiration must be a future timezone-aware datetime")

    token = "vls_" + secrets.token_urlsafe(32)
    with enter_session() as sess:
        vip_list = sess.get(VipList, vip_list_id)
        if vip_list is None:
            raise ValueError("VIP list not found")
        if vip_list.partner_import is not None:
            raise ValueError("Imported lists cannot be shared onward")
        share = VipListShare(
            vip_list_id=vip_list_id,
            name=name,
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            expires_at=expires_at,
        )
        sess.add(share)
        sess.flush()
        info = _share_info(share)
    return {**info, "token": token}


def list_shares(vip_list_id: int) -> list[dict]:
    with enter_session() as sess:
        if sess.get(VipList, vip_list_id) is None:
            raise ValueError("VIP list not found")
        return [
            _share_info(share)
            for share in sess.scalars(
                select(VipListShare)
                .where(VipListShare.vip_list_id == vip_list_id)
                .order_by(VipListShare.id)
            )
        ]


def revoke_share(share_id: int, revoked_by: str | None = None) -> bool:
    with enter_session() as sess:
        share = sess.get(VipListShare, share_id)
        if share is None:
            raise ValueError("Share not found")
        if share.revoked_at is None:
            share.revoked_at = datetime.now(UTC)
            share.revoked_by = revoked_by
    return True


def get_partner_feed(token: str) -> dict | None:
    if not isinstance(token, str) or len(token) > 128 or not token.startswith("vls_"):
        return None
    digest = hashlib.sha256(token.encode()).hexdigest()
    with enter_session() as sess:
        share = sess.scalar(
            select(VipListShare).where(VipListShare.token_hash == digest)
        )
        now = datetime.now(UTC)
        if (
            share is None
            or share.revoked_at is not None
            or (share.expires_at is not None and share.expires_at <= now)
        ):
            return None
        records = get_active_vip_records(sess, share.vip_list_id)
        share.last_used_at = now
        return {
            "schema_version": 1,
            "list": {"name": share.vip_list.name},
            "records": [
                {
                    "player_id": record.player.player_id,
                    "description": record.description,
                    "expires_at": record.expires_at,
                }
                for record in records
            ],
        }
