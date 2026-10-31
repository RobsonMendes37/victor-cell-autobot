"""
Application Configuration using Pydantic Settings.
Includes Business Hours logic with local timezone and safe port defaults.
"""

from datetime import datetime, time
from typing import Optional

import pytz
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    GEMINI_API_KEY: str = "demo_key"
    GEMINI_API_KEY_BACKUP: Optional[str] = None

    # Portas seguras para não conflitar com 8080 (Java local) nem 3000/3010 (VM Oracle)
    PORT_BACKEND: int = 8005
    PORT_EVOLUTION: int = 8085

    EVOLUTION_API_URL: str = "http://localhost:8085"
    EVOLUTION_API_KEY: str = "ChaveSecretaLoja123"
    EVOLUTION_INSTANCE_NAME: str = "victor-cell-01"

    CAIXA_STAFF_PHONE: str = "5585999999999"

    DATABASE_PATH: str = "data/pecasbot.db"

    STORE_TIMEZONE: str = "America/Fortaleza"
    STORE_OPENING_TIME: str = "08:30"
    STORE_CLOSING_TIME: str = "18:00"
    STORE_SAT_CLOSING_TIME: str = "13:00"

    DEBOUNCE_WAIT_SECONDS: float = 3.0
    HOLD_HOURS: int = 2
    ACTIVE_SKU_TIMEOUT_HOURS: int = 2

    def get_local_now(self) -> datetime:
        """Returns current datetime in Fortaleza timezone."""
        tz = pytz.timezone(self.STORE_TIMEZONE)
        return datetime.now(tz)

    def is_store_open(self, now_dt: Optional[datetime] = None) -> bool:
        """Checks whether the physical store is open based on Fortaleza timezone."""
        tz = pytz.timezone(self.STORE_TIMEZONE)
        local_now = now_dt.astimezone(tz) if now_dt else datetime.now(tz)

        weekday = local_now.weekday()  # 0=Segunda, 5=Sábado, 6=Domingo
        if weekday == 6:  # Domingo fechado
            return False

        current_time = local_now.time()

        open_h, open_m = map(int, self.STORE_OPENING_TIME.split(":"))
        open_time = time(open_h, open_m)

        if weekday == 5:  # Sábado até 13h
            close_h, close_m = map(int, self.STORE_SAT_CLOSING_TIME.split(":"))
        else:  # Seg-Sex até 18h
            close_h, close_m = map(int, self.STORE_CLOSING_TIME.split(":"))
        close_time = time(close_h, close_m)

        return open_time <= current_time <= close_time


settings = Settings()
