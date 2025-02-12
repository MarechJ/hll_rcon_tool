import datetime
from unittest import mock

from rcon.automods.tk_autoban import (
    BanTeamKillOnConnectUserConfig,
    auto_ban_if_tks_right_after_connection,
)
from rcon.types import StructuredLogLineWithMetaData
from rcon.user_config.ban_tk_on_connect import BanTeamKillOnConnectWhiteList, TimeFrame


@mock.patch("rcon.automods.tk_autoban.get_player_profile", autospec=True, return_value=None)
@mock.patch(
    "rcon.automods.tk_autoban.BanTeamKillOnConnectUserConfig.load_from_db",
    return_value=BanTeamKillOnConnectUserConfig(
        enabled=True,
        message="Vous avez été banni automatiquement car votre premiere action apres connection est un TEAM KILL.\nSi c'etait un accident demandez votre déban sur: https://discord.io/HLLFR (Via un navigateur, pas directement dans discord)\n\nYou've been banned automatically for TEAM KILLING. Cheers",
        excluded_weapons=["None"],
        max_time_after_connect_minutes=5,
        ignore_tk_after_n_kills=1,
        ignore_tk_after_n_deaths=2,
        discord_webhook_message="{player} banned for TK right after connecting",
        whitelist_players=BanTeamKillOnConnectWhiteList(
            has_flag=["✅"], is_vip=True, has_at_least_n_sessions=10
        ),
        blacklist_id=0,
    ),
)
def test_ban_excluded_weapon(*args):
    tk_log = {
        "version": 1,
        "timestamp_ms": 1612695641000,
        "action": "TEAM KILL",
        "player_name_1": "[ARC] DYDSO ★ツ",
        "player_id_1": 76561198091327692,
        "player_name_2": "Francky Mc Fly",
        "player_id_2": 76561198091327692,
        "weapon": "None",
        "raw": "[646 ms (1612695641)] TEAM KILL: [ARC] DYDSO ★ツ(Axis/76561198091327692) -> Francky Mc Fly(Axis/76561198133214514) with None",
        "content": "[ARC] DYDSO ★ツ(Axis/76561198091327692) -> Francky Mc Fly(Axis/76561198133214514) with None",
    }
    logs = [
        tk_log,
        {
            "id": 1381028,
            "version": 1,
            "creation_time": "2021-02-07T11:02:11.725",
            "timestamp_ms": 1612695428000,
            "action": "CONNECTED",
            "player_name_1": "[ARC] DYDSO ★ツ",
            "player_name_2": None,
            "weapon": None,
            "player_id_1": None,
            "player_id_2": None,
            "raw": "[600 ms (1612695428)] CONNECTED [ARC] DYDSO ★ツ",
            "content": "[ARC] DYDSO ★ツ",
            "server": "1",
        },
    ]

    with (
        mock.patch("rcon.automods.tk_autoban.Rcon") as rcon,
        mock.patch(
            "rcon.automods.tk_autoban.get_recent_logs", return_value={"logs": logs}
        ) as get,
    ):
        rcon.get_vips_ids = mock.MagicMock(return_value=[])
        auto_ban_if_tks_right_after_connection(rcon, tk_log)
        rcon.perma_ban.assert_not_called()


