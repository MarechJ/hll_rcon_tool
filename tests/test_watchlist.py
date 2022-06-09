from rcon.watchlist import PlayerWatch, watchdog


def test_watchlist_hook():
    log = {
        "version": 1,
        "timestamp_ms": 1610288198000,
        "relative_time_ms": -9104289.268000001,
        "raw": "[2:31:44 hours (1610288198)] DISCONNECTED Boulard",
        "line_without_time": "DISCONNECTED Boulard",
        "action": "DISCONNECTED",
        "player": "Boulard",
        "steam_id_64_1": None,
        "player2": None,
        "steam_id_64_2": None,
        "weapon": None,
        "message": "Boulard",
        "sub_content": None,
    }
    steam_id = '7777777777777777'
    class Fake:
        def get_player_info(self, player_name):
            return steam_id
    PlayerWatch(steam_id).watch("Test player", "No further comments")
    watchdog(Fake(), log)