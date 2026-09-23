import importlib.util
import os
from contextlib import nullcontext
from pathlib import Path
from unittest.mock import Mock

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import set_committed_value

os.environ.setdefault("HLL_MAINTENANCE_CONTAINER", "1")
os.environ.setdefault("SERVER_NUMBER", "1")

from rcon import workers
from rcon.models import Maps


@pytest.mark.parametrize("has_morale", [True, False])
def test_worker_persists_morale_and_serializes_scoreboard(has_morale, monkeypatch):
    engine = sa.create_engine("sqlite://")
    # Use SQLite for the round trip; the existing result field uses PostgreSQL JSONB.
    table = Maps.__table__.to_metadata(sa.MetaData())
    for column in table.columns:
        if isinstance(column.type, JSONB):
            column.type = sa.JSON()
    table.create(engine)
    history = [{"ts": 10, "allied_morale": 768, "axis_morale": 999}]
    map_info = {
        "name": "junobeach_conquest_day",
        "start": 1000,
        "end": 2000,
        "match_time": 3600,
        "cap_flips": [{"ts": 10, "allied_score": 3, "axis_score": 2}],
    }
    if has_morale:
        map_info.update(morale_history=history, initial_morale=1000)

    with Session(engine) as session:
        monkeypatch.setattr(workers, "enter_session", lambda: nullcontext(session))
        monkeypatch.setattr(workers, "record_stats_from_map", Mock())
        monkeypatch.setattr(workers, "clear_stats_cache", Mock())
        workers._record_stats(map_info)
        session.expunge_all()

        saved = session.query(Maps).one()
        set_committed_value(saved, "player_stats", [])
        # Both scoreboard detail and list responses use this serializer.
        response = saved.to_dict(with_stats=True)
        assert response["morale_history"] == (history if has_morale else [])
        assert response["initial_morale"] == (1000 if has_morale else None)
        assert response["cap_flips"] == map_info["cap_flips"]
        # Reprocessing an existing match must retain its saved history.
        workers._record_stats(map_info)
        assert session.query(Maps).count() == 1
        assert saved.to_dict()["morale_history"] == response["morale_history"]
    engine.dispose()


def test_morale_migration_preserves_legacy_rows_and_can_downgrade():
    path = (
        Path(__file__).parents[1]
        / "alembic/versions/b7d9e2a641c0_add_map_morale_history.py"
    )
    spec = importlib.util.spec_from_file_location("morale_migration", path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = sa.create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(sa.text("CREATE TABLE map_history (id INTEGER PRIMARY KEY)"))
        connection.execute(sa.text("INSERT INTO map_history (id) VALUES (1)"))
        with Operations.context(MigrationContext.configure(connection)):
            migration.upgrade()
            row = (
                connection.execute(sa.text("SELECT * FROM map_history"))
                .mappings()
                .one()
            )
            assert dict(row) == {
                "id": 1,
                "morale_history": "[]",
                "initial_morale": None,
            }
            connection.execute(sa.text("INSERT INTO map_history (id) VALUES (2)"))
            assert (
                connection.execute(
                    sa.text("SELECT morale_history FROM map_history WHERE id = 2")
                ).scalar_one()
                == "[]"
            )
            migration.downgrade()
            assert connection.execute(
                sa.text("SELECT id FROM map_history ORDER BY id")
            ).scalars().all() == [1, 2]
    engine.dispose()
