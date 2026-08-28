from rcon.commands import ServerCtl
from rcon.rcon import Rcon


def test_add_vip_to_gameserver_calls_raw_rcon_and_invalidates_cache(
    monkeypatch,
):
    calls = []
    cache_clears = []

    def fake_add_vip(self, player_id, description):
        calls.append((player_id, description))
        return True

    monkeypatch.setattr(ServerCtl, "add_vip", fake_add_vip)
    monkeypatch.setattr(
        Rcon.get_vip_ids,
        "cache_clear",
        lambda: cache_clears.append(True),
    )

    rcon = object.__new__(Rcon)

    result = rcon.add_vip_to_gameserver(
        player_id="76561198080212634",
        description="Player",
    )

    assert result is True
    assert calls == [("76561198080212634", "Player")]
    assert len(cache_clears) == 2


def test_remove_vip_from_gameserver_calls_raw_rcon_and_invalidates_cache(
    monkeypatch,
):
    calls = []
    cache_clears = []

    def fake_remove_vip(self, player_id):
        calls.append(player_id)
        return True

    monkeypatch.setattr(ServerCtl, "remove_vip", fake_remove_vip)
    monkeypatch.setattr(
        Rcon.get_vip_ids,
        "cache_clear",
        lambda: cache_clears.append(True),
    )

    rcon = object.__new__(Rcon)

    result = rcon.remove_vip_from_gameserver(
        player_id="76561198080212634",
    )

    assert result is True
    assert calls == ["76561198080212634"]
    assert len(cache_clears) == 2
