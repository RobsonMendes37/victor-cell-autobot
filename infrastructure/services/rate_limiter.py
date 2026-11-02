"""
Asynchronous Sliding-Window Rate Limiter.
Protects webhooks, simulator endpoints, and external AI quotas from DoS, brute force, and runaway client loops.
"""

import time
from collections import defaultdict
from typing import Any, Dict, List, Tuple


class SlidingWindowRateLimiter:
    """
    In-memory Sliding Window Rate Limiter.
    Tracks timestamps of requests per key within a sliding time window.
    """

    def __init__(self, max_requests: int = 20, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._history: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, key: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Evaluates whether a request from 'key' is permitted.
        Returns:
          (is_allowed: bool, info: dict with 'remaining', 'reset_seconds', 'limit')
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Remove requisições fora da janela deslizante
        timestamps = [ts for ts in self._history[key] if ts > window_start]
        self._history[key] = timestamps

        current_count = len(timestamps)
        if current_count >= self.max_requests:
            oldest_ts = timestamps[0]
            retry_after = round(self.window_seconds - (now - oldest_ts), 2)
            return False, {
                "allowed": False,
                "limit": self.max_requests,
                "remaining": 0,
                "retry_after": max(1.0, retry_after),
            }

        # Registra a requisição atual
        self._history[key].append(now)
        remaining = self.max_requests - (current_count + 1)
        return True, {
            "allowed": True,
            "limit": self.max_requests,
            "remaining": remaining,
            "retry_after": 0.0,
        }

    def reset_key(self, key: str) -> None:
        """Clears request history for a specific key."""
        if key in self._history:
            del self._history[key]

    def cleanup(self) -> int:
        """Prunes expired keys to prevent memory leaks in long-running processes."""
        now = time.time()
        window_start = now - self.window_seconds
        keys_to_delete = []

        for key, timestamps in list(self._history.items()):
            valid = [ts for ts in timestamps if ts > window_start]
            if not valid:
                keys_to_delete.append(key)
            else:
                self._history[key] = valid

        for k in keys_to_delete:
            del self._history[k]

        return len(keys_to_delete)
