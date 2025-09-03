from datetime import datetime
import pytest
from fakeredis import FakeStrictRedis
from unittest.mock import MagicMock, patch
from rcon import maps
from rcon.user_config.vote_map import DefaultMethods
from rcon.vote_map import InvalidVoteError, PlayerChoiceNotAllowed, PlayerVoteNotAllowed, VoteMap, VoteMapException, VoteMapUserConfig
from rcon.maps import LAYERS, MAPS, Environment, Layer, GameMode, Team
from rcon.types import PlayerProfileType

ALL_MAPS = list(LAYERS.values())

CAR_WARFARE_DAY = Layer(
    id="carentan_warfare",
    map=MAPS["carentan"],
    game_mode=GameMode.WARFARE,
)
CAR_WARFARE_NIGHT = Layer(
    id="carentan_warfare_night",
    map=MAPS["carentan"],
    game_mode=GameMode.WARFARE,
    environment=Environment.NIGHT,
)
CAR_OFF_ALLIES = Layer(
    id="carentan_offensive_us",
    map=MAPS["carentan"],
    game_mode=GameMode.OFFENSIVE,
    attackers=Team.ALLIES,
)
CAR_OFF_AXIS = Layer(
    id="carentan_offensive_ger",
    map=MAPS["carentan"],
    game_mode=GameMode.OFFENSIVE,
    attackers=Team.AXIS,
)
CAR_SKIRMISH_DAY = Layer(
    id="CAR_S_1944_Day_P_Skirmish",
    map=MAPS["carentan"],
    game_mode=GameMode.CONTROL,
    environment=Environment.DAY,
)
CAR_SKIRMISH_RAIN = Layer(
    id="CAR_S_1944_Rain_P_Skirmish",
    map=MAPS["carentan"],
    game_mode=GameMode.CONTROL,
    environment=Environment.RAIN,
)
CAR_SKIRMISH_DUSK = Layer(
    id="CAR_S_1944_Dusk_P_Skirmish",
    map=MAPS["carentan"],
    game_mode=GameMode.CONTROL,
    environment=Environment.DUSK,
)
HUR_WARFARE_DAY = Layer(
    id="hurtgenforest_warfare_V2",
    map=MAPS["hurtgenforest"],
    game_mode=GameMode.WARFARE,
)
UTAH_WARFARE_DAY = Layer(
    id="utahbeach_warfare",
    map=MAPS["utahbeach"],
    game_mode=GameMode.WARFARE,
)
INVALID_MAP = Layer(
    id="invalid",
    map=MAPS["utahbeach"],
    game_mode=GameMode.WARFARE,
)

# Sample map data for mocking
SAMPLE_MAPS = [
    CAR_WARFARE_DAY,
    CAR_WARFARE_NIGHT,
    CAR_OFF_ALLIES,
    CAR_OFF_AXIS,
    CAR_SKIRMISH_DAY,
    CAR_SKIRMISH_DUSK,
    CAR_SKIRMISH_RAIN,
    HUR_WARFARE_DAY,
]


@pytest.fixture
def redis_client():
    """Fixture for a fake Redis client."""
    return FakeStrictRedis()


@pytest.fixture
def mock_rcon():
    """Fixture for mocking Rcon interactions."""
    rcon = MagicMock()
    rcon.get_maps.return_value = ALL_MAPS
    rcon.get_playerids.return_value = [
        ("Player1", "71234567890"),
        ("Player2", "0j8dkd3fj948h9fhv3m9thvm578"),
    ]
    rcon.get_vip_ids.return_value = [{ "player_id": "ID_WITH_VIP" }]
    # Initialize dynamic rotation state
    rotation = SAMPLE_MAPS[:1]  # Start with one map
    rcon.get_map_rotation.side_effect = lambda: rotation
    rcon.current_map = SAMPLE_MAPS[0]

    # Mock remove_map_from_rotation
    def remove_map_from_rotation(map_id):
        nonlocal rotation
        map = maps.parse_layer(map_id)
        rotation = [m for m in rotation if m != map]
        return rotation
    
    rcon.remove_map_from_rotation.side_effect = remove_map_from_rotation

    # Mock add_map_to_rotation
    def add_map_to_rotation(map_id):
        nonlocal rotation
        map = maps.parse_layer(map_id)
        if map not in rotation:
            rotation.append(map)
        return rotation

    rcon.add_map_to_rotation.side_effect = add_map_to_rotation
    return rcon


@pytest.fixture
def default_config_loader():
    """Fixture for a default VoteMapUserConfig."""
    return lambda: VoteMapUserConfig(
        enabled=True,
        default_method="least_played_from_suggestions",
    )


