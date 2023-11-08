from unittest import mock

from rcon.game_logs import auto_ban_if_tks_right_after_connection


@mock.patch("rcon.game_logs.get_player_profile", autospec=True, return_value=None)
@mock.patch(
    "rcon.game_logs.get_config",
    return_value={
        "BAN_TK_ON_CONNECT": {
            "enabled": True,
            "message": "Vous avez été banni automatiquement car votre premiere action apres connection est un TEAM KILL.\nSi c'etait un accident demandez votre déban sur: https://discord.io/HLLFR (Via un navigateur, pas directement dans discord)\n\nYou've been banned automatically for TEAM KILLING. Cheers",
            "author_name": "HATERS GONNA HATE",
            "exclude_weapons": ["None"],
            "max_time_after_connect_minutes": 5,
            "ignore_tk_after_n_kills": 1,
            "ignore_tk_after_n_death": 2,
            "discord_webhook_url": "",
            "discord_webhook_message": "{player} banned for TK right after connecting",
            "whitelist_players": {
                "has_flag": ["✅"],
                "is_vip": True,
                "has_at_least_n_sessions": 10,
            },
        },
    },
)
def test_ban_excluded_weapon(*args):
    tk_log = {
        "version": 1,
        "timestamp_ms": 1612695641000,
        "action": "TEAM KILL",
        "player": "[ARC] DYDSO ★ツ",
        "steam_id_64_1": 76561198091327692,
        "player2": "Francky Mc Fly",
        "steam_id_64_1": 76561198091327692,
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
            "player": "[ARC] DYDSO ★ツ",
            "player2": None,
            "weapon": None,
            "steam_id_64_1": None,
            "steam_id_64_1": None,
            "raw": "[600 ms (1612695428)] CONNECTED [ARC] DYDSO ★ツ",
            "content": "[ARC] DYDSO ★ツ",
            "server": "1",
        },
    ]

    with mock.patch("rcon.game_logs.Rcon") as rcon, mock.patch(
        "rcon.game_logs.get_recent_logs", return_value={"logs": logs}
    ) as get:
        rcon.get_vips_ids = mock.MagicMock(return_value=[])
        auto_ban_if_tks_right_after_connection(rcon, tk_log)
        rcon.do_perma_ban.assert_not_called()


@mock.patch("rcon.game_logs.get_player_profile", autospec=True, return_value=None)
@mock.patch(
    "rcon.game_logs.get_config",
    return_value={
        "BAN_TK_ON_CONNECT": {
            "enabled": True,
            "message": "Vous avez été banni automatiquement car votre premiere action apres connection est un TEAM KILL.\nSi c'etait un accident demandez votre déban sur: https://discord.io/HLLFR (Via un navigateur, pas directement dans discord)\n\nYou've been banned automatically for TEAM KILLING. Cheers",
            "author_name": "HATERS GONNA HATE",
            "exclude_weapons": ["None"],
            "max_time_after_connect_minutes": 5,
            "ignore_tk_after_n_kills": 1,
            "ignore_tk_after_n_death": 2,
            "discord_webhook_url": "",
            "discord_webhook_message": "{player} banned for TK right after connecting",
            "whitelist_players": {
                "has_flag": ["✅"],
                "is_vip": True,
                "has_at_least_n_sessions": 10,
            },
        },
    },
)
def test_ban_success(*args):
    tk_log = {
        "version": 1,
        "timestamp_ms": 1612695641000,
        "action": "TEAM KILL",
        "player": "[ARC] DYDSO ★ツ",
        "steam_id_64_1": 76561198091327692,
        "player2": "Francky Mc Fly",
        "steam_id_64_1": 76561198091327692,
        "weapon": "G43",
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
            "player": "[ARC] DYDSO ★ツ",
            "player2": None,
            "weapon": None,
            "steam_id_64_1": None,
            "steam_id_64_1": None,
            "raw": "[600 ms (1612695428)] CONNECTED [ARC] DYDSO ★ツ",
            "content": "[ARC] DYDSO ★ツ",
            "server": "1",
        },
    ]

    with mock.patch("rcon.game_logs.Rcon") as rcon, mock.patch(
        "rcon.game_logs.get_recent_logs", return_value={"logs": logs}
    ) as get:
        rcon.get_vips_ids = mock.MagicMock(return_value=[])
        auto_ban_if_tks_right_after_connection(rcon, tk_log)
        rcon.do_perma_ban.assert_called()


