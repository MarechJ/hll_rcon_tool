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
