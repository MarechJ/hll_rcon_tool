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
"""


@mock.patch('rcon.extended_commands.ServerCtl._connect', side_effect=lambda *args: print("Connecting"))
def test_log_parsing(*mocks):
    with mock.patch('rcon.extended_commands.ServerCtl.get_logs', return_value=RAW_LOGS):
        res = Rcon({}).get_structured_logs(30)
        assert set(res['actions']) == set(['DISCONNECTED', 'CHAT[Allies]', 'CHAT[Axis]', 'CHAT[Allies][Unit]', 'KILL', 'CONNECTED', 'CHAT[Allies][Team]', 'CHAT[Axis][Team]', 'CHAT[Axis][Unit]', 'CHAT'])
        assert set(res['players']) == set([None, '[CPC] xALF', '湊あくあ', 'Karadoc', 'Dieter Schlüter: b', 'Karadoc', 'Waxxeer', 'Bullitt-FR', 'fguitou', 'bananacocoo', 'bananacocoo : toto', '[bananacocoo', ']bananacocoo'])
        assert set(l['timestamp_ms'] for l in res['logs']) == {1606340677000, 1606340690000}

        res = Rcon({}).get_structured_logs(30, filter_action='CHAT')
        assert all('CHAT' in l['action'] for l in res['logs'])