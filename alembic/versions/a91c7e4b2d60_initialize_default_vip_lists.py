"""Initialize one empty default VIP list per configured server.

Revision ID: a91c7e4b2d60
Revises: d4b8f3c2a1e0
"""

from alembic import op


revision = "a91c7e4b2d60"
down_revision = "d4b8f3c2a1e0"
branch_labels = None
depends_on = None


def upgrade():
    # Create a separate operational list for every configured server which
    # does not already have a default assignment. Migrated legacy lists and
    # their records remain completely separate and unchanged.
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
            'IGNORE_UNKNOWN',
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

    # Assign the dedicated empty/default list. An existing manual default is
    # never replaced. If a matching Default Server list already exists, reuse
    # the oldest matching list rather than creating a duplicate.
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


def downgrade():
    # This is intentionally data-preserving. Default lists may contain VIPs
    # created after the upgrade, so a downgrade of this data-only migration
    # must not delete lists, records, or deliberate default assignments.
    pass
