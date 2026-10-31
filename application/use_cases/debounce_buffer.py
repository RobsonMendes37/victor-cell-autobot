"""
Debounce Buffer Service for Rapid Sequential Messages.
Combines fragmented WhatsApp messages (e.g., within 3 seconds) into a single turn.
"""

import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict, List

logger = logging.getLogger("DebounceBuffer")


class DebounceBuffer:
    def __init__(self, wait_seconds: float = 3.0):
        self.wait_seconds = wait_seconds
        self._buffers: Dict[str, List[str]] = {}
        self._tasks: Dict[str, asyncio.Task] = {}

    async def enqueue(
        self, customer_phone: str, text: str, callback: Callable[[str, str], Awaitable[Any]]
    ) -> None:
        """
        Enqueues incoming text. If another message arrives before wait_seconds,
        resets the timer and merges text.
        """
        if customer_phone not in self._buffers:
            self._buffers[customer_phone] = []

        if text.strip():
            self._buffers[customer_phone].append(text)

        # Cancela timer anterior se ainda estiver em espera
        if customer_phone in self._tasks and not self._tasks[customer_phone].done():
            self._tasks[customer_phone].cancel()

        # Cria novo timer de disparo
        self._tasks[customer_phone] = asyncio.create_task(
            self._process_after_delay(customer_phone, callback)
        )

    async def add_message(
        self, phone: str, text_chunk: str, dispatch_callback: Callable[[str], Awaitable[Any]]
    ) -> None:
        """Alias for enqueue with direct callback on combined text."""
        async def wrapper(c_phone: str, combined: str):
            await dispatch_callback(combined)

        await self.enqueue(customer_phone=phone, text=text_chunk, callback=wrapper)

    async def _process_after_delay(
        self, customer_phone: str, callback: Callable[[str, str], Awaitable[Any]]
    ):
        try:
            await asyncio.sleep(self.wait_seconds)
            messages = self._buffers.pop(customer_phone, [])
            if messages:
                combined_text = "\n".join(messages).strip()
                logger.info(
                    f"Processando buffer de {len(messages)} mensagens agregadas para {customer_phone}"
                )
                await callback(customer_phone, combined_text)
        except asyncio.CancelledError:
            pass
