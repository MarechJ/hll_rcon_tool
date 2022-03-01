from unittest import mock

from rcon.extended_commands import Rcon


RAW_LOGS = """
[1.89 sec (1606340677)] CHAT[Team][bananacocoo(Allies/76561198003251789)]: pas jouable la map
[29:55 min (1606340690)] KILL: Karadoc(Axis/76561198080212634) -> Bullitt-FR(Allies/76561198000776367) with G43
[29:42 min (1606340690)] KILL: 湊あくあ(Axis/76561198202984515) -> fguitou(Allies/76561198034763447) with None
[29:42 min (1606340690)] KILL: [CPC] xALF(Allies/76561197960985412) -> Karadoc(Axis/76561198080212634) with MK2_Grenade
[29:40 min (1606340690)] DISCONNECTED Dieter Schlüter: b
[29:37 min (1606340690)] CONNECTED Waxxeer
[29:59 min (1606340690)] CHAT[Unit][bananacocoo : toto(Allies/76561198003251789)]: Blah
[29:59 min (1606340690)] CHAT[Unit][[bananacocoo(Axis/76561198003251789)]: Blah
[29:59 min (1606340690)] CHAT[Team][]bananacocoo(Axis/76561198003251789)]: Blah
[8.23 sec (1645012372)] TEAMSWITCH T17 Scott (Axis > None)
[6.14 sec (1645012374)] TEAMSWITCH T17 Scott (None > Allies)
[41.9 sec (1645012996)] KICK: [T17 Scott] has been kicked. [KICKED FOR TEAM KILLING!]
[1:03 min (1645012776)] KICK: [T17 Scott] has been kicked. [BANNED FOR 2 HOURS FOR TEAM KILLING!]
[128 sec (1645012281)] MATCH START UTAH BEACH OFFENSIVE
[6.06 sec (16250121723)] MATCH ENDED `UTAH BEACH OFFENSIVE` ALLIED (1 - 4) AXIS
[2:00 min (1646137918)] BAN: [(WTH) Abusify] has been banned. [BANNED FOR 2 HOURS BY THE ADMINISTRATOR!

Test message]
[2:00 min (1646137918)] KICK: [(WTH) Abusify] has been kicked. [BANNED FOR 2 HOURS BY THE ADMINISTRATOR!

Test message]
[2:00 min (1646137918)] DISCONNECTED (WTH) Abusify
"""
RAW_VOTE = """
[15:49 min (1606998428)] VOTE Player [[fr]ELsass_blitz] Started a vote of type (PVR_Kick_Abuse) against [拢儿]. VoteID: [1]
[15:47 min (1606998429)] VOTE Player [[ARC] MaTej ★ツ] voted [PV_Favour] for VoteID[1]
[15:42 min (1606998434)] VOTE Vote [1] completed. Result: PVR_Passed
[15:42 min (1606998434)] VOTE Vote Kick {拢儿} successfully passed. [For: 2/0 - Against: 0]
[13:21 min (1606998575)] VOTE Player [Galiat] Started a vote of type (PVR_Kick_Abuse) against [[TGF] AstroHeap]. VoteID: [2]
[13:19 min (1606998577)] VOTE Player [nsancho] voted [PV_Favour] for VoteID[2]
[13:14 min (1606998582)] VOTE Vote [2] completed. Result: PVR_Passed
[13:14 min (1606998582)] VOTE Vote Kick {[TGF] AstroHeap} successfully passed. [For: 2/0 - Against: 0]
[5:18 min (1606999058)] VOTE Player [Cpt.Lati] Started a vote of type (PVR_Kick_Abuse) against [Jesse Pingman]. VoteID: [3]
[5:16 min (1606999060)] VOTE Player [Codyckj] voted [PV_Favour] for VoteID[3]
[5:11 min (1606999065)] VOTE Vote [3] completed. Result: PVR_Passed
[5:11 min (1606999065)] VOTE Vote Kick {Jesse Pingman} successfully passed. [For: 2/0 - Against: 0]
"""

@mock.patch(
    "rcon.extended_commands.ServerCtl._connect",
    side_effect=lambda *args: print("Connecting"),
)
def test_match_log(*mocks):
    res = Rcon.parse_logs(
        """
        [128 sec (1645012281)] MATCH START UTAH BEACH OFFENSIVE
        [6.06 sec (16250121723)] MATCH ENDED `UTAH BEACH OFFENSIVE` ALLIED (1 - 4) AXIS
        """
    )

    assert len(res["logs"]) == 2
    assert res["logs"][0]["action"] == "MATCH ENDED"
    assert res["logs"][0]["timestamp_ms"] == 16250121723000
    assert res["logs"][0]["player"] == None
    assert res["logs"][0]["player2"] == None
    assert res['logs'][0]['sub_content'] == "`UTAH BEACH OFFENSIVE` ALLIED (1 - 4) AXIS"
    assert res["logs"][0]["steam_id_64_1"] == None
    assert res["logs"][0]["steam_id_64_2"] == None

    assert res["logs"][1]["action"] == "MATCH START"
    assert res['logs'][1]['sub_content'] == "UTAH BEACH OFFENSIVE"

