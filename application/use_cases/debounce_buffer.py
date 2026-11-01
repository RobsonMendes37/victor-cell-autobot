"""
Debounce Buffer Service for Rapid Sequential Messages.
Combines fragmented WhatsApp messages (e.g., within 3 seconds) into a single turn,
preserving media (photos and voice notes) sent during the window.
"""

import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger("DebounceBuffer")


class DebounceBuffer:
    def __init__(self, wait_seconds: float = 3.0):
        self.wait_seconds = wait_seconds
        self._buffers: Dict[str, List[str]] = {}
        self._media: Dict[str, Tuple[bytes, str]] = {}
        self._tasks: Dict[str, asyncio.Task] = {}

    async def enqueue(
        self,
        customer_phone: str,
        text: str,
        callback: Callable[[str, str, Optional[bytes], Optional[str]], Awaitable[Any]],
        media_bytes: Optional[bytes] = None,
        mime_type: Optional[str] = None,
    ) -> None:
        """
        Enqueues incoming text and media. If another message arrives before wait_seconds,
        resets the timer and merges text while preserving media.
        """
        if customer_phone not in self._buffers:
            self._buffers[customer_phone] = []

        if text.strip():
            self._buffers[customer_phone].append(text)

        if media_bytes and mime_type:
            self._media[customer_phone] = (media_bytes, mime_type)

        # Cancela timer anterior se ainda estiver em espera
        if customer_phone in self._tasks and not self._tasks[customer_phone].done():
            self._tasks[customer_phone].cancel()

        # Cria novo timer de disparo
        self._tasks[customer_phone] = asyncio.create_task(
            self._process_after_delay(customer_phone, callback)
        )

    async def add_message(
        self,
        phone: str,
        text_chunk: str,
        dispatch_callback: Callable[[str, Optional[bytes], Optional[str]], Awaitable[Any]],
        media_bytes: Optional[bytes] = None,
        mime_type: Optional[str] = None,
    ) -> None:
        """Alias for enqueue with direct callback on combined text and media."""
        async def wrapper(c_phone: str, combined: str, m_bytes: Optional[bytes], m_type: Optional[str]):
            await dispatch_callback(combined, m_bytes, m_type)

        await self.enqueue(
            customer_phone=phone,
            text=text_chunk,
            callback=wrapper,
            media_bytes=media_bytes,
            mime_type=mime_type,
        )

    async def _process_after_delay(
        self,
        customer_phone: str,
        callback: Callable[[str, str, Optional[bytes], Optional[str]], Awaitable[Any]],
    ):
        try:
            await asyncio.sleep(self.wait_seconds)
            messages = self._buffers.pop(customer_phone, [])
            media = self._media.pop(customer_phone, None)
            media_bytes = media[0] if media else None
            mime_type = media[1] if media else None

            combined_text = "\n".join(messages).strip()
            logger.info(
                f"Processando buffer de {len(messages)} mensagens agregadas para {customer_phone} (tem_midia: {media_bytes is not None})"
            )
            await callback(customer_phone, combined_text, media_bytes, mime_type)
        except asyncio.CancelledError:
            pass