@pytest.fixture
def config_loader_with_vote_flags():
    """Fixture for a default VoteMapUserConfig."""
    return lambda: VoteMapUserConfig(
        enabled=True,
        vote_flags=[
            {"flag": "🔨", "vote_count": 1},
            {"flag": "⭐", "vote_count": 2},
            {"flag": "❤️", "vote_count": 4},
        ],
        player_choice_flags=["✅"],
        vote_ban_flags=["😭"],
        vip_vote_count=69,
    )


@pytest.fixture
def disabled_config_loader():
    """Fixture for a disabled VoteMapUserConfig."""
    return lambda: VoteMapUserConfig(
        enabled=False,
        default_method="least_played_from_suggestions",
    )


@pytest.fixture
def mock_maps_history():
    """
    Fixture for mocking MapsHistory.\n
    HUR - 3x\n
    CAR_NIGHT - 0x\n
    OTHER - 1x
    """
    now = int(datetime.now().timestamp())
    minus_hour = lambda n=1: now - (60 * 60 * n)

    history = [
        {
            "name": HUR_WARFARE_DAY.id,
            "start": minus_hour(1),
            "end": None,
        },
        {
            "name": CAR_WARFARE_DAY.id,
            "start": minus_hour(2),
            "end": minus_hour(1),
        },
        {
            "name": CAR_SKIRMISH_DAY.id,
            "start": minus_hour(3),
            "end": minus_hour(2),
        },
        {
            "name": HUR_WARFARE_DAY.id,
            "start": minus_hour(4),
            "end": minus_hour(3),
        },
        {
            "name": CAR_OFF_ALLIES.id,
            "start": minus_hour(5),
            "end": minus_hour(4),
        },
        {
            "name": HUR_WARFARE_DAY.id,
            "start": minus_hour(6),
            "end": minus_hour(5),
        },
        {
            "name": CAR_OFF_AXIS.id,
            "start": minus_hour(7),
            "end": minus_hour(6),
        },
        {
            "name": CAR_SKIRMISH_DUSK.id,
            "start": minus_hour(8),
            "end": minus_hour(7),
        },
        {
            "name": CAR_SKIRMISH_RAIN.id,
            "start": minus_hour(9),
            "end": minus_hour(8),
        },
    ]
    return history


@pytest.fixture
def votemap(redis_client, mock_rcon, default_config_loader, mock_maps_history):
    """Fixture for a VoteMap instance with injected dependencies."""
    with (
        patch("rcon.vote_map.get_redis_client", return_value=redis_client),
        patch(
            "rcon.user_config.vote_map.VoteMapUserConfig.load_from_db",
            return_value=default_config_loader,
        ),
    ):
        return VoteMap(
            rcon=mock_rcon,
            config_loader=default_config_loader,
            maps_history=mock_maps_history,
        )


@pytest.fixture
def votemap_disabled(
    redis_client, mock_rcon, disabled_config_loader, mock_maps_history
):
    """Fixture for VoteMap with disabled voting."""
    with patch("rcon.vote_map.get_redis_client", return_value=redis_client):
        return VoteMap(
            rcon=mock_rcon,
            config_loader=disabled_config_loader,
            maps_history=mock_maps_history,
        )

@pytest.fixture
def votemap_flags(
    redis_client, mock_rcon, config_loader_with_vote_flags, mock_maps_history
):
    """Fixture for VoteMap with disabled voting."""
    with patch("rcon.vote_map.get_redis_client", return_value=redis_client):
        return VoteMap(
            rcon=mock_rcon,
            config_loader=config_loader_with_vote_flags,
            maps_history=mock_maps_history,
        )


# Helper to mock player profile
def mock_player_profile(
    player_id: str, player_name: str, flags: list[str] | None = [], vips=[]
) -> PlayerProfileType:
    return {
        "player_id": player_id,
        "names": [{"name": player_name}],
        "flags": [{ "flag": flag } for flag in flags],
        "vips": vips,
    }


### Unit Tests


def test_initialization_default_state(votemap, mock_rcon):
    """Test that VoteMap initializes with a default whitelist."""
    assert set(votemap.get_map_whitelist()) == set(mock_rcon.get_maps())
    assert votemap.get_selection() == []  # Initially empty


def test_set_map_whitelist(votemap):
    """Test setting list of maps as whitelist"""
    votemap.set_map_whitelist(SAMPLE_MAPS)
    assert set(SAMPLE_MAPS) == set(votemap.get_map_whitelist())


def test_add_map_to_whitelist(votemap):
    """Test adding a map to the whitelist."""
    votemap.set_map_whitelist(SAMPLE_MAPS)
    votemap.add_map_to_whitelist(UTAH_WARFARE_DAY)
    assert UTAH_WARFARE_DAY in votemap.get_map_whitelist()