@mock.patch("rcon.automods.tk_autoban.get_player_profile", autospec=True, return_value=None)
def test_ban_success(*args):
    tk_log: StructuredLogLineWithMetaData = {
        "version": 1,
        "timestamp_ms": 1612695641000,
        "event_time": datetime.datetime.fromtimestamp(1612695641),
        "action": "TEAM KILL",
        "player_name_1": "[ARC] DYDSO ★ツ",
        "player_id_1": "76561198091327692",
        "player_name_2": "Francky Mc Fly",
        "player_id_2": "76561198091327692",
        "weapon": "G43",
        "raw": "[646 ms (1612695641)] TEAM KILL: [ARC] DYDSO ★ツ(Axis/76561198091327692) -> Francky Mc Fly(Axis/76561198133214514) with None",
        "content": "[ARC] DYDSO ★ツ(Axis/76561198091327692) -> Francky Mc Fly(Axis/76561198133214514) with None",
    }
    logs = [
        tk_log,
        tk_log,
        {
            "id": 1381028,
            "version": 1,
            "creation_time": "2021-02-07T11:02:11.725",
            "timestamp_ms": 1612695428000,
            "action": "CONNECTED",
            "player_name_1": "[ARC] DYDSO ★ツ",
            "player_name_2": None,
            "weapon": None,
            "player_id_1": None,
            "player_id_2": None,
            "raw": "[600 ms (1612695428)] CONNECTED [ARC] DYDSO ★ツ",
            "content": "[ARC] DYDSO ★ツ",
            "server": "1",
        },
    ]

    config = BanTeamKillOnConnectUserConfig(
        enabled=True,
        message="Vous avez été banni automatiquement car votre premiere action apres connection est un TEAM KILL.\nSi c'etait un accident demandez votre déban sur: https://discord.io/HLLFR (Via un navigateur, pas directement dans discord)\n\nYou've been banned automatically for TEAM KILLING. Cheers",
        author_name="HATERS GONNA HATE",
        excluded_weapons=["None"],
        max_time_after_connect_minutes=5,
        ignore_tk_after_n_kills=1,
        ignore_tk_after_n_deaths=2,
        discord_webhook_message="{player} banned for TK right after connecting",
        whitelist_players=BanTeamKillOnConnectWhiteList(
            has_flag=["✅"], is_vip=True, has_at_least_n_sessions=10
        ),
        blacklist_id=0,
    )
    with (
        mock.patch("rcon.automods.tk_autoban.Rcon") as rcon,
        mock.patch(
            "rcon.automods.tk_autoban.get_recent_logs", return_value={"logs": logs}
        ),
    ):
        rcon.get_vips_ids = mock.MagicMock(return_value=[])
        result = auto_ban_if_tks_right_after_connection(rcon, tk_log, config)
        assert result


@mock.patch("rcon.automods.tk_autoban.get_player_profile", autospec=True, return_value=None)
def test_ban_success_temp_ban(*args):
    tk_log = {
        "version": 1,
        "timestamp_ms": 1612695641000,
        "action": "TEAM KILL",
        "player_name_1": "[ARC] DYDSO ★ツ",
        "player_id_1": "76561198091327692",
        "player_name_2": "Francky Mc Fly",
        "player_id_2": "76561198091327692",
        "weapon": "G43",
        "raw": "[646 ms (1612695641)] TEAM KILL: [ARC] DYDSO ★ツ(Axis/76561198091327692) -> Francky Mc Fly(Axis/76561198133214514) with None",
        "content": "[ARC] DYDSO ★ツ(Axis/76561198091327692) -> Francky Mc Fly(Axis/76561198133214514) with None",
    }
    logs = [
        tk_log,
        tk_log,
        {
            "id": 1381028,
            "version": 1,
            "creation_time": "2021-02-07T11:02:11.725",
            "timestamp_ms": 1612695428000,
            "action": "CONNECTED",
            "player_name_1": "[ARC] DYDSO ★ツ",
            "player_name_2": None,
            "weapon": None,
            "player_id_1": None,
            "player_id_2": None,
            "raw": "[600 ms (1612695428)] CONNECTED [ARC] DYDSO ★ツ",
            "content": "[ARC] DYDSO ★ツ",
            "server": "1",
        },
    ]

    config = BanTeamKillOnConnectUserConfig(
        enabled=True,
        message="Vous avez été banni automatiquement car votre premiere action apres connection est un TEAM KILL.\nSi c'etait un accident demandez votre déban sur: https://discord.io/HLLFR (Via un navigateur, pas directement dans discord)\n\nYou've been banned automatically for TEAM KILLING. Cheers",
        author_name="HATERS GONNA HATE",
        excluded_weapons=["None"],
        max_time_after_connect_minutes=5,
        ignore_tk_after_n_kills=1,
        ignore_tk_after_n_deaths=2,
        discord_webhook_message="{player} banned for TK right after connecting",
        whitelist_players=BanTeamKillOnConnectWhiteList(
            has_flag=["✅"], is_vip=True, has_at_least_n_sessions=10
        ),
        blacklist_id=0,
        ban_duration=TimeFrame(days=1),
    )

    with (
        mock.patch("rcon.automods.tk_autoban.Rcon") as rcon,
        mock.patch(
            "rcon.automods.tk_autoban.get_recent_logs", return_value={"logs": logs}
        ),
    ):
        rcon.get_vips_ids = mock.MagicMock(return_value=[])
        result = auto_ban_if_tks_right_after_connection(rcon, tk_log, config)
        assert result and result["expires_at"]


