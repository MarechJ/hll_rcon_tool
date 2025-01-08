import os

import pytest

os.environ["HLL_MAINTENANCE_CONTAINER"] = "1"
from rcon.models import PlayerStats
from rcon.types import PlayerTeamAssociation, PlayerTeamConfidence
from rcon.maps import Team


def test_detects_no_kills_no_deaths():
    p = PlayerStats(weapons=dict(), death_by_weapons=dict())

    assert p.detect_team() == PlayerTeamAssociation(side=Team.UNKNOWN, confidence=PlayerTeamConfidence.STRONG, ratio=0)


@pytest.mark.parametrize(
    "weapon, expected", [
        ('M1A1 THOMPSON', Team.ALLIES),
        ('PPSH 41', Team.ALLIES),
        ('Sten Gun Mk.V', Team.ALLIES),
        ('GEWEHR 43', Team.AXIS),
    ]
)
def test_detects_weapons(weapon, expected):
    p = PlayerStats(weapons={weapon: 1}, death_by_weapons=dict())

    assert p.detect_team() == PlayerTeamAssociation(side=expected, confidence=PlayerTeamConfidence.STRONG, ratio=100)


@pytest.mark.parametrize(
    "death, expected", [
        ('M1A1 THOMPSON', Team.AXIS),
        ('PPSH 41', Team.AXIS),
        ('Sten Gun Mk.V', Team.AXIS),
        ('GEWEHR 43', Team.ALLIES),
    ]
)
def test_detects_death_by_weapon(death, expected):
    p = PlayerStats(weapons=dict(), death_by_weapons={death: 1})

    assert p.detect_team() == PlayerTeamAssociation(side=expected, confidence=PlayerTeamConfidence.STRONG, ratio=100)


def test_same_numbers():
    p = PlayerStats(weapons={'M1A1 THOMPSON': 1}, death_by_weapons={'M1A1 THOMPSON': 1})

    assert p.detect_team() == PlayerTeamAssociation(side=Team.UNKNOWN, confidence=PlayerTeamConfidence.MIXED, ratio=50)


def test_multiple_sides():
    p = PlayerStats(weapons={'M1A1 THOMPSON': 4, 'GEWEHR 43': 3, 'STG44': 3}, death_by_weapons={'GEWEHR 43': 1})

    assert p.detect_team() == PlayerTeamAssociation(side=Team.AXIS, confidence=PlayerTeamConfidence.MIXED, ratio=54.55)


def test_prefer_more_kills():
    p = PlayerStats(weapons={'M1A1 THOMPSON': 1, 'GEWEHR 43': 2}, death_by_weapons=dict())

    assert p.detect_team() == PlayerTeamAssociation(side=Team.AXIS, confidence=PlayerTeamConfidence.MIXED, ratio=66.67)


def test_detect_complex():
    p = PlayerStats(weapons={
        '88 KWK 36 L/56 [Sd.Kfz.181 Tiger 1]': 21,
        'COAXIAL MG34 [Sd.Kfz.181 Tiger 1]': 3,
        'COAXIAL MG34': 1,
        '50mm KwK 39/1 [Sd.Kfz.234 Puma]': 1,
    }, death_by_weapons={
        'BAZOOKA': 2,
        'SATCHEL': 1,
        'M1 GARAND': 1,
    })

    assert p.detect_team() == PlayerTeamAssociation(side=Team.AXIS, confidence=PlayerTeamConfidence.STRONG, ratio=100)


def test_detect_complex_inf():
    p = PlayerStats(weapons={
        'M1 GARAND': 31,
        'BAZOOKA': 1,
        'MK2 GRENADE': 1,
        'M1A1 THOMPSON': 1,
        'BROWNING M1919': 2,
    }, death_by_weapons={
        'GEWEHR 43': 9,
        'MG42': 1,
        'MP40': 1,
        'STG44': 1,
        'FG42 x4': 1,
        '150MM HOWITZER [sFH 18]': 1,
        '20MM KWK 30 [Sd.Kfz.121 Luchs]': 1,
    })

    assert p.detect_team() == PlayerTeamAssociation(side=Team.ALLIES, confidence=PlayerTeamConfidence.STRONG, ratio=100)
    assert p.calc_kills_by_type() == {
        'bazooka': 1,
        'grenade': 1,
        'machine_gun': 2,
        'infantry': 32,
    }


def test_detect_ignores_some_other_side():
    p = PlayerStats(weapons={
        'M1 GARAND': 45,
        'M1A1 THOMPSON': 4,
        'MK2 GRENADE': 3,
        'BAZOOKA': 2,
    }, death_by_weapons={
        'GEWEHR 43': 28,
        'MP40': 7,
        'KARABINER 98K': 7,
        'FG42 x4': 6,
        '150MM HOWITZER [sFH 18]': 5,
        'STG44': 3,
        'COAXIAL MG34 [Sd.Kfz.181 Tiger 1]': 2,
        '88 KWK 36 L/56 [Sd.Kfz.181 Tiger 1]': 2,
        'MG42': 1,
        'SATCHEL': 1,
        'BOMBING RUN': 1,
        # this is a teamkill or a wrongly attributed kill or a kill by an explosion of a vehicle or something
        # it should not result in a MIXED team confidence
        'Sherman M4A3(75)W': 1,
    })

    assert p.detect_team() == PlayerTeamAssociation(side=Team.ALLIES, confidence=PlayerTeamConfidence.STRONG, ratio=99.12)
