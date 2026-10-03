"""Migrate legacy player_vip data to VIP Lists.

Revision ID: 7a6c5e4d3b21
Revises: 4f3a2c1d9e80
"""

from alembic import op


revision = "7a6c5e4d3b21"
down_revision = "4f3a2c1d9e80"
branch_labels = None
depends_on = None


def upgrade():
    # Refuse to migrate malformed legacy rows. VIP list server masks support
    # server numbers 1 through 32.
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM player_vip
                WHERE server_number IS NULL
                   OR server_number < 1
                   OR server_number > 32
            ) THEN
                RAISE EXCEPTION
                    'player_vip contains an invalid server_number';
            END IF;
        END
        $$;
        """
    )

    # Preserve the legacy VIP assignments in one migrated list per server.
    op.execute(
        """
        INSERT INTO vip_list (name, sync, servers)
        SELECT
            'Migrated Server #' || server_number,
            'IGNORE_UNKNOWN'::viplistsyncmethod,
            (1::bigint << (server_number - 1))
        FROM player_vip
        GROUP BY server_number
        ORDER BY server_number
        """
    )

    op.execute(
        """
        INSERT INTO vip_list_record (
            admin_name,
            created_at,
            active,
            description,
            notes,
            expires_at,
            player_id_id,
            vip_list_id
        )
        SELECT
            'CRCON migration',
            NOW(),
            true,
            NULL,
            NULL,
            CASE
                WHEN pv.expiration >=
                     TIMESTAMPTZ '3000-01-01 00:00:00+00'
                    THEN NULL
                ELSE pv.expiration
            END,
            pv.playersteamid_id,
            vl.id
        FROM player_vip AS pv
        JOIN vip_list AS vl
          ON vl.name = 'Migrated Server #' || pv.server_number
         AND vl.servers = (1::bigint << (pv.server_number - 1))
        """
    )

    # Create one operational default list for every configured or legacy
    # server which does not already have a default assignment.
    op.execute(
        """
        WITH configured_servers AS (
            SELECT DISTINCT server_number
            FROM user_config
            WHERE server_number BETWEEN 1 AND 32

            UNION

            SELECT DISTINCT server_number
            FROM player_vip
            WHERE server_number BETWEEN 1 AND 32
        ),
        missing_defaults AS (
            SELECT configured_servers.server_number
            FROM configured_servers
            LEFT JOIN vip_list_default
              ON vip_list_default.server_number =
                 configured_servers.server_number
            WHERE vip_list_default.server_number IS NULL
        )
        INSERT INTO vip_list (name, sync, servers)
        SELECT
            'Default Server #' || missing_defaults.server_number,
            'IGNORE_UNKNOWN'::viplistsyncmethod,
            (1::bigint << (missing_defaults.server_number - 1))
        FROM missing_defaults
        WHERE NOT EXISTS (
            SELECT 1
            FROM vip_list
            WHERE vip_list.name =
                      'Default Server #' || missing_defaults.server_number
              AND vip_list.servers =
                      (1::bigint << (missing_defaults.server_number - 1))
        )
        ORDER BY missing_defaults.server_number
        """
    )

    op.execute(
        """
        WITH configured_servers AS (
            SELECT DISTINCT server_number
            FROM user_config
            WHERE server_number BETWEEN 1 AND 32

            UNION

            SELECT DISTINCT server_number
            FROM player_vip
            WHERE server_number BETWEEN 1 AND 32
        )
        INSERT INTO vip_list_default (server_number, vip_list_id)
        SELECT
            configured_servers.server_number,
            (
                SELECT vip_list.id
                FROM vip_list
                WHERE vip_list.name =
                          'Default Server #' ||
                          configured_servers.server_number
                  AND vip_list.servers =
                      (
                          1::bigint <<
                          (configured_servers.server_number - 1)
                      )
                ORDER BY vip_list.id
                LIMIT 1
            )
        FROM configured_servers
        WHERE NOT EXISTS (
            SELECT 1
            FROM vip_list_default
            WHERE vip_list_default.server_number =
                  configured_servers.server_number
        )
        ORDER BY configured_servers.server_number
        """
    )

    # Preserve the previous effective REMOVE_UNKNOWN behavior. Missing rows
    # represent IGNORE_UNKNOWN.
    op.execute(
        """
        INSERT INTO vip_server_sync_config (server_number, sync)
        SELECT server_number, 'REMOVE_UNKNOWN'::viplistsyncmethod
        FROM generate_series(1, 32) AS server_number
        WHERE EXISTS (
            SELECT 1
            FROM vip_list
            WHERE servers IS NULL
               OR (servers & (1::bigint << (server_number - 1))) <> 0
        )
        AND NOT EXISTS (
            SELECT 1
            FROM vip_list
            WHERE (
                    servers IS NULL
                    OR (servers & (1::bigint << (server_number - 1))) <> 0
                  )
              AND sync <> 'REMOVE_UNKNOWN'::viplistsyncmethod
        )
        """
    )

    # Validate that every legacy VIP row was represented exactly once before
    # the legacy table is removed.
    op.execute(
        """
        DO $$
        DECLARE
            legacy_count bigint;
            migrated_count bigint;
        BEGIN
            SELECT COUNT(*)
            INTO legacy_count
            FROM player_vip;

            SELECT COUNT(*)
            INTO migrated_count
            FROM player_vip AS pv
            JOIN vip_list AS vl
              ON vl.name = 'Migrated Server #' || pv.server_number
             AND vl.servers = (1::bigint << (pv.server_number - 1))
            JOIN vip_list_record AS vlr
              ON vlr.vip_list_id = vl.id
             AND vlr.player_id_id = pv.playersteamid_id;

            IF legacy_count <> migrated_count THEN
                RAISE EXCEPTION
                    'VIP migration validation failed: % legacy rows, % migrated rows',
                    legacy_count,
                    migrated_count;
            END IF;
        END
        $$;
        """
    )

    op.drop_table("player_vip")


def downgrade():
    # Recreating player_vip would be lossy: VIP Lists may contain records,
    # expirations and assignments which cannot be represented by the legacy
    # model. Do not silently synthesize legacy data.
    raise RuntimeError(
        "Downgrade across the legacy VIP migration is not supported"
    )
