from rcon.hooks import should_ban


def test_should_not_ban():
    assert not should_ban(
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
    )

    assert not should_ban(
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
    )

    assert not should_ban(
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
    )

    assert not should_ban(
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
    )

    assert not should_ban(
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
    )


def test_should_ban():
    assert should_ban(
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
    )

    assert should_ban(
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
    )

    assert should_ban(
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
    )

    assert should_ban(
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
    )
