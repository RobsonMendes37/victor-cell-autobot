"""
Deep Tests for DebounceBuffer.
Verifies message aggregation, timer resets on bursts, and flush behavior.
"""

import asyncio

import pytest

from application.use_cases.debounce_buffer import DebounceBuffer


@pytest.mark.asyncio
async def test_debounce_aggregates_rapid_burst():
    calls = []

    async def callback(full_text: str, media_bytes, mime_type):
        calls.append(full_text)

    buffer = DebounceBuffer(wait_seconds=0.1)

    # Rapid burst of 3 messages within 50ms
    await buffer.add_message("5585991110001", "Boa tarde", callback)
    await buffer.add_message("5585991110001", "tudo bem?", callback)
    await buffer.add_message("5585991110001", "tem tela do T290?", callback)

    # Wait for debounce window to fire
    await asyncio.sleep(0.2)

    assert len(calls) == 1
    assert "Boa tarde" in calls[0]
    assert "tudo bem?" in calls[0]
    assert "tem tela do T290?" in calls[0]
