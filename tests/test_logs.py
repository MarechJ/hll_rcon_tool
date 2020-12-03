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




@mock.patch('rcon.extended_commands.ServerCtl._connect', side_effect=lambda *args: print("Connecting"))
def test_log_parsing(*mocks):
    with mock.patch('rcon.extended_commands.ServerCtl.get_logs', return_value=RAW_LOGS):
        res = Rcon({}).get_structured_logs(30)

        assert set(res['actions']) == set(['DISCONNECTED', 'CHAT[Allies]', 'CHAT[Axis]', 'CHAT[Allies][Unit]', 'KILL', 'CONNECTED', 'CHAT[Allies][Team]', 'CHAT[Axis][Team]', 'CHAT[Axis][Unit]', 'CHAT', "TEAM KILL"])
        assert set(res['players']) == set([None, '[CPC] xALF', '湊あくあ', 'Karadoc', 'Dieter Schlüter: b', 'Karadoc', 'Waxxeer', 'Bullitt-FR', 'fguitou', 'bananacocoo', 'bananacocoo : toto', '[bananacocoo', ']bananacocoo'])
        assert set(l['timestamp_ms'] for l in res['logs']) == {1606340677000, 1606340690000}

        res = Rcon({}).get_structured_logs(30, filter_action='CHAT')
        assert all('CHAT' in l['action'] for l in res['logs'])