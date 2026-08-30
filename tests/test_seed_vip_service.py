from rcon.seed_vip.service import (
    DRY_RUN_DISCORD_PREFIX,
    format_discord_message,
)


def test_format_discord_message_marks_dry_run():
    message = "Server has reached 10 players"

    result = format_discord_message(message, dry_run=True)

    assert result == f"{DRY_RUN_DISCORD_PREFIX}{message}"
    assert "DRY RUN" in result


def test_format_discord_message_does_not_modify_live_message():
    message = "Server has reached 10 players"

    result = format_discord_message(message, dry_run=False)

    assert result == message


class _RewardConfig:
    def __init__(self, vip_list_id=None, dry_run=False):
        from types import SimpleNamespace

        self.dry_run = dry_run
        self.reward = SimpleNamespace(
            vip_list_id=vip_list_id,
            player_name_format_not_current_vip="{player_name} - CRCON Seed VIP",
        )


class _RewardRcon:
    def __init__(self, applicable_lists, default_list=None):
        self.applicable_lists = applicable_lists
        self.default_list = default_list
        self.upserts = []
        self.legacy_add_calls = []

    def get_vip_lists_for_server(self):
        return self.applicable_lists

    def get_default_vip_list(self):
        return self.default_list

    def upsert_vip_list_record(self, **kwargs):
        self.upserts.append(kwargs)
        return {"id": len(self.upserts), **kwargs}

    def add_vip(self, **kwargs):
        self.legacy_add_calls.append(kwargs)
        raise AssertionError("Legacy add_vip must not be used")


def test_resolve_reward_vip_list_uses_selected_applicable_list():
    from rcon.seed_vip.utils import resolve_reward_vip_list

    default_list = {"id": 1, "name": "Default"}
    selected_list = {"id": 2, "name": "Seeding"}
    rcon = _RewardRcon([default_list, selected_list], default_list)

    result = resolve_reward_vip_list(
        rcon=rcon,
        config=_RewardConfig(vip_list_id=2),
    )

    assert result == selected_list


def test_resolve_reward_vip_list_falls_back_to_default():
    from rcon.seed_vip.utils import resolve_reward_vip_list

    default_list = {"id": 1, "name": "Default"}
    rcon = _RewardRcon([default_list], default_list)

    result = resolve_reward_vip_list(
        rcon=rcon,
        config=_RewardConfig(vip_list_id=999),
    )

    assert result == default_list


def test_resolve_reward_vip_list_returns_none_without_valid_default():
    from rcon.seed_vip.utils import resolve_reward_vip_list

    rcon = _RewardRcon([], None)

    result = resolve_reward_vip_list(
        rcon=rcon,
        config=_RewardConfig(vip_list_id=999),
    )

    assert result is None


def test_reward_players_uses_targeted_api_and_skips_existing_vips():
    from collections import defaultdict
    from datetime import UTC, datetime

    from rcon.seed_vip.models import Player, VipPlayer
    from rcon.seed_vip.utils import reward_players

    existing_id = "00020000000000000000000000000001"
    new_id = "00020000000000000000000000000002"
    expiration = datetime(2035, 1, 1, tzinfo=UTC)
    rcon = _RewardRcon([{"id": 7, "name": "Seeding"}])

    rewarded = reward_players(
        rcon=rcon,
        config=_RewardConfig(),
        vip_list_id=7,
        to_add_vip_steam_ids={existing_id, new_id},
        current_vips={
            existing_id: VipPlayer(
                player=Player(
                    player_id=existing_id,
                    name="Existing VIP",
                    current_playtime_seconds=0,
                ),
                expiration_date=expiration,
            )
        },
        players_lookup={new_id: "New Seeder"},
        expiration_timestamps=defaultdict(lambda: expiration),
    )

    assert rewarded == {new_id}
    assert rcon.legacy_add_calls == []
    assert rcon.upserts == [
        {
            "player_id": new_id,
            "vip_list_id": 7,
            "description": "New Seeder - CRCON Seed VIP",
            "expires_at": expiration,
            "notes": "Granted by Seed VIP Reward",
            "admin_name": "Seed VIP Reward",
        }
    ]


def test_seed_vip_schema_documents_deprecated_reward_fields():
    from rcon.user_config.seed_vip import SeedVIPUserConfig

    schema = SeedVIPUserConfig.model_json_schema()
    reward_properties = schema["$defs"]["Reward"]["properties"]

    assert (
        "Deprecated compatibility field" in reward_properties["forward"]["description"]
    )
    assert "existing effective VIP" in reward_properties["cumulative"]["description"]
    assert "default VIP list" in reward_properties["vip_list_id"]["description"]
