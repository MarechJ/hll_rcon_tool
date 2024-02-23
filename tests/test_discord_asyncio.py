import unittest
from rcon.discord_asyncio import DiscordAsyncio


class TestDiscordAsyncio(unittest.TestCase):

    def setUp(self):
        self.discord_asyncio = DiscordAsyncio()

    def test_only_one_instance(self):
        """
        Test that only one instance of DiscordAsyncio is created.
        """
        discord_asyncio = DiscordAsyncio()
        another_discord_asyncio = DiscordAsyncio()
        assert discord_asyncio is another_discord_asyncio


if __name__ == "__main__":
    unittest.main()
