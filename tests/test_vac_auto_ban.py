import pytest
from rcon.hooks import should_ban


@pytest.mark.parametrize(
    "bans, max_game_bans, max_days_since_ban, player_flags, whitelist_flags, expected",
    [
        (
            {
                "SteamId": "...",
                "CommunityBanned": False,
                "VACBanned": False,
                "NumberOfVACBans": 0,
                "DaysSinceLastBan": 0,
                "NumberOfGameBans": 0,
                "EconomyBan": "none",
            },
            float("inf"),
            1,
            ["🤡"],
            ["🤡"],
            False,
        ),
        (
            {
                "SteamId": "...",
                "CommunityBanned": False,
                "VACBanned": False,
                "NumberOfVACBans": 0,
                "DaysSinceLastBan": 0,
                "NumberOfGameBans": 0,
                "EconomyBan": "none",
            },
            float("inf"),
            1,
            [],
            [],
            False,
        ),
        (
            {
                "SteamId": "...",
                "CommunityBanned": True,
                "VACBanned": False,
                "NumberOfVACBans": 0,
                "DaysSinceLastBan": 0,
                "NumberOfGameBans": 0,
                "EconomyBan": "none",
            },
            float("inf"),
            1,
            [],
            [],
            False,
        ),
        (
            {
                "SteamId": "...",
                "CommunityBanned": True,
                "VACBanned": False,
                "NumberOfVACBans": 0,
                "DaysSinceLastBan": 0,
                "NumberOfGameBans": 0,
                "EconomyBan": "none",
            },
            float("inf"),
            1,
            [],
            [],
            False,
        ),
        (
            {
                "SteamId": "...",
                "CommunityBanned": True,
                "VACBanned": False,
                "NumberOfVACBans": 0,
                "DaysSinceLastBan": 1,
                "NumberOfGameBans": 5,
                "EconomyBan": "none",
            },
            float("inf"),
            40,
            [],
            [],
            False,
        ),
        (
            {
                "SteamId": "...",
                "CommunityBanned": True,
                "VACBanned": False,
                "NumberOfVACBans": 0,
                "DaysSinceLastBan": 1,
                "NumberOfGameBans": 5,
                "EconomyBan": "none",
            },
            6,
            40,
            [],
            [],
            False,
        ),
    ],
)
def test_should_not_ban(
    bans, max_game_bans, max_days_since_ban, player_flags, whitelist_flags, expected
):
    assert (
        should_ban(
            bans=bans,
            max_game_bans=max_game_bans,
            max_days_since_ban=max_days_since_ban,
            player_flags=player_flags,
            whitelist_flags=whitelist_flags,
        )
        == expected
    )


@pytest.mark.parametrize(
    "bans, max_game_bans, max_days_since_ban, player_flags, whitelist_flags, expected",
    [
        (
            {
                "SteamId": "...",
                "CommunityBanned": False,
                "VACBanned": True,
                "NumberOfVACBans": 0,
                "DaysSinceLastBan": 1,
                "NumberOfGameBans": 0,
                "EconomyBan": "none",
            },
            float("inf"),
            40,
            [],
            [],
            True,
        ),
        (
            {
                "SteamId": "...",
                "CommunityBanned": True,
                "VACBanned": True,
                "NumberOfVACBans": 0,
                "DaysSinceLastBan": 1,
                "NumberOfGameBans": 5,
                "EconomyBan": "none",
            },
            5,
            4,
            [],
            [],
            True,
        ),
        (
            {
                "SteamId": "...",
                "CommunityBanned": True,
                "VACBanned": False,
                "NumberOfVACBans": 0,
                "DaysSinceLastBan": 1,
                "NumberOfGameBans": 5,
                "EconomyBan": "none",
            },
            5,
            4,
            [],
            [],
            True,
        ),
        (
            {
                "SteamId": "...",
                "CommunityBanned": True,
                "VACBanned": True,
                "NumberOfVACBans": 0,
                "DaysSinceLastBan": 1,
                "NumberOfGameBans": 1,
                "EconomyBan": "none",
            },
            1,
            4,
            [],
            [],
            True,
        ),
        (
            {
                "SteamId": "...",
                "CommunityBanned": True,
                "VACBanned": True,
                "NumberOfVACBans": 0,
                "DaysSinceLastBan": 1,
                "NumberOfGameBans": 1,
                "EconomyBan": "none",
            },
            1,
            4,
            [],
            ["🤡"],
            True,
        ),
    ],
)
def test_should_ban(
    bans, max_game_bans, max_days_since_ban, player_flags, whitelist_flags, expected
):
    assert (
        should_ban(
            bans=bans,
            max_game_bans=max_game_bans,
            max_days_since_ban=max_days_since_ban,
            player_flags=player_flags,
            whitelist_flags=whitelist_flags,
        )
        == expected
    )
