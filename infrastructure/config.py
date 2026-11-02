"""
Application Configuration using Pydantic Settings.
Includes Business Hours logic with local timezone, safe non-conflicting ports,
multi-recipient staff notification settings, and Google Sheets API Key.
"""

from datetime import datetime, time
from typing import Any, Dict, List, Optional

import pytz
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    GEMINI_API_KEY: str = "demo_key"
    GEMINI_API_KEY_BACKUP: Optional[str] = None

    # Google Sheets Integration
    GOOGLE_SHEET_ID: Optional[str] = None
    GOOGLE_SHEETS_API_KEY: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: str = "credentials.json"

    # Portas seguras (não conflitam com 8080 nem 3000/3010 já em uso na VM da Oracle)
    PORT_BACKEND: int = 8005
    PORT_EVOLUTION: int = 8085

    EVOLUTION_API_URL: str = "http://localhost:8085"
    EVOLUTION_API_KEY: str = "ChaveSecretaLoja123"
    EVOLUTION_INSTANCE_NAME: str = "victor-cell-01"

    # Token de segurança opcional para proteger o endpoint de webhook
    WEBHOOK_SECRET_TOKEN: Optional[str] = None

    # Credenciais do Painel de Gerenciamento / Dashboard
    DASHBOARD_USERNAME: str = "admin"
    DASHBOARD_PASSWORD: str = "victorcell2026"
    DASHBOARD_SECRET_KEY: str = "victor-cell-secret-token-auth-2026"

    # Provedor de Estoque Plugável (Ports & Adapters: GOOGLE_SHEETS, BLING_V3, MEMORY)
    INVENTORY_PROVIDER: str = "GOOGLE_SHEETS"
    BLING_CLIENT_ID: Optional[str] = None
    BLING_CLIENT_SECRET: Optional[str] = None
    BLING_ACCESS_TOKEN: Optional[str] = None
    BLING_REFRESH_TOKEN: Optional[str] = None
    INVENTORY_CACHE_TTL: int = 300

    # Lista de números do balcão/caixa (separados por vírgula no .env)
    STAFF_PHONES: str = "5585999999999"

    DATABASE_PATH: str = "data/pecasbot.db"
    DATABASE_URL: Optional[str] = None

    STORE_TIMEZONE: str = "America/Fortaleza"
    STORE_OPENING_TIME: str = "08:30"
    STORE_CLOSING_TIME: str = "18:00"
    STORE_SAT_CLOSING_TIME: str = "13:00"

    DEBOUNCE_WAIT_SECONDS: float = 3.0
    HOLD_HOURS: int = 2
    ACTIVE_SKU_TIMEOUT_HOURS: int = 2

    # Configurações do ntfy (Alertas sonoros com vibração no celular da equipe)
    NTFY_ENABLED: bool = True
    NTFY_SERVER: str = "https://ntfy.sh"
    NTFY_TOPIC: str = "victor-cell-balcao-alertas"

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

    def get_store_schedule_status(self, now_dt: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Retorna o diagnóstico completo de horário de funcionamento no fuso de Fortaleza.
        Inclui status de abertura, descrição amigável de reabertura e texto conciso para o atendente/balcão.
        """
        tz = pytz.timezone(self.STORE_TIMEZONE)
        local_now = now_dt.astimezone(tz) if now_dt else datetime.now(tz)
        weekday = local_now.weekday()  # 0=Segunda, 4=Sexta, 5=Sábado, 6=Domingo
        current_time = local_now.time()

        open_h, open_m = map(int, self.STORE_OPENING_TIME.split(":"))
        open_time = time(open_h, open_m)

        if weekday == 5:
            close_h, close_m = map(int, self.STORE_SAT_CLOSING_TIME.split(":"))
        else:
            close_h, close_m = map(int, self.STORE_CLOSING_TIME.split(":"))
        close_time = time(close_h, close_m)

        weekday_names = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
        day_name = weekday_names[weekday]

        # Domingo
        if weekday == 6:
            return {
                "is_open": False,
                "is_sunday": True,
                "day_name": day_name,
                "current_time": local_now.strftime("%H:%M"),
                "reopen_desc": f"abre amanhã (segunda) às {self.STORE_OPENING_TIME}",
                "short_notice": f"Fechado hoje domingo, abre amanhã {self.STORE_OPENING_TIME}",
                "badge_text": f"🔴 Fechado Hoje (Domingo) • Reabre Segunda {self.STORE_OPENING_TIME}",
            }

        # Antes da abertura matinal
        if current_time < open_time:
            return {
                "is_open": False,
                "is_sunday": False,
                "day_name": day_name,
                "current_time": local_now.strftime("%H:%M"),
                "reopen_desc": f"abre hoje às {self.STORE_OPENING_TIME}",
                "short_notice": f"Fechado agora, abre hoje {self.STORE_OPENING_TIME}",
                "badge_text": f"🔴 Fechado • Reabre Hoje {self.STORE_OPENING_TIME}",
            }

        # Após o fechamento
        if current_time > close_time:
            if weekday == 5:  # Sábado após 13h
                reopen = f"abre segunda às {self.STORE_OPENING_TIME}"
                short = f"Fechado agora, abre segunda {self.STORE_OPENING_TIME}"
                badge = f"🔴 Fechado • Reabre Segunda {self.STORE_OPENING_TIME}"
            elif weekday == 4:  # Sexta após 18h
                reopen = f"abre amanhã (sábado) às {self.STORE_OPENING_TIME}"
                short = f"Fechado agora, abre amanhã (sábado) {self.STORE_OPENING_TIME}"
                badge = f"🔴 Fechado • Reabre Sábado {self.STORE_OPENING_TIME}"
            else:  # Seg-Qui após 18h
                reopen = f"abre amanhã às {self.STORE_OPENING_TIME}"
                short = f"Fechado agora, abre amanhã {self.STORE_OPENING_TIME}"
                badge = f"🔴 Fechado • Reabre Amanhã {self.STORE_OPENING_TIME}"

            return {
                "is_open": False,
                "is_sunday": False,
                "day_name": day_name,
                "current_time": local_now.strftime("%H:%M"),
                "reopen_desc": reopen,
                "short_notice": short,
                "badge_text": badge,
            }

        # Aberto
        sat_text = f"até {self.STORE_SAT_CLOSING_TIME}" if weekday == 5 else f"até {self.STORE_CLOSING_TIME}"
        return {
            "is_open": True,
            "is_sunday": False,
            "day_name": day_name,
            "current_time": local_now.strftime("%H:%M"),
            "reopen_desc": f"aberto agora ({sat_text})",
            "short_notice": "Loja aberta agora",
            "badge_text": f"🟢 Loja Aberta • Fecha {sat_text}",
        }

    def is_store_open(self, now_dt: Optional[datetime] = None) -> bool:
        """Verifica se a loja física está em horário de atendimento."""
        return bool(self.get_store_schedule_status(now_dt)["is_open"])


settings = Settings()