@mock.patch("rcon.automods.tk_autoban.get_player_profile", autospec=True, return_value=None)
def test_ban_ignored_kill(*args):
    tk_log = {
        "version": 1,
        "timestamp_ms": 1612695641000,
        "action": "TEAM KILL",
        "player_name_1": "[ARC] DYDSO ★ツ",
        "player_id_1": "76561198091327692",
        "player_name_2": "Francky Mc Fly",
        "player_id_2": "76561198091327692",
        "weapon": "G43",
        "raw": "[646 ms (1612695641)] TEAM KILL: [ARC] DYDSO ★ツ(Axis/76561198091327692) -> Francky Mc Fly(Axis/76561198133214514) with None",
        "content": "[ARC] DYDSO ★ツ(Axis/76561198091327692) -> Francky Mc Fly(Axis/76561198133214514) with None",
    }
    logs = [
        tk_log,
        {
            "version": 1,
            "timestamp_ms": 1612695641000,
            "action": "KILL",
            "player_name_1": "[ARC] DYDSO ★ツ",
            "player_id_1": "76561198091327692",
            "player_name_2": "Francky Mc Fly",
            "player_id_2": "76561198091327692",
            "weapon": "G43",
            "raw": "[646 ms (1612695641)] TEAM KILL: [ARC] DYDSO ★ツ(Axis/76561198091327692) -> Francky Mc Fly(Axis/76561198133214514) with None",
            "content": "[ARC] DYDSO ★ツ(Axis/76561198091327692) -> Francky Mc Fly(Axis/76561198133214514) with None",
        },
        {
            "id": 1381028,
            "version": 1,
            "creation_time": "2021-02-07T11:02:11.725",
            "timestamp_ms": 1612695428000,
            "action": "CONNECTED",
            "player_name_1": "[ARC] DYDSO ★ツ",
            "player_name_2": None,
            "weapon": None,
            "player_id_1": None,
            "player_id_2": None,
            "raw": "[600 ms (1612695428)] CONNECTED [ARC] DYDSO ★ツ",
            "content": "[ARC] DYDSO ★ツ",
            "server": "1",
        },
    ]
    config = BanTeamKillOnConnectUserConfig(
        enabled=True,
        message="Vous avez été banni automatiquement car votre premiere action apres connection est un TEAM KILL.\nSi c'etait un accident demandez votre déban sur: https://discord.io/HLLFR (Via un navigateur, pas directement dans discord)\n\nYou've been banned automatically for TEAM KILLING. Cheers",
        author_name="HATERS GONNA HATE",
        excluded_weapons=["None"],
        max_time_after_connect_minutes=5,
        ignore_tk_after_n_kills=1,
        ignore_tk_after_n_deaths=2,
        discord_webhook_message="{player} banned for TK right after connecting",
        whitelist_players=BanTeamKillOnConnectWhiteList(
            has_flag=["✅"], is_vip=True, has_at_least_n_sessions=10
        ),
    )
    with (
        mock.patch("rcon.automods.tk_autoban.Rcon") as rcon,
        mock.patch(
            "rcon.automods.tk_autoban.get_recent_logs", return_value={"logs": logs}
        ),
    ):
        rcon.get_vips_ids = mock.MagicMock(return_value=[])
        auto_ban_if_tks_right_after_connection(rcon, tk_log, config)
        rcon.perma_ban.assert_not_called()