@mock.patch(
    "rcon.extended_commands.ServerCtl._connect",
    side_effect=lambda *args: print("Connecting"),
)
def test_teamswitch_log(*mocks):
    res = Rcon.parse_logs(
        """
        [8.23 sec (1645012372)] TEAMSWITCH T17 Scott (Axis > None)
        [6.14 sec (1645012374)] TEAMSWITCH T17 Scott (None > Allies)
        """
    )

    assert len(res["logs"]) == 2
    assert res["logs"][0]["action"] == "TEAMSWITCH"
    assert res["logs"][0]["timestamp_ms"] == 1645012374000
    assert res["logs"][0]["player"] == "T17 Scott"
    assert res["logs"][0]["player2"] == None
    assert res['logs'][0]['sub_content'] == "None > Allies"
    assert res["logs"][0]["steam_id_64_1"] == None
    assert res["logs"][0]["steam_id_64_2"] == None

    assert res['logs'][1]['sub_content'] == "Axis > None"

@mock.patch(
    "rcon.extended_commands.ServerCtl._connect",
    side_effect=lambda *args: print("Connecting"),
)
def test_teamkill_kick_log(*mocks):
    res = Rcon.parse_logs(
        """
        [1:03 min (1645012776)] KICK: [T17 Scott] has been kicked. [BANNED FOR 2 HOURS FOR TEAM KILLING!]
        [41.9 sec (1645012996)] KICK: [T17 Scott] has been kicked. [KICKED FOR TEAM KILLING!]
        """
    )

    assert len(res["logs"]) == 2
    assert res["logs"][0]["action"] == "TK KICKED"
    assert res["logs"][0]["timestamp_ms"] == 1645012996000
    assert res["logs"][0]["player"] == "T17 Scott"
    assert res["logs"][0]["player2"] == None
    assert res['logs'][0]['sub_content'] == "has been kicked. [KICKED FOR TEAM KILLING!]"
    assert res["logs"][0]["steam_id_64_1"] == None
    assert res["logs"][0]["steam_id_64_2"] == None

    assert res['logs'][1]['sub_content'] == "has been kicked. [BANNED FOR 2 HOURS FOR TEAM KILLING!]"
    assert res["logs"][1]["action"] == "TK BANNED FOR 2 HOURS"



@mock.patch(
    "rcon.extended_commands.ServerCtl._connect",
    side_effect=lambda *args: print("Connecting"),
)
def test_admin_cam_log(*mocks):
    res = Rcon.parse_logs(
        """[15:49 min (1606998428)] Player [bananacocoo (76561198003251789)] Entered Admin Camera"""
    )

    assert res["logs"][0]["action"] == "CAMERA"
    assert res["logs"][0]["timestamp_ms"] == 1606998428000
    assert res["logs"][0]["player"] == "bananacocoo"
    assert res["logs"][0]["player2"] == None
    # assert res['logs'][0]['sub_content'] == 'thx'
    assert res["logs"][0]["steam_id_64_1"] == "76561198003251789"
    assert res["logs"][0]["steam_id_64_2"] == None




@mock.patch("rcon.extended_commands.ServerCtl._connect",
    side_effect=lambda *args: print("Connecting"))
def test_line(*mocks):
    res = Rcon.parse_logs(
        '[54.7 sec (1607457183)] KILL: BlAkStE(Allies/76561198202095713) -> Spaghetti with too m(Axis/76561198372886209) with Thompson'
    )
    print(res["logs"])
    assert len(res["logs"]) == 1
    assert res["logs"][0]["player2"] == "Spaghetti with too m"

@mock.patch(
    "rcon.extended_commands.ServerCtl._connect",
    side_effect=lambda *args: print("Connecting"),
)
def test_chat(*mocks):
    res = Rcon.parse_logs(
        "[16:56 min (1606998360)] CHAT[Team][Zuiho(Allies/76561198088159692)]: thx"
    )

    assert res["logs"][0]["player"] == "Zuiho"
    assert res["logs"][0]["sub_content"] == "thx"
    assert res["logs"][0]["steam_id_64_1"] == "76561198088159692"
    assert res["logs"][0]["action"] == "CHAT[Allies][Team]"
    assert res["logs"][0]["timestamp_ms"] == 1606998360000


@mock.patch(
    "rcon.extended_commands.ServerCtl._connect",
    side_effect=lambda *args: print("Connecting"),
)
def test_vote_started(*mocks):
    res = Rcon.parse_logs(
        "[15:49 min (1606998428)] VOTE Player [[fr]ELsass_blitz] Started a vote of type (PVR_Kick_Abuse) against [拢儿]. VoteID: [1]"
    )

    assert res["logs"][0]["player"] == "[fr]ELsass_blitz"
    assert res["logs"][0]["player2"] == "拢儿"
    # assert res['logs'][0]['sub_content'] == 'thx'
    assert res["logs"][0]["steam_id_64_1"] == None
    assert res["logs"][0]["steam_id_64_2"] == None
    assert res["logs"][0]["action"] == "VOTE STARTED"
    assert res["logs"][0]["timestamp_ms"] == 1606998428000


