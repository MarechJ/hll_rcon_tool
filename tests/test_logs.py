from datetime import datetime

import pytest

from rcon.extended_commands import Rcon


# Test that we successfully split raw log lines from the game server
# into the time stamp and actual log line
@pytest.mark.parametrize(
    "raw_logs, expected",
    [
        (
            """
[29:55 min (1606340690)] KILL: Karadoc(Axis/76561198080212634) -> Bullitt-FR(Allies/76561198000776367) with G43
[29:42 min (1606340690)] KILL: 湊あくあ(Axis/76561198202984515) -> fguitou(Allies/76561198034763447) with None
[3:35 min (1675366030)] TEAM KILL: Ð¡Ð°ÑÐºÐ°(Allies/76561198346893462) -> Milk Dick(Allies/76561198044472891) with 155MM HOWITZER [M114]
[2:07:28 hours (1675358597)] TEAM KILL: Oz(Allies/76561198163789126) -> Sic_Anger(Allies/76561199201574614) with PPSH 41 W/DRUM
[29:37 min (1606340690)] CONNECTED Waxxeer (12345678901234567)
[29:40 min (1606340690)] DISCONNECTED Dieter Schlüter: b (12345678901234567)
[1.89 sec (1606340677)] CHAT[Team][bananacocoo(Allies/76561198003251789)]: pas jouable la map
[29:59 min (1606340690)] CHAT[Team][]bananacocoo(Axis/76561198003251789)]: Blah
[29:59 min (1606340690)] CHAT[Unit][bananacocoo : toto(Allies/76561198003251789)]: Blah
[29:59 min (1606340690)] CHAT[Unit][[bananacocoo(Axis/76561198003251789)]: Blah
[8.23 sec (1645012372)] TEAMSWITCH T17 Scott (Axis > None)
[6.14 sec (1645012374)] TEAMSWITCH T17 Scott (None > Allies)
[41.9 sec (1645012996)] KICK: [T17 Scott] has been kicked. [KICKED FOR TEAM KILLING!]
[1:03 min (1645012776)] KICK: [T17 Scott] has been kicked. [BANNED FOR 2 HOURS FOR TEAM KILLING!]
[4:48 min (1646331637)] KICK: [VegaBond] has been kicked. [BANNED FOR 1 HOURS BY THE ADMINISTRATOR!
[27.8 sec (1646334121)] KICK: [GinPick]ledYak] has been kicked. [PERMANENTLY BANNED BY THE ADMINISTRATOR!
[2:00 min (1646137918)] BAN: [(WTH) Abusify] has been banned. [BANNED FOR 2 HOURS BY THE ADMINISTRATOR!
[2:00 min (1646137918)] KICK: [adamtfitz] has been kicked. [YOU WERE KICKED FOR BEING IDLE]
[128 sec (1645012281)] MATCH START UTAH BEACH OFFENSIVE
[6.06 sec (16250121723)] MATCH ENDED `UTAH BEACH OFFENSIVE` ALLIED (1 - 4) AXIS
[57:13 min (1675362812)] Player [Fachi (76561198312191879)] Entered Admin Camera
[15.5 sec (1675360329)] VOTESYS: Player [NoodleArms] Started a vote of type (PVR_Kick_Abuse) against [buscÃ´O-sensei]. VoteID: [2]
[9.85 sec (1675360334)] VOTESYS: Player [Dingbat252] voted [PV_Favour] for VoteID[2]
[4.56 sec (1675360340)] VOTESYS: Vote [2] completed. Result: PVR_Passed
[4.56 sec (1675360340)] VOTESYS: Vote Kick {buscÃ´O-sensei} successfully passed. [For: 2/1 - Against: 0]
[5.73 sec (1675270564)] MESSAGE: player [Tacsquatch(76561198104788712)], content [please ignore this
I just need a multiline message in the RCON logs
to test something]
[4.56 sec (1675270564)] MESSAGE: player [ð“¼ð“ºð“¾ð“²ð“­ð“­ [KRKN](76561198062837577)], content [Please ignore this just need a message in the RCON logs to test something.]

""",
            [
                (
                    "1606340690",
                    "KILL: Karadoc(Axis/76561198080212634) -> Bullitt-FR(Allies/76561198000776367) with G43",
                ),
                (
                    "1606340690",
                    "KILL: 湊あくあ(Axis/76561198202984515) -> fguitou(Allies/76561198034763447) with None",
                ),
                (
                    "1675366030",
                    "TEAM KILL: Ð¡Ð°ÑÐºÐ°(Allies/76561198346893462) -> Milk Dick(Allies/76561198044472891) with 155MM HOWITZER [M114]",
                ),
                (
                    "1675358597",
                    "TEAM KILL: Oz(Allies/76561198163789126) -> Sic_Anger(Allies/76561199201574614) with PPSH 41 W/DRUM",
                ),
                (
                    "1606340690",
                    "CONNECTED Waxxeer (12345678901234567)",
                ),
                (
                    "1606340690",
                    "DISCONNECTED Dieter Schlüter: b (12345678901234567)",
                ),
                (
                    "1606340677",
                    "CHAT[Team][bananacocoo(Allies/76561198003251789)]: pas jouable la map",
                ),
                (
                    "1606340690",
                    "CHAT[Team][]bananacocoo(Axis/76561198003251789)]: Blah",
                ),
                (
                    "1606340690",
                    "CHAT[Unit][bananacocoo : toto(Allies/76561198003251789)]: Blah",
                ),
                (
                    "1606340690",
                    "CHAT[Unit][[bananacocoo(Axis/76561198003251789)]: Blah",
                ),
                (
                    "1645012372",
                    "TEAMSWITCH T17 Scott (Axis > None)",
                ),
                (
                    "1645012374",
                    "TEAMSWITCH T17 Scott (None > Allies)",
                ),
                (
                    "1645012996",
                    "KICK: [T17 Scott] has been kicked. [KICKED FOR TEAM KILLING!]",
                ),
                (
                    "1645012776",
                    "KICK: [T17 Scott] has been kicked. [BANNED FOR 2 HOURS FOR TEAM KILLING!]",
                ),
                (
                    "1646331637",
                    "KICK: [VegaBond] has been kicked. [BANNED FOR 1 HOURS BY THE ADMINISTRATOR!",
                ),
                (
                    "1646334121",
                    "KICK: [GinPick]ledYak] has been kicked. [PERMANENTLY BANNED BY THE ADMINISTRATOR!",
                ),
                (
                    "1646137918",
                    "BAN: [(WTH) Abusify] has been banned. [BANNED FOR 2 HOURS BY THE ADMINISTRATOR!",
                ),
                (
                    "1646137918",
                    "KICK: [adamtfitz] has been kicked. [YOU WERE KICKED FOR BEING IDLE]",
                ),
                (
                    "1645012281",
                    "MATCH START UTAH BEACH OFFENSIVE",
                ),
                (
                    "16250121723",
                    "MATCH ENDED `UTAH BEACH OFFENSIVE` ALLIED (1 - 4) AXIS",
                ),
                (
                    "1675362812",
                    "Player [Fachi (76561198312191879)] Entered Admin Camera",
                ),
                (
                    "1675360329",
                    "VOTESYS: Player [NoodleArms] Started a vote of type (PVR_Kick_Abuse) against [buscÃ´O-sensei]. VoteID: [2]",
                ),
                (
                    "1675360334",
                    "VOTESYS: Player [Dingbat252] voted [PV_Favour] for VoteID[2]",
                ),
                (
                    "1675360340",
                    "VOTESYS: Vote [2] completed. Result: PVR_Passed",
                ),
                (
                    "1675360340",
                    "VOTESYS: Vote Kick {buscÃ´O-sensei} successfully passed. [For: 2/1 - Against: 0]",
                ),
                (
                    "1675270564",
                    "MESSAGE: player [Tacsquatch(76561198104788712)], content [please ignore this\nI just need a multiline message in the RCON logs\nto test something]",
                ),
                (
                    "1675270564",
                    "MESSAGE: player [ð“¼ð“ºð“¾ð“²ð“­ð“­ [KRKN](76561198062837577)], content [Please ignore this just need a message in the RCON logs to test something.]",
                ),
            ],
        )
    ],
)
def test_multiline_parsing(raw_logs, expected):
    assert list(Rcon.split_raw_log_lines(raw_logs)) == list(expected)