@mock.patch("rcon.automods.tk_autoban.get_player_profile", autospec=True, return_value=None)
def test_ban_count_one_death(*args):
    tk_log: StructuredLogLineWithMetaData = {
        "version": 1,
        "timestamp_ms": 1612695641000,
        "event_time": datetime.datetime.fromtimestamp(1612695641),
        "action": "TEAM KILL",
        "player_name_1": "[ARC] DYDSO ★ツ",
        "player_id_1": "76561198091327692",
        "player_name_2": "Francky Mc Fly",
        "player_id_2": "76561198091327692",
        "weapon": "G43",
        "raw": "[646 ms (1612695641)] TEAM KILL: [ARC] DYDSO ★ツ(Axis/76561198091327692) -> Francky Mc Fly(Axis/76561198133214514) with None",
        "content": "[ARC] DYDSO ★ツ(Axis/76561198091327692) -> Francky Mc Fly(Axis/76561198133214514) with None",
    }
    logs = [
        tk_log,
        tk_log,
        {
            "version": 1,
            "timestamp_ms": 1612695641000,
            "action": "KILL",
            "player_name_2": "[ARC] DYDSO ★ツ",
            "player_id_2": "76561198091327692",
            "player_name_1": "Francky Mc Fly",
            "player_id_1": "76561198091327692",
            "weapon": "G43",
            "raw": "[646 ms (1612695641)] TEAM KILL: [ARC] DYDSO ★ツ(Axis/76561198091327692) -> Francky Mc Fly(Axis/76561198133214514) with None",
            "content": "[ARC] DYDSO ★ツ(Axis/76561198091327692) -> Francky Mc Fly(Axis/76561198133214514) with None",
        },
        {
            "id": 1381028,
            "version": 1,
            "creation_time": "2021-02-07T11:02:11.725",
            "timestamp_ms": 1612695428000,
            "action": "CONNECTED",
            "player_name_1": "[ARC] DYDSO ★ツ",
            "player_name_2": None,
            "weapon": None,
            "player_id_1": None,
            "player_id_2": None,
            "raw": "[600 ms (1612695428)] CONNECTED [ARC] DYDSO ★ツ",
            "content": "[ARC] DYDSO ★ツ",
            "server": "1",
        },
    ]

    config = BanTeamKillOnConnectUserConfig(
        enabled=True,
        message="Vous avez été banni automatiquement car votre premiere action apres connection est un TEAM KILL.\nSi c'etait un accident demandez votre déban sur: https://discord.io/HLLFR (Via un navigateur, pas directement dans discord)\n\nYou've been banned automatically for TEAM KILLING. Cheers",
        author_name="HATERS GONNA HATE",
        excluded_weapons=["None"],
        max_time_after_connect_minutes=5,
        ignore_tk_after_n_kills=1,
        ignore_tk_after_n_deaths=2,
        discord_webhook_message="{player} banned for TK right after connecting",
        whitelist_players=BanTeamKillOnConnectWhiteList(
            has_flag=["✅"], is_vip=True, has_at_least_n_sessions=10
        ),
        blacklist_id=0,
    )

    with (
        mock.patch("rcon.automods.tk_autoban.Rcon") as rcon,
        mock.patch(
            "rcon.automods.tk_autoban.get_recent_logs", return_value={"logs": logs}
        ),
    ):
        rcon.get_vips_ids = mock.MagicMock(return_value=[])
        result = auto_ban_if_tks_right_after_connection(rcon, tk_log, config)
        assert result