@mock.patch("rcon.game_logs.get_player_profile", autospec=True, return_value=None)
@mock.patch(
    "rcon.game_logs.get_config",
    return_value={
        "BAN_TK_ON_CONNECT": {
            "enabled": True,
            "message": "Vous avez été banni automatiquement car votre premiere action apres connection est un TEAM KILL.\nSi c'etait un accident demandez votre déban sur: https://discord.io/HLLFR (Via un navigateur, pas directement dans discord)\n\nYou've been banned automatically for TEAM KILLING. Cheers",
            "author_name": "HATERS GONNA HATE",
            "exclude_weapons": ["None"],
            "max_time_after_connect_minutes": 5,
            "ignore_tk_after_n_kills": 1,
            "ignore_tk_after_n_death": 2,
            "discord_webhook_url": "",
            "discord_webhook_message": "{player} banned for TK right after connecting",
            "whitelist_players": {
                "has_flag": ["✅"],
                "is_vip": True,
                "has_at_least_n_sessions": 10,
            },
        },
    },
)
def test_ban_ignored_kill(*args):
    tk_log = {
        "version": 1,
        "timestamp_ms": 1612695641000,
        "action": "TEAM KILL",
        "player": "[ARC] DYDSO ★ツ",
        "steam_id_64_1": 76561198091327692,
        "player2": "Francky Mc Fly",
        "steam_id_64_1": 76561198091327692,
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
            "player": "[ARC] DYDSO ★ツ",
            "steam_id_64_1": 76561198091327692,
            "player2": "Francky Mc Fly",
            "steam_id_64_1": 76561198091327692,
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
            "player": "[ARC] DYDSO ★ツ",
            "player2": None,
            "weapon": None,
            "steam_id_64_1": None,
            "steam_id_64_1": None,
            "raw": "[600 ms (1612695428)] CONNECTED [ARC] DYDSO ★ツ",
            "content": "[ARC] DYDSO ★ツ",
            "server": "1",
        },
    ]

    with mock.patch("rcon.game_logs.Rcon") as rcon, mock.patch(
        "rcon.game_logs.get_recent_logs", return_value={"logs": logs}
    ) as get:
        rcon.get_vips_ids = mock.MagicMock(return_value=[])
        auto_ban_if_tks_right_after_connection(rcon, tk_log)
        rcon.do_perma_ban.assert_not_called()


@mock.patch("rcon.game_logs.get_player_profile", autospec=True, return_value=None)
@mock.patch(
    "rcon.game_logs.get_config",
    return_value={
        "BAN_TK_ON_CONNECT": {
            "enabled": True,
            "message": "Vous avez été banni automatiquement car votre premiere action apres connection est un TEAM KILL.\nSi c'etait un accident demandez votre déban sur: https://discord.io/HLLFR (Via un navigateur, pas directement dans discord)\n\nYou've been banned automatically for TEAM KILLING. Cheers",
            "author_name": "HATERS GONNA HATE",
            "exclude_weapons": ["None"],
            "max_time_after_connect_minutes": 5,
            "ignore_tk_after_n_kills": 1,
            "ignore_tk_after_n_death": 2,
            "discord_webhook_url": "",
            "discord_webhook_message": "{player} banned for TK right after connecting",
            "whitelist_players": {
                "has_flag": ["✅"],
                "is_vip": True,
                "has_at_least_n_sessions": 10,
            },
        },
    },
)
def test_ban_count_one_death(*args):
    tk_log = {
        "version": 1,
        "timestamp_ms": 1612695641000,
        "action": "TEAM KILL",
        "player": "[ARC] DYDSO ★ツ",
        "steam_id_64_1": 76561198091327692,
        "player2": "Francky Mc Fly",
        "steam_id_64_1": 76561198091327692,
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
            "player2": "[ARC] DYDSO ★ツ",
            "steam_id_64_2": 76561198091327692,
            "player": "Francky Mc Fly",
            "steam_id_64_1": 76561198091327692,
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
            "player": "[ARC] DYDSO ★ツ",
            "player2": None,
            "weapon": None,
            "steam_id_64_1": None,
            "steam_id_64_1": None,
            "raw": "[600 ms (1612695428)] CONNECTED [ARC] DYDSO ★ツ",
            "content": "[ARC] DYDSO ★ツ",
            "server": "1",
        },
    ]

    with mock.patch("rcon.game_logs.Rcon") as rcon, mock.patch(
        "rcon.game_logs.get_recent_logs", return_value={"logs": logs}
    ) as get:
        rcon.get_vips_ids = mock.MagicMock(return_value=[])
        auto_ban_if_tks_right_after_connection(rcon, tk_log)
        rcon.do_perma_ban.assert_called()