@pytest.mark.parametrize(
    "raw_timestamp, expected",
    [
        ("1606999065", datetime(2020, 12, 3, 12, 37, 45)),
    ],
)
def test_timestamp_parsing(raw_timestamp, expected):
    assert Rcon._extract_time(raw_timestamp) == expected


@pytest.mark.parametrize(
    "raw_log_line, expected",
    [
        (
            "KILL: Reduktorius(Axis/76561198136839181) -> Loch(Allies/76561198086167606) with FG42 x4",
            {
                "action": "KILL",
                "player": "Reduktorius",
                "steam_id_64_1": "76561198136839181",
                "player2": "Loch",
                "steam_id_64_2": "76561198086167606",
                "weapon": "FG42 x4",
                "message": "Reduktorius(Axis/76561198136839181) -> Loch(Allies/76561198086167606) with FG42 x4",
                "sub_content": None,
            },
        ),
        (
            "KILL: short(Axis/123) ->(Axis/76561198136839181) -> Loch(Allies/76561198086167606) with FG42 x4",
            {
                "action": "KILL",
                "player": "short(Axis/123) ->",
                "steam_id_64_1": "76561198136839181",
                "player2": "Loch",
                "steam_id_64_2": "76561198086167606",
                "weapon": "FG42 x4",
                "message": "short(Axis/123) ->(Axis/76561198136839181) -> Loch(Allies/76561198086167606) with FG42 x4",
                "sub_content": None,
            },
        ),
    ],
)
def test_kills(
    raw_log_line,
    expected,
):
    assert Rcon.parse_log_line(raw_log_line) == expected


