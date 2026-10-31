"""
Application Configuration using Pydantic Settings.
Includes Business Hours logic with local timezone, safe non-conflicting ports,
multi-recipient staff notification settings, and optional webhook authentication.
"""

from datetime import datetime, time
from typing import List, Optional

import pytz
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    GEMINI_API_KEY: str = "demo_key"
    GEMINI_API_KEY_BACKUP: Optional[str] = None

    # Portas seguras (não conflitam com 8080 nem 3000/3010 já em uso na VM da Oracle)
    PORT_BACKEND: int = 8005
    PORT_EVOLUTION: int = 8085

    EVOLUTION_API_URL: str = "http://localhost:8085"
    EVOLUTION_API_KEY: str = "ChaveSecretaLoja123"
    EVOLUTION_INSTANCE_NAME: str = "victor-cell-01"

    # Token de segurança opcional para proteger o endpoint de webhook
    WEBHOOK_SECRET_TOKEN: Optional[str] = None

    # Lista de números do balcão/caixa (separados por vírgula no .env)
    STAFF_PHONES: str = "5585999999999"

    DATABASE_PATH: str = "data/pecasbot.db"

    STORE_TIMEZONE: str = "America/Fortaleza"
    STORE_OPENING_TIME: str = "08:30"
    STORE_CLOSING_TIME: str = "18:00"
    STORE_SAT_CLOSING_TIME: str = "13:00"

    DEBOUNCE_WAIT_SECONDS: float = 3.0
    HOLD_HOURS: int = 2
    ACTIVE_SKU_TIMEOUT_HOURS: int = 2

    def get_staff_phone_list(self) -> List[str]:
        """Retorna a lista de telefones da equipe do balcão limpos de caracteres."""
        phones = []
        for raw in self.STAFF_PHONES.split(","):
            clean = "".join(filter(str.isdigit, raw))
            if clean:
                phones.append(clean)
        return phones or ["5585999999999"]

    def get_local_now(self) -> datetime:
        """Retorna o datetime atual no fuso de Fortaleza."""
        tz = pytz.timezone(self.STORE_TIMEZONE)
        return datetime.now(tz)

    def is_store_open(self, now_dt: Optional[datetime] = None) -> bool:
        """Verifica se a loja física está em horário de atendimento."""
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
