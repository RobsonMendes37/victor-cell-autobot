"""
Test Suite for NTFY One-Click WhatsApp Actions.
Validates that push notifications include direct WhatsApp click URLs and interactive action buttons.
"""

from unittest.mock import AsyncMock, patch

import pytest

from infrastructure.notifiers.base import NotificationPayload, NotificationPriority
from infrastructure.notifiers.ntfy_channel import NtfyNotificationChannel


@pytest.mark.asyncio
async def test_ntfy_dispatch_includes_whatsapp_click_and_action():
    channel = NtfyNotificationChannel(
        server_url="https://ntfy.sh",
        topic="test_topic",
        enabled=True,
    )

    payload = NotificationPayload(
        title="🚨 NOVO DESPACHO UBER",
        message="Separar tela Tab A8",
        customer_phone="5585999998888",
        priority=NotificationPriority.URGENT,
        tags=["warning", "package"],
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        success = await channel.dispatch(payload)

        assert success is True
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        headers = kwargs.get("headers", {})

        assert headers["Title"] == "🚨 NOVO DESPACHO UBER"
        assert headers["Priority"] == "5"
        assert headers["Tags"] == "warning,package"
        # Validação do One-Click WhatsApp
        assert headers["Click"] == "https://wa.me/5585999998888"
        assert "view, Abrir WhatsApp, https://wa.me/5585999998888" in headers["Actions"]