@pytest.mark.parametrize(
    "raw_log_line, expected",
    [
        (
            "TEAM KILL: Cyanide(Allies/76561198010856091) -> HoMbRe CaPaZ(Allies/76561197981416155) with GMC CCKW 353 (Transport)",
            {
                "action": "TEAM KILL",
                "player": "Cyanide",
                "steam_id_64_1": "76561198010856091",
                "player2": "HoMbRe CaPaZ",
                "steam_id_64_2": "76561197981416155",
                "weapon": "GMC CCKW 353 (Transport)",
                "message": "Cyanide(Allies/76561198010856091) -> HoMbRe CaPaZ(Allies/76561197981416155) with GMC CCKW 353 (Transport)",
                "sub_content": None,
            },
        ),
        (
            "TEAM KILL: short(Axis/123) ->(Axis/76561198136839181) -> Loch(Axis/76561198086167606) with FG42 x4",
            {
                "action": "TEAM KILL",
                "player": "short(Axis/123) ->",
                "steam_id_64_1": "76561198136839181",
                "player2": "Loch",
                "steam_id_64_2": "76561198086167606",
                "weapon": "FG42 x4",
                "message": "short(Axis/123) ->(Axis/76561198136839181) -> Loch(Axis/76561198086167606) with FG42 x4",
                "sub_content": None,
            },
        ),
    ],
)
def test_team_kills(
    raw_log_line,
    expected,
):
    assert Rcon.parse_log_line(raw_log_line) == expected


@pytest.mark.parametrize(
    "raw_log_line, expected",
    [
        (
            "DISCONNECTED The Dandy Man (76561197972905683)",
            {
                "action": "DISCONNECTED",
                "player": "The Dandy Man",
                "steam_id_64_1": "76561197972905683",
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "DISCONNECTED The Dandy Man (76561197972905683)",
                "sub_content": None,
            },
        ),
        (
            "DISCONNECTED short(Axis/123) -> (76561198136839181)",
            {
                "action": "DISCONNECTED",
                "player": "short(Axis/123) ->",
                "steam_id_64_1": "76561198136839181",
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "DISCONNECTED short(Axis/123) -> (76561198136839181)",
                "sub_content": None,
            },
        ),
        (
            "CONNECTED The Dandy Man (76561197972905683)",
            {
                "action": "CONNECTED",
                "player": "The Dandy Man",
                "steam_id_64_1": "76561197972905683",
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "CONNECTED The Dandy Man (76561197972905683)",
                "sub_content": None,
            },
        ),
        (
            "CONNECTED short(Axis/123) -> (76561198136839181)",
            {
                "action": "CONNECTED",
                "player": "short(Axis/123) ->",
                "steam_id_64_1": "76561198136839181",
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "CONNECTED short(Axis/123) -> (76561198136839181)",
                "sub_content": None,
            },
        ),
    ],
)
def test_connect_disconnect(raw_log_line, expected):
    assert Rcon.parse_log_line(raw_log_line) == expected


