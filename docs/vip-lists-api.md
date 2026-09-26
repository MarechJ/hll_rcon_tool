# VIP Lists API

This document describes the VIP API changes introduced by the VIP Lists rework in
[#1431](https://github.com/MarechJ/hll_rcon_tool/pull/1431). It is intended for
administrators and developers who manage VIPs through external tools or scripts.

## Compatibility summary

No existing VIP API endpoint was removed.

The legacy endpoints remain available and now operate through the current server's
default VIP list. New integrations should use the VIP Lists endpoints because they
can address a specific list, preserve per-list metadata and support multi-server
synchronization.

| Legacy endpoint | Status | New behavior or recommended replacement |
| --- | --- | --- |
| `POST /api/add_vip` | Retained | Writes to the current server's default list and synchronizes the gameserver. Prefer `POST /api/add_vip_list_record` or `POST /api/upsert_vip_list_record`. |
| `POST /api/remove_vip` | Retained | Deactivates the matching record in the default list and synchronizes. Records in other applicable lists are not modified. Prefer `POST /api/edit_vip_list_record` or `POST /api/delete_vip_list_record`. |
| `POST /api/remove_all_vips` | Retained | Deactivates records in the default list only, then synchronizes. Other lists are not modified. Prefer the bulk record endpoints when list-specific control is required. |
| `GET /api/get_vip_ids` | Retained | Returns gameserver VIPs and augments managed entries with effective list expiration and name data. Unknown gameserver entries remain visible. Prefer the list and record query endpoints for database state. |
| `GET /api/get_vips_count` | Retained | Unchanged. |
| `GET /api/get_vip_slots_num` | Retained | Unchanged. |

The year-3000 value historically used by `add_vip` as an indefinite-expiration
sentinel is converted to `null`. Other valid future dates, including dates after
2030, remain finite.

## Transport and authentication

Endpoints use the existing CRCON API authentication and permission system. Authenticate
with a CRCON browser session or an API key that has the permission listed below.

- The base path is `/api/<command>`.
- Query endpoints use `GET`; parameters are supplied as query parameters.
- Mutating endpoints use `POST` with `Content-Type: application/json`.
- `server_number` may be omitted where documented. The current CRCON instance's
  configured server number is then used.
- Datetimes are ISO 8601 strings with a timezone, for example
  `2031-02-03T04:05:06+00:00`.
- Player IDs may be a 17-digit Steam64 ID or a 32-character hexadecimal network ID
  used by HLL Vietnam/EOS.

### Response envelope

All endpoints documented below return the normal CRCON response envelope. The
endpoint-specific schemas in this document describe the value of `result`.

```json
{
  "result": {},
  "command": "get_vip_lists",
  "arguments": {},
  "failed": false,
  "error": null,
  "forward_results": null,
  "version": "v12.2.1-38-gae956eab"
}
```

An application-level error returns HTTP 400 with `failed: true`, an explanatory
`error` string and a null result:

```json
{
  "result": null,
  "command": "get_vip_list",
  "arguments": {"vip_list_id": 9999},
  "failed": true,
  "error": "No VIP list found with ID 9999",
  "forward_results": null,
  "version": "v12.2.1-38-gae956eab"
}
```

Clients must check both the HTTP status and `failed`; they must not infer success
from the presence of a JSON response alone.

## Shared schemas

The schemas use JSON Schema Draft 2020-12 notation. Database-generated identifiers
are positive integers.

### `VipList`

```json
{
  "$id": "VipList",
  "type": "object",
  "additionalProperties": false,
  "required": ["id", "name", "sync", "servers"],
  "properties": {
    "id": {"type": "integer", "minimum": 1},
    "name": {"type": "string", "minLength": 1},
    "sync": {
      "type": "string",
      "enum": ["ignore_unknown", "remove_unknown"]
    },
    "servers": {
      "oneOf": [
        {"type": "null"},
        {
          "type": "array",
          "items": {"type": "integer", "minimum": 1},
          "uniqueItems": true
        }
      ],
      "description": "null applies the list to every server; an array limits it to the listed server numbers"
    }
  }
}
```

`ignore_unknown` leaves gameserver VIPs that are not managed by an applicable list
untouched. An unknown gameserver VIP is eligible for automatic removal only when
applicable list configuration permits it; use the sync preview before applying
changes.

### `VipListRecord`

```json
{
  "$id": "VipListRecord",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "id",
    "vip_list_id",
    "player_id",
    "player_name",
    "admin_name",
    "created_at",
    "is_active",
    "is_expired",
    "expires_at",
    "description",
    "notes"
  ],
  "properties": {
    "id": {"type": "integer", "minimum": 1},
    "vip_list_id": {"type": "integer", "minimum": 1},
    "player_id": {"type": "string"},
    "player_name": {"type": ["string", "null"]},
    "admin_name": {"type": "string"},
    "created_at": {"type": "string", "format": "date-time"},
    "is_active": {"type": "boolean"},
    "is_expired": {"type": "boolean"},
    "expires_at": {"type": ["string", "null"], "format": "date-time"},
    "description": {"type": ["string", "null"]},
    "notes": {"type": ["string", "null"]}
  }
}
```

Only one record for a player may exist in a given list. `is_expired` is computed
from `expires_at`; it is not accepted as an input field.

### `VipSyncPlan`

```json
{
  "$id": "VipSyncPlan",
  "type": "object",
  "additionalProperties": false,
  "required": ["to_add", "to_remove", "unchanged", "unknown"],
  "properties": {
    "to_add": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["player_id", "description"],
        "properties": {
          "player_id": {"type": "string"},
          "description": {"type": ["string", "null"]}
        }
      }
    },
    "to_remove": {"type": "array", "items": {"type": "string"}},
    "unchanged": {"type": "array", "items": {"type": "string"}},
    "unknown": {"type": "array", "items": {"type": "string"}}
  }
}
```

- `to_add`: active, unexpired database records missing from the gameserver.
- `to_remove`: gameserver VIPs that are no longer effective and should be removed.
- `unchanged`: entries already matching the effective database state.
- `unknown`: gameserver VIPs not managed by an applicable list and not scheduled
  for automatic removal.

### `VipSyncResult`

```json
{
  "$id": "VipSyncResult",
  "type": "object",
  "additionalProperties": false,
  "required": ["plan", "execution"],
  "properties": {
    "plan": {"$ref": "VipSyncPlan"},
    "execution": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "dry_run",
        "added",
        "removed",
        "skipped_additions",
        "skipped_removals",
        "failures",
        "successful"
      ],
      "properties": {
        "dry_run": {"type": "boolean"},
        "added": {"type": "array", "items": {"type": "string"}},
        "removed": {"type": "array", "items": {"type": "string"}},
        "skipped_additions": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["player_id", "description"],
            "properties": {
              "player_id": {"type": "string"},
              "description": {"type": ["string", "null"]}
            }
          }
        },
        "skipped_removals": {
          "type": "array",
          "items": {"type": "string"}
        },
        "failures": {
          "type": "array",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "required": ["action", "player_id", "error"],
            "properties": {
              "action": {"type": "string", "enum": ["add", "remove"]},
              "player_id": {"type": "string"},
              "error": {"type": "string"}
            }
          }
        },
        "successful": {"type": "boolean"}
      }
    }
  }
}
```

### `VipSyncStatus`

```json
{
  "$id": "VipSyncStatus",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "server_number",
    "state",
    "trigger",
    "started_at",
    "completed_at",
    "last_success_at",
    "added",
    "removed",
    "failures"
  ],
  "properties": {
    "server_number": {"type": "integer", "minimum": 1},
    "state": {
      "type": "string",
      "enum": ["never", "running", "successful", "failed"]
    },
    "trigger": {"type": ["string", "null"]},
    "started_at": {"type": ["string", "null"], "format": "date-time"},
    "completed_at": {"type": ["string", "null"], "format": "date-time"},
    "last_success_at": {"type": ["string", "null"], "format": "date-time"},
    "added": {"type": "integer", "minimum": 0},
    "removed": {"type": "integer", "minimum": 0},
    "failures": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["action", "player_id", "error"],
        "properties": {
          "action": {"type": "string"},
          "player_id": {"type": ["string", "null"]},
          "error": {"type": "string"}
        }
      }
    }
  }
}
```

## Endpoint reference

### List queries

All list query endpoints require `api.can_view_vip_lists`.

| Method and path | Parameters | `result` |
| --- | --- | --- |
| `GET /api/get_vip_lists` | None | `VipList[]` |
| `GET /api/get_vip_lists_for_server` | `server_number?: integer` | Applicable `VipList[]` |
| `GET /api/get_default_vip_list` | `server_number?: integer` | `VipList \| null` |
| `GET /api/get_vip_list` | `vip_list_id: integer` | `VipList` |

Example:

```http
GET /api/get_vip_lists_for_server?server_number=2
```

### Create, edit and delete lists

| Method and path | Permission | JSON request | `result` |
| --- | --- | --- | --- |
| `POST /api/create_vip_list` | `api.can_create_vip_lists` | `{"name": string, "sync"?: "ignore_unknown" \| "remove_unknown", "servers"?: integer[] \| null}` | `VipList` |
| `POST /api/edit_vip_list` | `api.can_change_vip_lists` | `{"vip_list_id": integer, "name"?: string, "sync"?: "ignore_unknown" \| "remove_unknown", "servers"?: integer[] \| null}` | `VipList` |
| `POST /api/delete_vip_list` | `api.can_delete_vip_lists` | `{"vip_list_id": integer}` | `boolean` |

`servers: null` applies a list to all configured servers. Omitting `servers` while
editing leaves the current assignment unchanged. List names are trimmed and must
not be empty.

```json
{
  "name": "Community VIPs",
  "sync": "ignore_unknown",
  "servers": [1, 2]
}
```

### Default list

| Method and path | Permission | Parameters or JSON request | `result` |
| --- | --- | --- | --- |
| `GET /api/get_default_vip_list` | `api.can_view_vip_lists` | `server_number?: integer` | `VipList \| null` |
| `POST /api/set_default_vip_list` | `api.can_change_vip_lists` | `{"vip_list_id": integer, "server_number"?: integer}` | `VipList` |
| `POST /api/clear_default_vip_list` | `api.can_change_vip_lists` | `{"server_number"?: integer}` | `boolean` |

The selected list must be applicable to that server. The default list is also the
compatibility target used by legacy write endpoints and by integrations that omit
an explicit list where such fallback is supported.

### Record queries

All record query endpoints require `api.can_view_vip_lists`.

| Method and path | Parameters | `result` |
| --- | --- | --- |
| `GET /api/get_vip_list_record` | `record_id: integer` | `VipListRecord` |
| `GET /api/get_player_vip_list_record` | `player_id: string`, `vip_list_id: integer` | `VipListRecord \| null` |
| `GET /api/get_player_vip_records` | `player_id: string`, `include_expired?: boolean` (default `true`), `include_inactive?: boolean` (default `true`), `server_number?: integer` | `VipListRecord[]` |
| `GET /api/get_active_vip_records` | `vip_list_id: integer` | `VipListRecord[]` |
| `GET /api/get_inactive_vip_records` | `vip_list_id: integer` | `VipListRecord[]` |

When `server_number` is supplied to `get_player_vip_records`, only records from
lists applicable to that server are returned.

### Create and upsert records

| Method and path | Permission | JSON request | `result` |
| --- | --- | --- | --- |
| `POST /api/add_vip_list_record` | `api.can_add_vip_list_records` | `AddVipListRecordRequest` | `VipListRecord` |
| `POST /api/upsert_vip_list_record` | `api.can_change_vip_lists` | `UpsertVipListRecordRequest` | `VipListRecord` |

```json
{
  "$id": "AddVipListRecordRequest",
  "type": "object",
  "additionalProperties": false,
  "required": ["player_id", "vip_list_id"],
  "properties": {
    "player_id": {"type": "string"},
    "vip_list_id": {"type": "integer", "minimum": 1},
    "description": {"type": ["string", "null"], "default": null},
    "active": {"type": "boolean", "default": true},
    "expires_at": {"type": ["string", "null"], "format": "date-time", "default": null},
    "notes": {"type": ["string", "null"], "default": null},
    "admin_name": {"type": "string", "default": "CRCON"}
  }
}
```

`UpsertVipListRecordRequest` has the same fields except that `active` is not accepted.
It always creates or reactivates the record. If the player already has a record in
the selected list, that record keeps its ID and its supplied values are updated.

Example Seed VIP-style upsert:

```json
{
  "player_id": "00025f93565049d3a713a7b6cdea95a5",
  "vip_list_id": 3,
  "description": "Seed VIP reward",
  "expires_at": "2026-09-01T18:00:00+00:00",
  "notes": "Granted automatically after seeding",
  "admin_name": "Seed VIP Reward"
}
```

### Edit and delete records

| Method and path | Permission | JSON request | `result` |
| --- | --- | --- | --- |
| `POST /api/edit_vip_list_record` | `api.can_change_vip_list_records` | `EditVipListRecordRequest` | `VipListRecord` |
| `POST /api/edit_vip_list_records` | `api.can_change_vip_list_records` | `BulkEditVipListRecordsRequest` | `VipListRecord[]` |
| `POST /api/delete_vip_list_record` | `api.can_delete_vip_list_records` | `{"record_id": integer}` | `boolean` |
| `POST /api/delete_vip_list_records` | `api.can_delete_vip_list_records` | `{"record_ids": integer[]}` | Number of deleted records |

```json
{
  "$id": "EditVipListRecordRequest",
  "type": "object",
  "additionalProperties": false,
  "required": ["record_id"],
  "properties": {
    "record_id": {"type": "integer", "minimum": 1},
    "vip_list_id": {"type": "integer", "minimum": 1},
    "description": {"type": ["string", "null"]},
    "active": {"type": "boolean"},
    "expires_at": {"type": ["string", "null"], "format": "date-time"},
    "notes": {"type": ["string", "null"]},
    "admin_name": {"type": "string", "default": "CRCON"}
  }
}
```

`BulkEditVipListRecordsRequest` replaces `record_id` with the required
`record_ids: integer[]` field. At least one editable field must be supplied. For
both edit operations, an omitted field is unchanged while an explicit `null` clears
a nullable field. Bulk edits are atomic.

Deleting a record permanently removes it from the database. Set `active: false`
instead when the record should remain available for auditing or later reactivation.

### Synchronization

| Method and path | Permission | Parameters or JSON request | `result` |
| --- | --- | --- | --- |
| `GET /api/get_vip_sync_plan` | `api.can_view_vip_ids` | `server_number?: integer` | `VipSyncResult` with `execution.dry_run: true` |
| `GET /api/get_vip_sync_status` | `api.can_view_vip_ids` | `server_number?: integer` | `VipSyncStatus` |
| `POST /api/synchronize_vip_lists` | `api.can_change_vip_lists` | `{"server_number"?: integer}` | `VipSyncResult` with `execution.dry_run: false` |
| `POST /api/remove_unknown_vip_from_gameserver` | `api.can_change_vip_lists` | `{"player_id": string, "server_number"?: integer}` | `RemoveUnknownVipResult` |

Always inspect `get_vip_sync_plan` before triggering a manual synchronization from
an external tool. A synchronization can add and remove gameserver VIPs according
to all lists applicable to the selected server.

`remove_unknown_vip_from_gameserver` performs a fresh dry-run immediately before
the removal. It rejects the operation if the player is managed by the database or
is no longer classified as unknown. After removal, it returns a refreshed plan:

```json
{
  "player_id": "00025f93565049d3a713a7b6cdea95a5",
  "removed": true,
  "plan": {
    "to_add": [],
    "to_remove": [],
    "unchanged": [],
    "unknown": []
  }
}
```

## Migration guidance for external integrations

Existing integrations do not have to migrate immediately. Their legacy calls are
routed through the default list configured for the current server.

New or updated integrations should:

1. Call `get_vip_lists_for_server` and select a list that applies to the target
   server.
2. Use `upsert_vip_list_record` for idempotent rewards and renewals.
3. Store both `vip_list_id` and the returned record `id`.
4. Use `edit_vip_list_record` with `active: false` to revoke a managed grant while
   retaining its history.
5. Preview synchronization with `get_vip_sync_plan` before manually calling
   `synchronize_vip_lists`.
6. Treat an indefinite expiration as `expires_at: null`.

The effective VIP set for a server is calculated across all applicable lists. A
player remains a gameserver VIP while at least one active, unexpired applicable
record still grants VIP access. Removing or deactivating a record in one list must
therefore not be assumed to remove a grant supplied by another list.

## Common validation errors

Typical HTTP 400 errors include:

- missing or unconfigured `server_number`;
- an empty list name;
- an unsupported player ID;
- a missing list or record ID;
- selecting a default list that does not apply to the server;
- creating a duplicate player record in the same list;
- a bulk edit without any editable field;
- attempting to remove a gameserver VIP that is not currently unknown.

Consumers should display the envelope's `error` value and avoid retrying validation
errors without changing the request.