@mock.patch(
    "rcon.extended_commands.ServerCtl._connect",
    side_effect=lambda *args: print("Connecting"),
)
def test_vote_completed(*mocks):
    res = Rcon.parse_logs(
        "[5:11 min (1606999065)] VOTE Vote [3] completed. Result: PVR_Passed"
    )

    assert res["logs"][0]["player"] == None
    assert res["logs"][0]["player2"] == None
    # assert res['logs'][0]['sub_content'] == 'thx'
    assert res["logs"][0]["steam_id_64_1"] == None
    assert res["logs"][0]["steam_id_64_2"] == None
    assert res["logs"][0]["action"] == "VOTE COMPLETED"

    res = Rcon.parse_logs(
        "[5:11 min (1606999065)] VOTE Vote Kick {Jesse Pingman} successfully passed. [For: 2/0 - Against: 0]"
    )

    assert res["logs"][0]["player"] == "Jesse Pingman"
    assert res["logs"][0]["player2"] == None
    # assert res['logs'][0]['sub_content'] == 'thx'
    assert res["logs"][0]["steam_id_64_1"] == None
    assert res["logs"][0]["steam_id_64_2"] == None
    assert res["logs"][0]["action"] == "VOTE COMPLETED"


@mock.patch(
    "rcon.extended_commands.ServerCtl._connect",
    side_effect=lambda *args: print("Connecting"),
)
def test_vote(*mocks):
    res = Rcon.parse_logs(
        "[13:19 min (1606998577)] VOTE Player [nsancho] voted [PV_Favour] for VoteID[2]"
    )

    assert res["logs"][0]["player"] == "nsancho"
    assert res["logs"][0]["player2"] == None
    # assert res['logs'][0]['sub_content'] == 'thx'
    assert res["logs"][0]["steam_id_64_1"] == None
    assert res["logs"][0]["steam_id_64_2"] == None
    assert res["logs"][0]["action"] == "VOTE"
    res = Rcon.parse_logs("[2:34:52 hours (1607023963)] VOTE Player [DarKskiN] voted [PV_Against] for VoteID[2]")
    assert res["logs"][0]["player"] == "DarKskiN"
    assert res["logs"][0]["player2"] == None
    # assert res['logs'][0]['sub_content'] == 'thx'
    assert res["logs"][0]["steam_id_64_1"] == None
    assert res["logs"][0]["steam_id_64_2"] == None
    assert res["logs"][0]["action"] == "VOTE"

@mock.patch(
    "rcon.extended_commands.ServerCtl._connect",
    side_effect=lambda *args: print("Connecting"),
)
def test_log_parsing(*mocks):
    with mock.patch(
        "rcon.extended_commands.ServerCtl.get_logs",
        return_value=RAW_LOGS + "\n" + RAW_VOTE,
    ):
        res = Rcon({}).get_structured_logs(30)

        assert set(res["actions"]) == set(
            [
                "DISCONNECTED",
                "CHAT[Allies]",
                "CHAT[Axis]",
                "CHAT[Allies][Unit]",
                "KILL",
                "CONNECTED",
                "CHAT[Allies][Team]",
                "CHAT[Axis][Team]",
                "CHAT[Axis][Unit]",
                "CHAT",
                "VOTE COMPLETED",
                "VOTE STARTED",
                "VOTE",
                "TEAMSWITCH",
                "TK KICKED",
                "TK BANNED FOR 2 HOURS",
                "TK",
                "MATCH START",
                "MATCH ENDED",
                "MATCH"
            ]
        )
        assert set(res["players"]) == set(
            [
                None,
                "[CPC] xALF",
                "湊あくあ",
                "Karadoc",
                "Dieter Schlüter: b",
                "Karadoc",
                "Waxxeer",
                "Bullitt-FR",
                "fguitou",
                "bananacocoo",
                "bananacocoo : toto",
                "[bananacocoo",
                "Codyckj",
                "nsancho",
                "拢儿",
                "]bananacocoo",
                "[ARC] MaTej ★ツ",
                "Cpt.Lati",
                "[fr]ELsass_blitz",
                "Galiat",
                "[TGF] AstroHeap",
                "Jesse Pingman",
                "T17 Scott",
                '(WTH) Abusify'
            ]
        )
        assert set(l["timestamp_ms"] for l in res["logs"]) == {
            1606999060000,
            1606340677000,
            1606340690000,
            1606998428000,
            1606998577000,
            1606998429000,
            1606999065000,
            1606998582000,
            1606999058000,
            1606998434000,
            1606998575000,
            1645012372000,
            1645012374000,
            1645012996000,
            1645012776000,
            1645012281000,
            16250121723000,
            1646137918000,
            1646137918000,
        }

        res = Rcon({}).get_structured_logs(30, filter_action="CHAT")
        assert all("CHAT" in l["action"] for l in res["logs"])