@pytest.mark.parametrize(
    "raw_log_line, expected",
    [
        (
            "CHAT[Unit][i eat chicken nugget(Allies/76561199004674256)]: were we spawning?",
            {
                "action": "CHAT[Allies][Unit]",
                "player": "i eat chicken nugget",
                "steam_id_64_1": "76561199004674256",
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "i eat chicken nugget: were we spawning? (76561199004674256)",
                "sub_content": "were we spawning?",
            },
        ),
        (
            "CHAT[Team][i eat chicken nugget(Allies/76561199004674256)]: were we spawning?",
            {
                "action": "CHAT[Allies][Team]",
                "player": "i eat chicken nugget",
                "steam_id_64_1": "76561199004674256",
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "i eat chicken nugget: were we spawning? (76561199004674256)",
                "sub_content": "were we spawning?",
            },
        ),
        (
            "CHAT[Unit][i eat chicken nugget(Axis/76561199004674256)]: were we spawning?",
            {
                "action": "CHAT[Axis][Unit]",
                "player": "i eat chicken nugget",
                "steam_id_64_1": "76561199004674256",
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "i eat chicken nugget: were we spawning? (76561199004674256)",
                "sub_content": "were we spawning?",
            },
        ),
        (
            "CHAT[Team][i eat chicken nugget(Axis/76561199004674256)]: were we spawning?",
            {
                "action": "CHAT[Axis][Team]",
                "player": "i eat chicken nugget",
                "steam_id_64_1": "76561199004674256",
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "i eat chicken nugget: were we spawning? (76561199004674256)",
                "sub_content": "were we spawning?",
            },
        ),
    ],
)
def test_chat(raw_log_line, expected):
    assert Rcon.parse_log_line(raw_log_line) == expected


@pytest.mark.parametrize(
    "raw_log_line, expected",
    [
        (
            "TEAMSWITCH short(Axis/123) -> (None > Allies)",
            {
                "action": "TEAMSWITCH",
                "player": "short(Axis/123) ->",
                "steam_id_64_1": None,
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "TEAMSWITCH short(Axis/123) -> (None > Allies)",
                "sub_content": "None > Allies",
            },
        ),
        (
            "TEAMSWITCH short(Axis/123) -> (Allies > None)",
            {
                "action": "TEAMSWITCH",
                "player": "short(Axis/123) ->",
                "steam_id_64_1": None,
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "TEAMSWITCH short(Axis/123) -> (Allies > None)",
                "sub_content": "Allies > None",
            },
        ),
        (
            "TEAMSWITCH short(Axis/123) -> (Axis > None)",
            {
                "action": "TEAMSWITCH",
                "player": "short(Axis/123) ->",
                "steam_id_64_1": None,
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "TEAMSWITCH short(Axis/123) -> (Axis > None)",
                "sub_content": "Axis > None",
            },
        ),
        (
            "TEAMSWITCH short(Axis/123) -> (None > Axis)",
            {
                "action": "TEAMSWITCH",
                "player": "short(Axis/123) ->",
                "steam_id_64_1": None,
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "TEAMSWITCH short(Axis/123) -> (None > Axis)",
                "sub_content": "None > Axis",
            },
        ),
    ],
)
def test_teamswitch(raw_log_line, expected):
    assert Rcon.parse_log_line(raw_log_line) == expected