def test_add_duplicate_map_to_whitelist(votemap):
    """Test adding a duplicate map to the whitelist does nothing"""
    map = list(votemap.get_map_whitelist())[0]
    original_length = len(votemap.get_map_whitelist())
    votemap.add_map_to_whitelist(map)  # Add duplicate
    assert map in votemap.get_map_whitelist()
    assert len(votemap.get_map_whitelist()) == original_length  # No duplicates added


def test_add_invalid_map_to_whitelist(votemap):
    """Test adding map with invalid id to the whitelist raises error"""
    with pytest.raises(Exception):
        votemap.add_map_to_whitelist(INVALID_MAP)


def test_set_invalid_maps_to_whitelist(votemap):
    """Test adding maps with invalid id to the whitelist raises error"""
    with pytest.raises(Exception):
        whitelist = votemap.get_map_whitelist()
        whitelist.add(INVALID_MAP)
        votemap.add_maps_to_whitelist(whitelist)


def test_remove_map_from_whitelist(votemap):
    """Test removing map from whitelist"""
    whitelist = votemap.get_map_whitelist()
    map = whitelist.pop()
    votemap.remove_map_from_whitelist(map)
    assert set(votemap.get_map_whitelist()) == set(whitelist)


def test_select_least_played_map(votemap):
    least_played_map = votemap._get_least_played_map(
        maps_to_pick_from=SAMPLE_MAPS
    )
    assert least_played_map == CAR_WARFARE_NIGHT


def test_select_least_played_map_with_empty_selection(votemap):
    with pytest.raises(ValueError):
        votemap._get_least_played_map(maps_to_pick_from=[])


def test_get_default_next_map_as_least_played_from_selection(votemap):
    votemap.set_selection(
        [CAR_WARFARE_DAY, HUR_WARFARE_DAY, UTAH_WARFARE_DAY]
    )
    least_played_map = votemap._get_default_next_map()
    assert least_played_map == UTAH_WARFARE_DAY


def test_get_default_next_map_as_least_played_from_all(
    mock_rcon, redis_client, mock_maps_history
):
    with patch("rcon.vote_map.get_redis_client", return_value=redis_client):
        votemap = VoteMap(
            rcon=mock_rcon,
            maps_history=mock_maps_history,
            config_loader=lambda: VoteMapUserConfig(
                enabled=True,
                default_method=DefaultMethods.least_played_all_maps
            ),
        )
    selection = [HUR_WARFARE_DAY, CAR_OFF_AXIS, CAR_SKIRMISH_DAY]
    votemap.set_selection(selection)
    least_played_map = votemap._get_default_next_map()
    assert least_played_map not in selection


def test_register_vote(votemap):
    player = mock_player_profile("123456", "player_1")
    votemap.set_selection(
        [HUR_WARFARE_DAY, CAR_OFF_AXIS, CAR_SKIRMISH_DAY]
    )
    selected_map = HUR_WARFARE_DAY
    entry = (
        votemap.get_selection().index(selected_map) + 1
    )  # selection starts from 1
    votemap.register_vote(player, int(datetime.now().timestamp()), entry)
    votes = votemap.get_votes()
    assert len(votes) == 1
    vote = votemap.get_vote(player["player_id"])
    assert vote is not None
    assert vote["player_id"] == player["player_id"]
    assert vote["player_name"] == player["names"][0]["name"]
    assert vote["vote_count"] == 1
    assert vote["map_id"] == selected_map.id


def test_register_vote_invalid_entry(votemap):
    player = mock_player_profile("123456", "player_1")
    selection = [HUR_WARFARE_DAY, CAR_OFF_AXIS, CAR_SKIRMISH_DAY]
    votemap.set_selection(selection)
    entry = 0  # without player choice the selection starts from 1
    with pytest.raises(InvalidVoteError):
        votemap.register_vote(player, int(datetime.now().timestamp()), entry)
    entry = len(selection) + 1  # the entry range should be between 1 and len(selection)
    with pytest.raises(InvalidVoteError):
        votemap.register_vote(player, int(datetime.now().timestamp()), entry)

def test_register_vote_match_highest_value_without_vip(votemap_flags):
    player = mock_player_profile("123456", "player_1", flags=["🔨", "❤️"])
    selection = [HUR_WARFARE_DAY, CAR_OFF_AXIS, CAR_SKIRMISH_DAY]
    votemap_flags.set_selection(selection)
    selected_map = HUR_WARFARE_DAY
    entry = (
        votemap_flags.get_selection().index(selected_map) + 1
    )
    votemap_flags.register_vote(player, int(datetime.now().timestamp()), entry)
    vote = votemap_flags.get_vote(player["player_id"])
    assert vote["vote_count"] == 4

