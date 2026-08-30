import pytest

from rcon.models import enter_session
from rcon.vip import (
    clear_default_vip_list,
    get_default_vip_list,
    set_default_vip_list,
)


@pytest.fixture
def isolated_default_vip_lists():
    """Temporarily isolate default-list assignments for servers 1 and 2."""
    server_numbers = (1, 2)

    with enter_session() as sess:
        original_defaults = {
            server_number: (
                default.id
                if (
                    default := get_default_vip_list(
                        sess,
                        server_number,
                    )
                )
                is not None
                else None
            )
            for server_number in server_numbers
        }

    for server_number in server_numbers:
        clear_default_vip_list(server_number)

    try:
        yield
    finally:
        for server_number in server_numbers:
            clear_default_vip_list(server_number)

        for server_number, vip_list_id in original_defaults.items():
            if vip_list_id is not None:
                set_default_vip_list(
                    server_number,
                    vip_list_id,
                )
