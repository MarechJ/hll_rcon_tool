from unittest import mock

from rcon.api_commands import RconAPI
from rcon.automods import server_info_for_automod
from rcon.automods.automod import do_punitions, enabled_moderators
from rcon.automods.models import ActionMethod, PunitionsToApply
from rcon.automods.tk_autoban import auto_ban_if_tks_right_after_connection
from rcon.game.hllv.profile import HLLV_PROFILE
from rcon.types import GameEnum, ServerInfo
from rcon.user_config.auto_mod_level import AutoModLevelUserConfig
from rcon.user_config.auto_mod_no_leader import AutoModNoLeaderUserConfig
from rcon.user_config.auto_mod_seeding import AutoModSeedingUserConfig
from rcon.user_config.auto_mod_solo_tank import AutoModNoSoloTankUserConfig
from rcon.user_config.ban_tk_on_connect import BanTeamKillOnConnectUserConfig


class VietnamRcon:
    game_profile = HLLV_PROFILE


class BoundVietnamRcon(VietnamRcon):
    server_info = ServerInfo(game=GameEnum.HLL_VIETNAM, number=11)


def test_server_info_uses_rcon_game_and_environment_server(monkeypatch):
    monkeypatch.setenv("HLL_GAME", GameEnum.HLL_WW2.value)
    monkeypatch.setenv("SERVER_NUMBER", "7")

    server_info = server_info_for_automod(VietnamRcon())

    assert server_info.game == GameEnum.HLL_VIETNAM
    assert server_info.number == 7


def test_bound_server_info_is_the_scope_source_of_truth(monkeypatch):
    monkeypatch.setenv("HLL_GAME", GameEnum.HLL_WW2.value)
    monkeypatch.setenv("SERVER_NUMBER", "1")

    assert server_info_for_automod(BoundVietnamRcon()) is BoundVietnamRcon.server_info


def test_squad_automods_load_configs_from_rcon_scope(monkeypatch):
    monkeypatch.setenv("HLL_GAME", GameEnum.HLL_WW2.value)
    monkeypatch.setenv("SERVER_NUMBER", "7")
    monkeypatch.setattr("rcon.automods.automod.get_redis_client", mock.Mock())

    configs = (
        AutoModLevelUserConfig,
        AutoModNoLeaderUserConfig,
        AutoModSeedingUserConfig,
        AutoModNoSoloTankUserConfig,
    )
    loaders = []
    for config in configs:
        loader = mock.Mock(return_value=config())
        monkeypatch.setattr(config, "load_from_db", loader)
        loaders.append(loader)

    assert enabled_moderators(VietnamRcon()) == []
    for loader in loaders:
        loader.assert_called_once_with(
            game=GameEnum.HLL_VIETNAM,
            server_number=7,
        )


def test_tk_automod_loads_config_from_rcon_scope(monkeypatch):
    monkeypatch.setenv("HLL_GAME", GameEnum.HLL_WW2.value)
    monkeypatch.setenv("SERVER_NUMBER", "8")
    loader = mock.Mock(return_value=BanTeamKillOnConnectUserConfig(enabled=False))
    monkeypatch.setattr(BanTeamKillOnConnectUserConfig, "load_from_db", loader)

    auto_ban_if_tks_right_after_connection(VietnamRcon(), {})

    loader.assert_called_once_with(
        game=GameEnum.HLL_VIETNAM,
        server_number=8,
    )


def test_action_execution_reuses_one_config_snapshot(monkeypatch):
    rcon = VietnamRcon()
    moderators = [mock.Mock()]
    load_moderators = mock.Mock(return_value=moderators)
    apply_actions = mock.Mock()
    monkeypatch.setattr(
        "rcon.automods.automod.enabled_moderators", load_moderators
    )
    monkeypatch.setattr("rcon.automods.automod._do_punitions", apply_actions)

    do_punitions(rcon, PunitionsToApply())

    load_moderators.assert_called_once_with(rcon)
    assert [call.args[1] for call in apply_actions.call_args_list] == [
        ActionMethod.MESSAGE,
        ActionMethod.PUNISH,
        ActionMethod.KICK,
    ]
    assert all(call.args[3] is moderators for call in apply_actions.call_args_list)


def test_api_validation_uses_rcon_scope(monkeypatch):
    monkeypatch.setenv("HLL_GAME", GameEnum.HLL_WW2.value)
    monkeypatch.setenv("SERVER_NUMBER", "10")
    loader = mock.Mock(return_value=AutoModNoLeaderUserConfig())
    validate = mock.Mock(return_value=None)
    monkeypatch.setattr(AutoModNoLeaderUserConfig, "load_from_db", loader)
    monkeypatch.setattr("rcon.api_commands.validate_user_config", validate)

    RconAPI._validate_user_config(
        VietnamRcon(),
        command_name="set_auto_mod_no_leader_config",
        by="test",
        model=AutoModNoLeaderUserConfig,
        data={"enabled": False},
        dry_run=False,
    )

    loader.assert_called_once_with(
        game=GameEnum.HLL_VIETNAM,
        server_number=10,
    )
    validate.assert_called_once_with(
        model=AutoModNoLeaderUserConfig,
        data={"enabled": False},
        dry_run=False,
        reset_to_default=False,
        game=GameEnum.HLL_VIETNAM,
        server_number=10,
    )
