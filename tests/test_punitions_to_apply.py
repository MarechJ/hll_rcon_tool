from rcon.automods.models import PunishDetails, PunishPlayer, PunitionsToApply

first_player: PunishPlayer = PunishPlayer(
    player_id="A_STEAM_ID",
    details=PunishDetails(author="", message="first warning"),
    name="",
    squad="",
    team="",
)
same_player: PunishPlayer = PunishPlayer(
    player_id="A_STEAM_ID",
    details=PunishDetails(author="", message="second warning"),
    name="",
    squad="",
    team="",
)
second_player: PunishPlayer = PunishPlayer(
    player_id="ANOTHER_STEAM_ID", name="", squad="", team=""
)


def test_merge_warnings():
    s: PunitionsToApply = PunitionsToApply()
    s.warning.append(first_player)
    o: PunitionsToApply = PunitionsToApply()
    o.warning.append(same_player)
    o.warning.append(second_player)

    s.merge(o)

    assert len(s.warning) == 3
    assert s.warning[0].details.message == "first warning"
    assert s.warning[1].details.message == "second warning"
    assert s.warning[0].player_id == s.warning[1].player_id


def test_merge_punishes():
    s: PunitionsToApply = PunitionsToApply()
    s.punish.append(first_player)
    o: PunitionsToApply = PunitionsToApply()
    o.punish.append(same_player)
    o.punish.append(second_player)

    s.merge(o)

    assert len(s.punish) == 2
    assert s.punish[0].details.message == "first warning"
    assert s.punish[1].player_id == second_player.player_id


def test_merge_kicks():
    s: PunitionsToApply = PunitionsToApply()
    s.kick.append(first_player)
    o: PunitionsToApply = PunitionsToApply()
    o.kick.append(same_player)
    o.kick.append(second_player)

    s.merge(o)

    assert len(s.kick) == 2
    assert s.kick[0].details.message == "first warning"
    assert s.kick[1].player_id == second_player.player_id
