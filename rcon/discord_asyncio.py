import asyncio
import logging
import threading
import time

from discord_webhook import AsyncDiscordWebhook, DiscordWebhook

logger = logging.getLogger(__name__)


# class the starts a new asyncio event loop in a new thread
class DiscordAsyncio:
    """
    A class for handling asynchronous Discord operations using asyncio.
    An event loop is created in a new thread when the class is instantiated.
    The singleton pattern is used to ensure that only one instance of the
    class is created.

    Methods:
    - send_webhook: Sends a DiscordWebhook asynchronously.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """
        Create a new instance of the DiscordAsyncio class if it doesn't already exist.

        Returns:
            The instance of the DiscordAsyncio class.
        """
        if cls._instance is None:
            # threading.Lock is expensive, so check if instance is None first
            # since instance is not None should be the most common case
            with cls._lock:
                if cls._instance is None:
                    logger.info(f"Creating new instance of {cls.__name__}")
                    cls._instance = super(DiscordAsyncio, cls).__new__(cls)
                    cls._instance._start_asyncio()
        return cls._instance

    def _start_asyncio(self):
        self.loop = asyncio.new_event_loop()
        t = threading.Thread(target=self.loop.run_forever)
        t.daemon = True
        t.start()
        logger.info(
            f"{threading.current_thread().name}:{threading.current_thread().ident}: started asyncio event loop in new thread: {t.name}:{t.ident}"
        )
        return self.loop

    def _stop_async(self):
        self.loop.call_soon_threadsafe(self.loop.stop)

    def send_webhook(self, webhook: DiscordWebhook):
        """
        Sends a DiscordWebhook asynchronously.

        Args:
        - webhook: The DiscordWebhook object to send.

        Returns:
        - A concurrent.futures.Future object representing the result of the asynchronous operation.
        """
        async_webhook: AsyncDiscordWebhook = self._make_async_webhook(webhook)
        return self.send_async_webhook(async_webhook)

    def send_async_webhook(self, async_webhook: AsyncDiscordWebhook):
        """
        Sends an AsyncDiscordWebhook.

        Args:
            async_webhook (AsyncDiscordWebhook): The asynchronous Discord webhook to send.

        Returns:
            concurrent.futures.Future: A future representing the result of the webhook send operation.
        """
        return asyncio.run_coroutine_threadsafe(
            self._send_webhook(async_webhook), self.loop
        )

    @staticmethod
    async def _send_webhook(webhook: AsyncDiscordWebhook):
        await webhook.execute()

    @staticmethod
    def _make_async_webhook(webhook):
        return AsyncDiscordWebhook(
            url=webhook.url,
            content=webhook.content,
            embeds=webhook.embeds,
            avatar_url=webhook.avatar_url,
            allowed_mentions=webhook.allowed_mentions,
            username=webhook.username,
            rate_limit_retry=True,
        )
