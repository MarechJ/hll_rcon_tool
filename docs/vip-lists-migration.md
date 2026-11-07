# VIP Lists migration guide

This document describes the database migration path for the VIP Lists rework,
including installations that previously deployed an intermediate development
version of this branch.

## Final migration layout

The final VIP Lists migration path consists of two revisions:

- `4f3a2c1d9e80` — creates the complete VIP Lists schema.
- `7a6c5e4d3b21` — migrates legacy `player_vip` data and removes the legacy
  table after validation.

The final migration replaces several temporary development migrations that
existed on earlier revisions of this branch.

## Important warning

Do not blindly run `alembic stamp` on an installation that previously deployed
an intermediate version of the VIP Lists branch.

Some intermediate revisions already created or modified VIP Lists tables.
Stamping such a database without first verifying its schema and data can cause
Alembic to consider migrations applied even though the database does not match
the final schema.

Always create a PostgreSQL backup before changing the Alembic revision or
running the final migration.

## 1. Determine the current state

Before upgrading, record the currently installed Alembic revision:

```bash
alembic current
```

Also check whether the legacy and new VIP tables exist:

```sql
SELECT to_regclass('public.player_vip') AS player_vip;
SELECT to_regclass('public.vip_list') AS vip_list;
SELECT to_regclass('public.vip_list_record') AS vip_list_record;
SELECT to_regclass('public.vip_list_default') AS vip_list_default;
SELECT to_regclass('public.vip_list_share') AS vip_list_share;
SELECT to_regclass('public.vip_list_import') AS vip_list_import;
SELECT to_regclass('public.vip_server_sync_config') AS vip_server_sync_config;
SELECT to_regclass('public.player_identity_game') AS player_identity_game;
SELECT to_regclass('public.vip_list_pending_record') AS vip_list_pending_record;
```

Record counts should also be captured before migration:

```sql
SELECT COUNT(*) FROM player_vip;
SELECT COUNT(*) FROM vip_list;
SELECT COUNT(*) FROM vip_list_record;
```

Run only the queries for tables that exist.

## 2. Normal upgrade from upstream / pre-VIP-Lists CRCON

Installations that have never deployed an intermediate VIP Lists migration
should use the normal Alembic upgrade path.

Revision `4f3a2c1d9e80` creates the final VIP Lists schema.

Revision `7a6c5e4d3b21` then migrates the legacy `player_vip` records into
VIP Lists.

For each legacy server it creates a list named:

```text
Migrated Server #<server_number>
```

and preserves the legacy player assignment and expiration.

Expiration timestamps at or beyond the historical year-3000 sentinel are
converted to no expiration. Real finite expiration dates remain finite.

Before removing `player_vip`, the migration validates that every legacy VIP
row is represented by a migrated VIP List record.

A normal installation can therefore use the standard upgrade:

```bash
alembic upgrade head
```

## 3. Upgrade from an intermediate version of this branch

Earlier development versions of this branch used several temporary Alembic
revisions while the VIP Lists implementation was being developed.

Superseded development revisions include:

```text
b7e2a91c4f10
d4b8f3c2a1e0
a91c7e4b2d60
c6f4a1d82e39
af731c89d215
c4e9a6b183d2
e8c9d1a742b5
f91a82c407de
bc27a8cbd9a2
d83c6a4f1b90
c7f42e91a6bd
6b1d8e90f4ab
```

These revisions covered development versions of:

- the VIP Lists data model;
- default VIP Lists;
- list flags and expiration settings;
- sharing credentials;
- partner imports;
- sharing usage and revocation information;
- per-server synchronization configuration.

They were later consolidated into the final migration layout.

If `alembic current` reports one of these removed development revisions, do
not blindly run `alembic upgrade head` or `alembic stamp`.

The database may already contain VIP Lists tables and user data, while the
consolidated schema migration expects to create those tables.

The safe procedure is:

1. Stop services that can modify VIP data.
2. Create and verify a PostgreSQL backup.
3. Record the current Alembic revision.
4. Inspect the existing VIP Lists schema and record counts.
5. Identify which intermediate development revision was deployed.
6. Verify that the existing schema matches that revision.
7. Preserve all existing VIP Lists, records, defaults, shares and imports.
8. Reconcile the intermediate revision with the consolidated migration only
   after the database state has been verified.
9. Run the remaining final migration steps.
10. Verify the final schema and data before restarting CRCON.

### Known deployed intermediate revision: `6b1d8e90f4ab`

Revision `6b1d8e90f4ab` is a known deployed development state of the VIP Lists
branch.

At this revision, the development migration chain had already created and
populated the VIP Lists tables. In particular, the earlier
`b7e2a91c4f10` migration had already copied legacy `player_vip` assignments
into `vip_list` and `vip_list_record`.

The consolidated `4f3a2c1d9e80` migration cannot be applied directly to such
a database because it attempts to create the VIP Lists tables again.

The following `7a6c5e4d3b21` migration must also not be run manually against
an unreconciled `6b1d8e90f4ab` database. It performs the legacy
`player_vip` migration again before validating and dropping the legacy table.

Therefore a database reporting:

```text
6b1d8e90f4ab


The exact reconciliation procedure depends on the deployed intermediate
revision and should not be replaced by a generic `alembic stamp` command.

## 4. Legacy migration safety checks

Revision `7a6c5e4d3b21` validates the legacy `player_vip` data before removing
the table.

Legacy rows are rejected if `server_number` is:

- `NULL`;
- less than `1`; or
- greater than `32`.

The migration creates one migrated list per legacy server and transfers the
legacy VIP assignments into `vip_list_record`.

It then compares the number of legacy records with the records represented in
the generated migrated lists.

If the counts differ, the migration raises an exception and does not continue
with removal of the legacy table.

Only after successful validation is `player_vip` dropped.

## 5. Final database state

After a successful upgrade, Alembic should report:

```text
7a6c5e4d3b21 (head)
```

The final VIP schema includes:

```text
vip_list
vip_list_record
vip_list_default
vip_list_share
vip_list_import
vip_server_sync_config
player_identity_game
vip_list_pending_record
```

The legacy table:

```text
player_vip
```

should no longer exist after `7a6c5e4d3b21` completes successfully.

## 6. Verification

Check the Alembic revision:

```bash
alembic current
```

Expected:

```text
7a6c5e4d3b21 (head)
```

Check the relevant tables:

```sql
SELECT to_regclass('public.player_vip') AS player_vip;
SELECT to_regclass('public.vip_list') AS vip_list;
SELECT to_regclass('public.vip_list_record') AS vip_list_record;
SELECT to_regclass('public.player_identity_game') AS player_identity_game;
SELECT to_regclass('public.vip_list_pending_record') AS vip_list_pending_record;
```

`player_vip` should return `NULL`. The final VIP Lists tables should exist.

Review the resulting lists:

```sql
SELECT id, name, servers
FROM vip_list
ORDER BY id;
```

Review record counts per list:

```sql
SELECT vip_list_id, COUNT(*)
FROM vip_list_record
GROUP BY vip_list_id
ORDER BY vip_list_id;
```

Review default-list assignments:

```sql
SELECT server_number, vip_list_id
FROM vip_list_default
ORDER BY server_number;
```

Finally verify that the backend, supervisor, maintenance and frontend services
start successfully and that VIP synchronization reports no migration-related
errors.

## 7. Downgrade limitation

Downgrading across `7a6c5e4d3b21` is intentionally unsupported.

After migration, VIP Lists can contain information that cannot be represented
losslessly by the old `player_vip` model. The migration therefore refuses to
recreate `player_vip` automatically.

Rollback across this migration boundary requires restoring the PostgreSQL
backup taken before the upgrade together with application code compatible with
that database state.
