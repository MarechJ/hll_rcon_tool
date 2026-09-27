# VIP list partnerships

This feature builds on the VIP Lists rework in PR #1431. A locally owned list can
have any number of independent, revocable, read-only shares. Each partner imports
one share into a separate, read-only local list. A player can also appear in any
number of locally owned lists; the existing effective VIP calculation keeps VIP
access while at least one applicable active list still grants it.

## Share a list

In **VIP Lists**, select a locally owned list, open **Edit list**, enter a partner
name under **Share this list**, and create a key. A share icon marks lists with
active credentials. Copy the key immediately. It is stored as a SHA-256
digest and cannot be recovered later. Give the partner the key and the feed URL
shown in the UI. One partner's key can be revoked without affecting other shares.
The share settings show when and by which CRCON user a key was revoked. Keys
revoked before this tracking was added show an unknown user.

The partner requests `GET /api/get_shared_vip_list` with
`Authorization: Bearer <share key>`. This endpoint requires no CRCON account and
exposes only active, unexpired player IDs, descriptions for players without a
known name, and expiration timestamps. It never exports notes, list flags,
permissions, other lists, or the CRCON API key. Invalid or revoked credentials
return HTTP 401.

## Import a partner list

Select **Import partner list**, enter the HTTPS feed URL and key, and optionally
configure a Discord webhook and an inactive-record retention period. A key is
encrypted at rest using the CRCON web secret. Keep `RCONWEB_API_SECRET` stable
and set it to the same strong value on both backend and supervisor containers.
Imports require a configured value of at least 16 characters. Rotating it requires reconnecting
partner imports. The feed URL must resolve to public addresses, use HTTPS on
port 443, and end in `/api/get_shared_vip_list`.
The **Settings** action can later change the approval mode, retention period,
or webhook without losing imported records or local exclusions.

An import starts empty. Select the imported list and click **Synchronize now** to
load it. By default, newly discovered players await local approval. The alternative
automatic mode activates them at the first successful synchronization. Partner
changes to existing entries, expiration, and removal are applied automatically.
An incomplete, invalid, or unavailable feed never changes existing entries.

Imported records are read-only through the normal VIP list editing API. An
administrator with `can_approve_vip_list_imports` may approve a pending player
or exclude a player from that import. An exclusion survives later imports and
does not affect locally owned lists. **Copy to own list** creates a separate,
locally managed VIP record; it does not change the imported record.

The VIP synchronization handler attempts partner updates on startup and at its
normal periodic interval, but each import is fetched no more than once every
15 minutes unless a user requests a manual sync. A PostgreSQL advisory lock
prevents concurrent handlers from applying the same import at once. A successful
change triggers the usual gameserver VIP synchronization.

When a partner removes a player or the source entry expires, the imported record
becomes inactive. A partner-removed entry without a local exclusion can be
deleted manually. If the imported list has a
retention period, expired or partner-removed records are cleaned up after that
period. Locally excluded records are retained to ensure the exclusion remains in
force if a partner later adds the player again.

An optional Discord webhook sends one summary for a changed feed. Fetch failures
send a generic alert at most once per hour. Webhook URLs and share keys are not
included in notifications. The webhook must use `https://discord.com/api/webhooks/`.

## Permissions

The `owner` and `admin` groups receive three distinct permissions on migration:

| Permission | Purpose |
| --- | --- |
| `can_manage_vip_list_shares` | Create, list, and revoke share keys |
| `can_manage_vip_list_imports` | Connect sources and trigger manual sync |
| `can_approve_vip_list_imports` | Approve and locally exclude imported players |

The imported list's ordinary record-edit endpoints reject changes. The existing
`can_delete_vip_lists` permission can remove an imported list entirely, and
`can_delete_vip_list_records` can remove partner-removed records without exclusions.

## Deployment and verification

Apply both Alembic and Django migrations before starting the updated backend.
The source and recipient instances must both run this feature. Verify a first
import with approval enabled: the player stays pending until approved; exclude
the player and synchronize again; then confirm an independent record in an owned
list still grants VIP. Finally revoke the share and confirm the feed returns 401
without deleting the recipient's existing entries.
