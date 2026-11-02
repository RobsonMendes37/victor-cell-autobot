"""
Circuit Breaker Pattern implementation for resilient external API integration.
Protects the system against cascading failures when Google Gemini or external services experience downtime or quota limits.
"""

import logging
import time
from enum import Enum
from typing import Any, Dict

logger = logging.getLogger("CircuitBreaker")


class CircuitState(str, Enum):
    CLOSED = "CLOSED"  # Normal operation: requests pass through
    OPEN = "OPEN"  # Failing: fast fallback without calling remote API
    HALF_OPEN = "HALF_OPEN"  # Testing recovery: allows probe requests


class CircuitBreakerOpenException(Exception):
    """Raised when an operation is attempted while the circuit breaker is OPEN."""

    pass


class CircuitBreaker:
    """
    Resilient Circuit Breaker state machine.
    Tracks failures within a sliding evaluation window.
    Transitions:
      CLOSED -> (failures >= threshold) -> OPEN
      OPEN -> (elapsed >= recovery_timeout) -> HALF_OPEN
      HALF_OPEN -> (success) -> CLOSED
      HALF_OPEN -> (failure) -> OPEN
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout_seconds: float = 60.0,
        name: str = "GeminiAI",
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.name = name
        self.state: CircuitState = CircuitState.CLOSED
        self.failure_count: int = 0
        self.success_count: int = 0
        self.last_failure_time: float = 0.0
        self.last_state_change: float = time.time()
        self.total_trips: int = 0

    def can_execute(self) -> bool:
        """Determines whether a remote call is allowed to proceed."""
        now = time.time()
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if now - self.last_failure_time >= self.recovery_timeout_seconds:
                logger.info(
                    f"[{self.name}] Janela de recuperação atingida ({self.recovery_timeout_seconds}s). "
                    f"Transitando para HALF_OPEN para testar conectividade."
                )
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
                return True
            return False

        if self.state == CircuitState.HALF_OPEN:
            # Em HALF_OPEN, permite sondagem controlada
            return True

        return False

    def record_success(self) -> None:
        """Notifies the breaker of a successful remote operation."""
        self.success_count += 1
        if self.state == CircuitState.HALF_OPEN:
            logger.info(
                f"[{self.name}] Chamada bem-sucedida em HALF_OPEN! Circuito RESTAURADO para CLOSED."
            )
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.last_state_change = time.time()
        elif self.state == CircuitState.CLOSED:
            # Em operação normal, zera falhas esporádicas anteriores
            self.failure_count = 0

    def record_failure(self, error: Exception) -> None:
        """Notifies the breaker of a failed remote operation."""
        now = time.time()
        self.failure_count += 1
        self.last_failure_time = now

        logger.warning(
            f"[{self.name}] Falha na chamada ({error}). Falhas acumuladas: "
            f"{self.failure_count}/{self.failure_threshold} (Estado atual: {self.state.value})"
        )

        if self.state == CircuitState.HALF_OPEN:
            logger.error(
                f"[{self.name}] Falha detectada em teste HALF_OPEN! Reabrindo circuito imediatamente para OPEN."
            )
            self.state = CircuitState.OPEN
            self.last_state_change = now
            self.total_trips += 1
        elif self.state == CircuitState.CLOSED and self.failure_count >= self.failure_threshold:
            logger.error(
                f"[{self.name}] Limiar de {self.failure_threshold} falhas consecutivas atingido! "
                f"DISJUNTOR ACIONADO: Circuito ABERTO (OPEN). Fallback semântico assumirá 100% das mensagens "
                f"pelos próximos {self.recovery_timeout_seconds}s sem latência de rede."
            )
            self.state = CircuitState.OPEN
            self.last_state_change = now
            self.total_trips += 1

    def reset(self) -> None:
        """Manually forces the breaker back to normal CLOSED state."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_state_change = time.time()
        logger.info(f"[{self.name}] Circuito resetado manualmente para CLOSED.")

    def get_stats(self) -> Dict[str, Any]:
        """Returns runtime diagnostics for observability endpoints."""
        now = time.time()
        time_in_state = round(now - self.last_state_change, 2)
        remaining_lockout = 0.0
        if self.state == CircuitState.OPEN:
            remaining_lockout = max(
                0.0, round(self.recovery_timeout_seconds - (now - self.last_failure_time), 2)
            )

        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "success_count": self.success_count,
            "total_trips": self.total_trips,
            "time_in_current_state_seconds": time_in_state,
            "remaining_lockout_seconds": remaining_lockout,
            "can_execute": self.can_execute(),
        }
