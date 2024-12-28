from datetime import datetime, timedelta
from rcon.models import PlayerID, PlayerSession

def test_get_current_playtime_seconds():
    now = datetime.now()

    # Create mock sessions
    active_session = PlayerSession(start=now - timedelta(minutes=30), end=None)  # No end -> Active
    ended_session = PlayerSession(start=now - timedelta(hours=2), end=now - timedelta(hours=1))  # Has end -> Ended

    # Create a PlayerID object with mock sessions
    player = PlayerID()

    # Test with an active session (no end defined)
    player.sessions = [active_session]
    playtime = player.get_current_playtime_seconds()
    print(f"Playtime for active session: {playtime} seconds")
    assert playtime > 0, "Playtime should be greater than 0 for active sessions"

    # Test with an ended session (end is defined)
    player.sessions = [ended_session]
    playtime = player.get_current_playtime_seconds()
    print(f"Playtime for ended session: {playtime} seconds")
    assert playtime == 0, "Playtime should be 0 for ended sessions"

# Run the test function
test_get_current_playtime_seconds()
