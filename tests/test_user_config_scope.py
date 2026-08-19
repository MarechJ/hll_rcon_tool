import os
from contextlib import contextmanager

import pytest
from pydantic import ValidationInfo, field_validator

os.environ.setdefault("SERVER_NUMBER", "1")
os.environ.setdefault("HLL_GAME", "hll")

from rcon.models import UserConfig
from rcon.types import GameEnum, GameIntEnum
from rcon.user_config.auto_mod_level import AutoModLevelUserConfig
from rcon.user_config.auto_mod_no_leader import AutoModNoLeaderUserConfig
from rcon.user_config.auto_settings import AutoSettingsConfig
from rcon.user_config.ban_tk_on_connect import BanTeamKillOnConnectUserConfig
from rcon.user_config.utils import (
    BaseUserConfig,
    _add_conf,
    _get_conf,
    all_subclasses,
    set_user_config,
    user_config_identity,
    validate_user_config,
)


class FakeQuery:
    def __init__(self, result=None):
        self.result = result
        self.criteria = ()

    def filter(self, *criteria):
        self.criteria = criteria
        return self

    def one_or_none(self):
        return self.result


class FakeSession:
    def __init__(self, result=None):
        self.query_result = result
        self.query_object = FakeQuery(result)
        self.added = []

    def query(self, model):
        assert model is UserConfig
        return self.query_object

    def add(self, model):
        self.added.append(model)
        return model

    def rollback(self):
        pass


def _criterion_values(query: FakeQuery) -> dict[str, object]:
    return {criterion.left.key: criterion.right.value for criterion in query.criteria}


def test_identity_uses_server_info_from_environment(monkeypatch):
    monkeypatch.setenv("HLL_GAME", GameEnum.HLL_VIETNAM.value)
    monkeypatch.setenv("SERVER_NUMBER", "7")

    assert user_config_identity("ExampleConfig") == (
        GameIntEnum.HLL_VIETNAM,
        7,
        "ExampleConfig",
    )


def test_get_conf_filters_by_game_server_and_name():
    session = FakeSession()

    _get_conf(
        session,
        "ExampleConfig",
        game=GameEnum.HLL_VIETNAM,
        server_number=3,
    )

    assert _criterion_values(session.query_object) == {
        "game": GameIntEnum.HLL_VIETNAM.value,
        "server_number": 3,
        "name": "ExampleConfig",
    }


def test_add_conf_sets_complete_database_identity():
    session = FakeSession()

    _add_conf(
        session,
        "ExampleConfig",
        {"enabled": True},
        game=GameEnum.HLL_WW2,
        server_number=4,
    )

    assert len(session.added) == 1
    assert session.added[0].game == GameIntEnum.HLL_WW2.value
    assert session.added[0].server_number == 4
    assert session.added[0].name == "ExampleConfig"
    assert session.added[0].value == {"enabled": True}


def test_set_user_config_does_not_cross_game_scope(monkeypatch):
    sessions = []

    @contextmanager
    def fake_enter_session():
        session = FakeSession()
        sessions.append(session)
        yield session

    monkeypatch.setattr("rcon.user_config.utils.enter_session", fake_enter_session)

    set_user_config(
        "ExampleConfig",
        {"enabled": True},
        game=GameEnum.HLL_VIETNAM,
        server_number=1,
    )

    assert _criterion_values(sessions[0].query_object)["game"] == 2
    assert sessions[0].added[0].game == 2


def test_auto_settings_uses_migrated_name():
    assert AutoSettingsConfig.NAME == "AutoSettings"


def test_every_user_config_declares_a_stable_name():
    configs = all_subclasses(BaseUserConfig)

    assert configs
    assert all(config.__dict__.get("NAME") == config.__name__ for config in configs)