@pytest.mark.parametrize(
    "raw_log_line, expected",
    [
        (
            "KICK: [VegaBond] has been kicked. [BANNED FOR 1 HOURS BY THE ADMINISTRATOR!]",
            {
                "action": "ADMIN BANNED",
                "player": "VegaBond",
                "steam_id_64_1": None,
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "KICK: [VegaBond] has been kicked. [BANNED FOR 1 HOURS BY THE ADMINISTRATOR!]",
                "sub_content": "has been kicked. [BANNED FOR 1 HOURS BY THE ADMINISTRATOR!]",
            },
        ),
        (
            "KICK: [GinPick]ledYak] has been kicked. [PERMANENTLY BANNED BY THE ADMINISTRATOR!]",
            {
                "action": "ADMIN PERMA BANNED",
                "player": "GinPick]ledYak",
                "steam_id_64_1": None,
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "KICK: [GinPick]ledYak] has been kicked. [PERMANENTLY BANNED BY THE ADMINISTRATOR!]",
                "sub_content": "has been kicked. [PERMANENTLY BANNED BY THE ADMINISTRATOR!]",
            },
        ),
        (
            "BAN: [(WTH) Abusify] has been banned. [BANNED FOR 2 HOURS BY THE ADMINISTRATOR!]",
            {
                "action": "ADMIN BANNED",
                "player": "(WTH) Abusify",
                "steam_id_64_1": None,
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "BAN: [(WTH) Abusify] has been banned. [BANNED FOR 2 HOURS BY THE ADMINISTRATOR!]",
                "sub_content": "has been banned. [BANNED FOR 2 HOURS BY THE ADMINISTRATOR!]",
            },
        ),
        (
            "KICK: [adamtfitz] has been kicked. [YOU WERE KICKED FOR BEING IDLE]",
            {
                "action": "ADMIN IDLE",
                "player": "adamtfitz",
                "steam_id_64_1": None,
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "KICK: [adamtfitz] has been kicked. [YOU WERE KICKED FOR BEING IDLE]",
                "sub_content": "has been kicked. [YOU WERE KICKED FOR BEING IDLE]",
            },
        ),
        (
            "KICK: [Duolong] has been kicked. [Host closed the connection.]",
            {
                "action": "ADMIN",
                "player": "Duolong",
                "steam_id_64_1": None,
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "KICK: [Duolong] has been kicked. [Host closed the connection.]",
                "sub_content": "has been kicked. [Host closed the connection.]",
            },
        ),
        (
            "KICK: [rowlanjaet] has been kicked. [Anti-Cheat Authentication timed out (1/2)]",
            {
                "action": "ADMIN ANTI-CHEAT",
                "player": "rowlanjaet",
                "steam_id_64_1": None,
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "KICK: [rowlanjaet] has been kicked. [Anti-Cheat Authentication timed out (1/2)]",
                "sub_content": "has been kicked. [Anti-Cheat Authentication timed out (1/2)]",
            },
        ),
    ],
)
def test_kicks(raw_log_line, expected):
    assert Rcon.parse_log_line(raw_log_line) == expected


@pytest.mark.parametrize(
    "raw_log_line, expected",
    [
        (
            "VOTESYS: Player [Dingbat252] voted [PV_Favour] for VoteID[20]",
            {
                "action": "VOTE",
                "player": "Dingbat252",
                "steam_id_64_1": None,
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "Player [Dingbat252] voted [PV_Favour] for VoteID[20]",
                "sub_content": "Player [Dingbat252] voted [PV_Favour] for VoteID[20]",
            },
        ),
        (
            "VOTESYS: Player [NoodleArms] Started a vote of type (PVR_Kick_Abuse) against [buscÃ´O-sensei]. VoteID: [20]",
            {
                "action": "VOTE STARTED",
                "player": "NoodleArms",
                "steam_id_64_1": None,
                "player2": "buscÃ´O-sensei",
                "steam_id_64_2": None,
                "weapon": None,
                "message": "Player [NoodleArms] Started a vote of type (PVR_Kick_Abuse) against [buscÃ´O-sensei]. VoteID: [20]",
                "sub_content": "Player [NoodleArms] Started a vote of type (PVR_Kick_Abuse) against [buscÃ´O-sensei]. VoteID: [20]",
            },
        ),
        (
            "VOTESYS: Vote [20] completed. Result: PVR_Passed",
            {
                "action": "VOTE COMPLETED",
                "player": None,
                "steam_id_64_1": None,
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "Vote [20] completed. Result: PVR_Passed",
                "sub_content": "Vote [20] completed. Result: PVR_Passed",
            },
        ),
        (
            "VOTESYS: Vote [10] expired before completion",
            {
                "action": "VOTE EXPIRED",
                "player": None,
                "steam_id_64_1": None,
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "Vote [10] expired before completion",
                "sub_content": "Vote [10] expired before completion",
            },
        ),
    ],
)
def test_vote_kicks(raw_log_line, expected):
    assert Rcon.parse_log_line(raw_log_line) == expected