@mock.patch("rcon.automods.tk_autoban.get_player_profile", autospec=True, return_value=None)
def test_ban_ignored_2_death(*args):
    tk_log = {
        "version": 1,
        "timestamp_ms": 1612695641000,
        "action": "TEAM KILL",
        "player_name_1": "[ARC] DYDSO ★ツ",
        "player_id_1": "76561198091327692",
        "player_name_2": "Francky Mc Fly",
        "player_id_2": "76561198091327692",
        "weapon": "G43",
        "raw": "[646 ms (1612695641)] TEAM KILL: [ARC] DYDSO ★ツ(Axis/76561198091327692) -> Francky Mc Fly(Axis/76561198133214514) with None",
        "content": "[ARC] DYDSO ★ツ(Axis/76561198091327692) -> Francky Mc Fly(Axis/76561198133214514) with None",
    }
    logs = [
        tk_log,
        {
            "version": 1,
            "timestamp_ms": 1612695641000,
            "action": "KILL",
            "player_name_2": "[ARC] DYDSO ★ツ",
            "player_id_2": "76561198091327692",
            "player_name_1": "Francky Mc Fly",
            "player_id_1": "76561198091327692",
            "weapon": "G43",
            "raw": "[646 ms (1612695641)] TEAM KILL: [ARC] DYDSO ★ツ(Axis/76561198091327692) -> Francky Mc Fly(Axis/76561198133214514) with None",
            "content": "[ARC] DYDSO ★ツ(Axis/76561198091327692) -> Francky Mc Fly(Axis/76561198133214514) with None",
        },
        {
            "version": 1,
            "timestamp_ms": 1612695641000,
            "action": "KILL",
            "player_name_2": "[ARC] DYDSO ★ツ",
            "player_id_2": "76561198091327692",
            "player_name_1": "Francky Mc Fly",
            "player_id_1": "76561198091327692",
            "weapon": "G43",
            "raw": "[646 ms (1612695641)] TEAM KILL: [ARC] DYDSO ★ツ(Axis/76561198091327692) -> Francky Mc Fly(Axis/76561198133214514) with None",
            "content": "[ARC] DYDSO ★ツ(Axis/76561198091327692) -> Francky Mc Fly(Axis/76561198133214514) with None",
        },
        {
            "id": 1381028,
            "version": 1,
            "creation_time": "2021-02-07T11:02:11.725",
            "timestamp_ms": 1612695428000,
            "action": "CONNECTED",
            "player_name_1": "[ARC] DYDSO ★ツ",
            "player_name_2": None,
            "weapon": None,
            "player_id_1": None,
            "player_id_2": None,
            "raw": "[600 ms (1612695428)] CONNECTED [ARC] DYDSO ★ツ",
            "content": "[ARC] DYDSO ★ツ",
            "server": "1",
        },
    ]

    config = BanTeamKillOnConnectUserConfig(
        enabled=True,
        message="Vous avez été banni automatiquement car votre premiere action apres connection est un TEAM KILL.\nSi c'etait un accident demandez votre déban sur: https://discord.io/HLLFR (Via un navigateur, pas directement dans discord)\n\nYou've been banned automatically for TEAM KILLING. Cheers",
        author_name="HATERS GONNA HATE",
        excluded_weapons=["None"],
        max_time_after_connect_minutes=5,
        ignore_tk_after_n_kills=1,
        ignore_tk_after_n_deaths=2,
        discord_webhook_message="{player} banned for TK right after connecting",
        whitelist_players=BanTeamKillOnConnectWhiteList(
            has_flag=["✅"], is_vip=True, has_at_least_n_sessions=10
        ),
    )

    with (
        mock.patch("rcon.automods.tk_autoban.Rcon") as rcon,
        mock.patch(
            "rcon.automods.tk_autoban.get_recent_logs", return_value={"logs": logs}
        ),
    ):
        rcon.get_vips_ids = mock.MagicMock(return_value=[])
        auto_ban_if_tks_right_after_connection(rcon, tk_log, config)
        rcon.perma_ban.assert_not_called()