def test_validation_receives_game_and_server_context():
    class ContextAwareConfig(BaseUserConfig):
        NAME = "ContextAwareConfig"

        game: GameEnum
        server_number: int

        @field_validator("game", mode="before")
        @classmethod
        def game_from_context(cls, value, info: ValidationInfo):
            return info.context["game"]

        @field_validator("server_number", mode="before")
        @classmethod
        def server_from_context(cls, value, info: ValidationInfo):
            return info.context["server_number"]

        @staticmethod
        def save_to_db(values, dry_run=True):
            return None

    validate_user_config(
        ContextAwareConfig,
        {"game": None, "server_number": None},
        game=GameEnum.HLL_VIETNAM,
        server_number=8,
    )

    validated = ContextAwareConfig.model_validate(
        {"game": None, "server_number": None},
        context={"game": GameEnum.HLL_VIETNAM, "server_number": 8},
    )
    assert validated.game == GameEnum.HLL_VIETNAM
    assert validated.server_number == 8


def test_role_validation_uses_selected_game_profile():
    config = AutoModNoLeaderUserConfig.model_validate(
        {"immune_roles": ["squadleader"]},
        context={"game": GameEnum.HLL_VIETNAM},
    )
    assert config.immune_roles == ["squadleader"]

    with pytest.raises(ValueError, match="not valid for hll"):
        AutoModNoLeaderUserConfig.model_validate(
            {"immune_roles": ["squadleader"]},
            context={"game": GameEnum.HLL_WW2},
        )


def test_level_threshold_roles_use_selected_game_profile():
    config = AutoModLevelUserConfig.model_validate(
        {
            "level_thresholds": {
                "squadleader": {"label": "Squad Leader", "min_players": 0, "min_level": 25}
            }
        },
        context={"game": GameEnum.HLL_VIETNAM},
    )

    assert "squadleader" in config.level_thresholds

    with pytest.raises(ValueError, match="not valid for hll"):
        AutoModLevelUserConfig.model_validate(
            {
                "level_thresholds": {
                    "squadleader": {
                        "label": "Squad Leader",
                        "min_players": 0,
                        "min_level": 25,
                    }
                }
            },
            context={"game": GameEnum.HLL_WW2},
        )


def test_weapon_validation_uses_selected_game_profile():
    config = BanTeamKillOnConnectUserConfig.model_validate(
        {"excluded_weapons": ["M16A1"]},
        context={"game": GameEnum.HLL_VIETNAM},
    )
    assert config.excluded_weapons == ["M16A1"]

    with pytest.raises(ValueError, match="not valid for hll"):
        BanTeamKillOnConnectUserConfig.model_validate(
            {"excluded_weapons": ["M16A1"]},
            context={"game": GameEnum.HLL_WW2},
        )


def test_auto_settings_maps_use_selected_game_profile():
    vietnam_settings = {
        "rules": [
            {
                "conditions": {
                    "current_map": {"map_names": ["wdeve_warfare_day"]}
                }
            }
        ]
    }

    AutoSettingsConfig(game=GameEnum.HLL_VIETNAM).validate_settings(
        vietnam_settings
    )
    with pytest.raises(ValueError, match="not valid for hll"):
        AutoSettingsConfig(game=GameEnum.HLL_WW2).validate_settings(
            vietnam_settings
        )


def test_validation_scope_reaches_legacy_save_implementation(monkeypatch):
    sessions = []

    @contextmanager
    def fake_enter_session():
        session = FakeSession()
        sessions.append(session)
        yield session

    class LegacySaveConfig(BaseUserConfig):
        NAME = "LegacySaveConfig"

        enabled: bool = False

        @staticmethod
        def save_to_db(values, dry_run=True):
            if not dry_run:
                set_user_config(LegacySaveConfig.NAME, values)

    monkeypatch.setattr("rcon.user_config.utils.enter_session", fake_enter_session)

    validate_user_config(
        LegacySaveConfig,
        {"enabled": True},
        dry_run=False,
        game=GameEnum.HLL_VIETNAM,
        server_number=9,
    )

    assert sessions[0].added[0].game == GameIntEnum.HLL_VIETNAM.value
    assert sessions[0].added[0].server_number == 9