@pytest.mark.parametrize(
    "raw_log_line, expected",
    [
        (
            "Player [Fachi (76561198312191879)] Entered Admin Camera",
            {
                "action": "CAMERA",
                "player": "Fachi",
                "steam_id_64_1": "76561198312191879",
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "[Fachi (76561198312191879)] Entered Admin Camera",
                "sub_content": "Entered Admin Camera",
            },
        ),
        (
            "Player [short(Axis/123) -> (76561198312191879)] Entered Admin Camera",
            {
                "action": "CAMERA",
                "player": "short(Axis/123) ->",
                "steam_id_64_1": "76561198312191879",
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "[short(Axis/123) -> (76561198312191879)] Entered Admin Camera",
                "sub_content": "Entered Admin Camera",
            },
        ),
    ],
)
def test_admin_camera(raw_log_line, expected):
    assert Rcon.parse_log_line(raw_log_line) == expected


@pytest.mark.parametrize(
    "raw_log_line, expected",
    [
        (
            "MATCH START SAINTE-M\u00c8RE-\u00c9GLISE WARFARE",
            {
                "action": "MATCH START",
                "player": None,
                "steam_id_64_1": None,
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "MATCH START SAINTE-M\u00c8RE-\u00c9GLISE WARFARE",
                "sub_content": "SAINTE-M\u00c8RE-\u00c9GLISE WARFARE",
            },
        ),
        (
            "MATCH ENDED `CARENTAN WARFARE` ALLIED (0 - 5) AXIS",
            {
                "action": "MATCH ENDED",
                "player": None,
                "steam_id_64_1": None,
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "MATCH ENDED `CARENTAN WARFARE` ALLIED (0 - 5) AXIS",
                "sub_content": "`CARENTAN WARFARE` ALLIED (0 - 5) AXIS",
            },
        ),
    ],
)
def test_match_start_end(raw_log_line, expected):
    assert Rcon.parse_log_line(raw_log_line) == expected


@pytest.mark.parametrize(
    "raw_log_line, expected",
    [
        (
            "MESSAGE: player [Tacsquatch(76561198062837577)], content [Please ignore this just need a message in the RCON logs to test something.]",
            {
                "action": "MESSAGE",
                "player": "Tacsquatch",
                "steam_id_64_1": "76561198062837577",
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "Tacsquatch(76561198062837577): Please ignore this just need a message in the RCON logs to test something.",
                "sub_content": "Please ignore this just need a message in the RCON logs to test something.",
            },
        ),
        (
            """MESSAGE: player [ð“¼ð“ºð“¾ð“²ð“­ð“­ [KRKN](76561198370630324)], content [please ignore this
I just need a multiline message in the RCON logs
to test something]""",
            {
                "action": "MESSAGE",
                "player": "ð“¼ð“ºð“¾ð“²ð“­ð“­ [KRKN]",
                "steam_id_64_1": "76561198370630324",
                "player2": None,
                "steam_id_64_2": None,
                "weapon": None,
                "message": "ð“¼ð“ºð“¾ð“²ð“­ð“­ [KRKN](76561198370630324): please ignore this\nI just need a multiline message in the RCON logs\nto test something",
                "sub_content": "please ignore this\nI just need a multiline message in the RCON logs\nto test something",
            },
        ),
    ],
)
def test_player_messages(raw_log_line, expected):
    assert Rcon.parse_log_line(raw_log_line) == expected
