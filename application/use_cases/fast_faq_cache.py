"""
Fast In-Memory FAQ Cache Service.
Provides sub-millisecond, deterministic balcão responses for common high-frequency queries
(store address, pix key, operating hours) with zero network latency and zero AI token cost.
"""

import re
from typing import Any, Dict, Optional

from domain.entities import StoreProfile
from infrastructure.config import settings


class FastFaqCacheService:
    """
    Sub-millisecond FAQ matching engine.
    Uses precompiled regex to detect standard store questions.
    """

    ADDRESS_PATTERNS = [
        r"\b(?:qual\s+(?:o\s+)?endere[cç]o|onde\s+fica|onde\s+[eé]\s+a\s+loja|localiza[cç][aã]o|manda\s+(?:o\s+)?endere[cç]o|manda\s+localiza[cç][aã]o|fica\s+onde|local\s+da\s+loja)\b",
    ]

    PIX_PATTERNS = [
        r"\b(?:qual\s+(?:o\s+)?pix|passa\s+(?:o\s+)?pix|manda\s+(?:o\s+)?pix|chave\s+pix|qual\s+a\s+chave\s+pix|dados\s+(?:pra|para)\s+pix|tem\s+pix)\b",
    ]

    HOURS_PATTERNS = [
        r"\b(?:que\s+horas\s+abre|qual\s+(?:o\s+)?hor[aá]rio|hor[aá]rio\s+de\s+funcionamento|que\s+horas\s+fecha|t[aá]\s+aberto|at[eé]\s+que\s+horas)\b",
    ]

    @classmethod
    def match_faq(
        cls, text: str, store_profile: Optional[StoreProfile] = None
    ) -> Optional[Dict[str, Any]]:
        clean = text.lower().strip()
        # Não intercepta se o cliente estiver cotando peça junto ("qual o pix da tela do a7")
        part_keywords = [
            "tela",
            "touch",
            "display",
            "bateria",
            "t220",
            "t295",
            "x200",
            "m10a",
            "m7",
            "separa",
            "separar",
            "uber",
        ]
        if any(w in clean for w in part_keywords):
            return None

        # 1. Endereço
        for pat in cls.ADDRESS_PATTERNS:
            if re.search(pat, clean, re.IGNORECASE):
                addr = (
                    store_profile.address
                    if (store_profile and store_profile.address)
                    else "Rua Barão do Rio Branco 1102, Centro."
                )
                return {
                    "matched": True,
                    "intent": "FAQ_ADDRESS",
                    "reply_text": addr,
                }

        # 2. Chave Pix
        for pat in cls.PIX_PATTERNS:
            if re.search(pat, clean, re.IGNORECASE):
                pix = (
                    f"Pix: {store_profile.pix_key}"
                    if (store_profile and store_profile.pix_key)
                    else "Pix: 85999990001 (Celular / Victor Cell)."
                )
                return {
                    "matched": True,
                    "intent": "FAQ_PIX",
                    "reply_text": pix,
                }

        # 3. Horário de Funcionamento
        for pat in cls.HOURS_PATTERNS:
            if re.search(pat, clean, re.IGNORECASE):
                sched = settings.get_store_schedule_status()
                if sched["is_open"]:
                    reply = (
                        f"Seg a Sex {settings.STORE_OPENING_TIME} às {settings.STORE_CLOSING_TIME}, "
                        f"Sáb até {settings.STORE_SAT_CLOSING_TIME}."
                    )
                else:
                    reply = f"Fechado. Abre amanhã {settings.STORE_OPENING_TIME}."
                return {
                    "matched": True,
                    "intent": "FAQ_HOURS",
                    "reply_text": reply,
                }

        return None