def test_register_vote_match_highest_value_with_vip(votemap_flags):
    player = mock_player_profile("ID_WITH_VIP", "VIP_PLAYER", flags=["🔨", "❤️"])
    selection = [HUR_WARFARE_DAY, CAR_OFF_AXIS, CAR_SKIRMISH_DAY]
    votemap_flags.set_selection(selection)
    selected_map = HUR_WARFARE_DAY
    entry = (
        votemap_flags.get_selection().index(selected_map) + 1
    )
    votemap_flags.register_vote(player, int(datetime.now().timestamp()), entry)
    vote = votemap_flags.get_vote(player["player_id"])
    assert vote["vote_count"] == 69

def test_player_banned_from_voting_based_on_vote_ban_flag(votemap_flags):
    player = mock_player_profile("123456", "player_1", flags=["😭"])
    selection = [HUR_WARFARE_DAY, CAR_OFF_AXIS, CAR_SKIRMISH_DAY]
    votemap_flags.set_selection(selection)
    selected_map = HUR_WARFARE_DAY
    entry = (
        votemap_flags.get_selection().index(selected_map) + 1
    )
    with pytest.raises(PlayerVoteNotAllowed):
        votemap_flags.register_vote(player, int(datetime.now().timestamp()), entry)


def test_player_not_allowed_register_player_choice(votemap_flags):
    player = mock_player_profile("123456", "player_1")
    selection = [HUR_WARFARE_DAY, CAR_OFF_AXIS, CAR_SKIRMISH_DAY]
    votemap_flags.set_selection(selection)
    selected_map = UTAH_WARFARE_DAY
    with pytest.raises(PlayerChoiceNotAllowed):
        votemap_flags.register_player_choice(selected_map, player)

def test_player_can_register_player_choice_when_only_flagged_allowed(votemap_flags):
    player = mock_player_profile("123456", "player_1", flags=["✅"])
    selection = [HUR_WARFARE_DAY, CAR_OFF_AXIS, CAR_SKIRMISH_DAY]
    votemap_flags.set_selection(selection)
    selected_map = UTAH_WARFARE_DAY
    votemap_flags.register_player_choice(selected_map, player)
    selection = votemap_flags.get_selection()
    assert len(selection) == 4
    assert selection[0] == selected_map

def test_player_can_register_player_choice_when_everyone_allowed(votemap):
    player = mock_player_profile("123456", "player_1")
    selection = [HUR_WARFARE_DAY, CAR_OFF_AXIS, CAR_SKIRMISH_DAY]
    votemap.set_selection(selection)
    selected_map = UTAH_WARFARE_DAY
    votemap.register_player_choice(selected_map, player)
    selection = votemap.get_selection()
    assert len(selection) == 4
    assert selection[0] == selected_map
    
def test_player_fails_to_register_player_choice_again(votemap):
    player = mock_player_profile("123456", "player_1")
    selection = [HUR_WARFARE_DAY, CAR_OFF_AXIS, CAR_SKIRMISH_DAY]
    votemap.set_selection(selection)
    map_1 = UTAH_WARFARE_DAY
    map_2 = CAR_SKIRMISH_RAIN
    votemap.register_player_choice(map_1, player)
    with pytest.raises(VoteMapException):
        votemap.register_player_choice(map_2, player)

def test_player_fails_to_register_player_choice_duplicate_map(votemap):
    player = mock_player_profile("123456", "player_1")
    selection = [HUR_WARFARE_DAY, CAR_OFF_AXIS, CAR_SKIRMISH_DAY]
    votemap.set_selection(selection)
    map_1 = CAR_OFF_AXIS
    with pytest.raises(VoteMapException):
        votemap.register_player_choice(map_1, player)

def test_ensure_next_map_with_empty_selection(votemap):
    votemap.set_selection([])
    votemap.apply_results()
    next_map = votemap.get_next_map()
    assert next_map in ALL_MAPS

def test_ensure_selection_when_no_maps_to_select_from(votemap):
    """Excludes last 3 played, HUR is the last played"""
    votemap.set_map_whitelist([HUR_WARFARE_DAY])
    new_selection = votemap.get_new_selection()
    assert len(new_selection) > 0
    assert HUR_WARFARE_DAY not in new_selection

def test_no_cmd_handling_while_disabled(votemap_disabled):
    result = votemap_disabled.handle_vote_command({})
    assert result.ok == False

def test_no_reminder_sent_while_disabled(votemap_disabled):
    t1 = votemap_disabled.get_last_reminder_time()
    result = votemap_disabled.send_reminder()
    t2 = votemap_disabled.get_last_reminder_time()
    assert result.ok == False
    assert t1 == t2

def test_reminder_sent_while_enabled(votemap):
    t1 = votemap.get_last_reminder_time()
    result = votemap.send_reminder()
    t2 = votemap.get_last_reminder_time()
    assert result.ok is True
    assert t1 != t2