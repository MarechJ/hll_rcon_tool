from _pytest.fixtures import fixture

from rcon.automods.get_team_count import get_team_count


@fixture
def team_view():
    global state, redis_store
    state = {}
    redis_store = {}
    return {
        "allies": {
            "combat": 0,
            "commander": {
                "player_id": "76561198206929556",
            },
            "count": 0,
            "deaths": 0,
            "defense": 0,
            "kills": 0,
            "offense": 0,
            "squads": {
                "able": {
                    "combat": 135,
                    "deaths": 10,
                    "defense": 600,
                    "has_leader": False,
                    "kills": 12,
                    "offense": 960,
                    "players": [
                        {
                            "player_id": "76561198206929555",
                        },
                        {
                            "player_id": "76561198206929556",
                        },
                    ],
                    "support": 264,
                    "type": "armor",
                },
            },
            "support": 0,
        },
        "axis": {
            "combat": 0,
            "commander": None,
            "count": 0,
            "deaths": 0,
            "defense": 0,
            "kills": 0,
            "offense": 0,
            "squads": {
                "able": {
                    "combat": 135,
                    "deaths": 10,
                    "defense": 600,
                    "has_leader": False,
                    "kills": 12,
                    "offense": 960,
                    "players": [
                        {
                            "player_id": "76561198206929555",
                        },
                    ],
                    "support": 264,
                    "type": "infantry",
                },
            },
            "support": 7323,
        },
    }


def test_team_count_with_commander(team_view):
    assert get_team_count(team_view, "allies") == 3


def test_team_count_without_commander(team_view):
    assert get_team_count(team_view, "axis") == 1