@mock.patch("rcon.game_logs.get_player_profile", autospec=True, return_value=None)
@mock.patch(
    "rcon.game_logs.get_config",
    return_value={
        "BAN_TK_ON_CONNECT": {
            "enabled": True,
            "message": "Vous avez été banni automatiquement car votre premiere action apres connection est un TEAM KILL.\nSi c'etait un accident demandez votre déban sur: https://discord.io/HLLFR (Via un navigateur, pas directement dans discord)\n\nYou've been banned automatically for TEAM KILLING. Cheers",
            "author_name": "HATERS GONNA HATE",
            "exclude_weapons": ["None"],
            "max_time_after_connect_minutes": 5,
            "ignore_tk_after_n_kills": 1,
            "ignore_tk_after_n_death": 2,
            "discord_webhook_url": "",
            "discord_webhook_message": "{player} banned for TK right after connecting",
            "whitelist_players": {
                "has_flag": ["✅"],
                "is_vip": True,
                "has_at_least_n_sessions": 10,
            },
        },
    },
)
def test_ban_ignored_2_death(*args):
    tk_log = {
        "version": 1,
        "timestamp_ms": 1612695641000,
        "action": "TEAM KILL",
        "player": "[ARC] DYDSO ★ツ",
        "steam_id_64_1": 76561198091327692,
        "player2": "Francky Mc Fly",
        "steam_id_64_1": 76561198091327692,
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
            "player2": "[ARC] DYDSO ★ツ",
            "steam_id_64_2": 76561198091327692,
            "player": "Francky Mc Fly",
            "steam_id_64_1": 76561198091327692,
            "weapon": "G43",
            "raw": "[646 ms (1612695641)] TEAM KILL: [ARC] DYDSO ★ツ(Axis/76561198091327692) -> Francky Mc Fly(Axis/76561198133214514) with None",
            "content": "[ARC] DYDSO ★ツ(Axis/76561198091327692) -> Francky Mc Fly(Axis/76561198133214514) with None",
        },
        {
            "version": 1,
            "timestamp_ms": 1612695641000,
            "action": "KILL",
            "player2": "[ARC] DYDSO ★ツ",
            "steam_id_64_2": 76561198091327692,
            "player": "Francky Mc Fly",
            "steam_id_64_1": 76561198091327692,
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
            "player": "[ARC] DYDSO ★ツ",
            "player2": None,
            "weapon": None,
            "steam_id_64_1": None,
            "steam_id_64_1": None,
            "raw": "[600 ms (1612695428)] CONNECTED [ARC] DYDSO ★ツ",
            "content": "[ARC] DYDSO ★ツ",
            "server": "1",
        },
    ]

    with mock.patch("rcon.game_logs.Rcon") as rcon, mock.patch(
        "rcon.game_logs.get_recent_logs", return_value={"logs": logs}
    ) as get:
        rcon.get_vips_ids = mock.MagicMock(return_value=[])
        auto_ban_if_tks_right_after_connection(rcon, tk_log)
        rcon.do_perma_ban.assert_not_called()
