"""
Catalog Search & Fuzzy Matching Service.
Provides robust model identification, technical synonym resolution, and typo tolerance
for balcão/WhatsApp queries without requiring heavy external NLP dependencies.
"""

import re
import unicodedata
from typing import Dict, List, Optional, Tuple

from domain.entities import Product, QualityTier


def remove_accents(text: str) -> str:
    """Removes diacritics/accents from a string (e.g. 'não' -> 'nao')."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def levenshtein_distance(s1: str, s2: str) -> int:
    """Computes pure Python Levenshtein edit distance between two strings."""
    if s1 == s2:
        return 0
    if len(s1) == 0:
        return len(s2)
    if len(s2) == 0:
        return len(s1)

    v0 = list(range(len(s2) + 1))
    v1 = [0] * (len(s2) + 1)

    for i in range(len(s1)):
        v1[0] = i + 1
        for j in range(len(s2)):
            cost = 0 if s1[i] == s2[j] else 1
            v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
        for j in range(len(s2) + 1):
            v0[j] = v1[j]

    return v0[len(s2)]


def string_similarity(s1: str, s2: str) -> float:
    """Returns normalized similarity ratio between 0.0 (completely different) and 1.0 (identical)."""
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    dist = levenshtein_distance(s1, s2)
    return 1.0 - (dist / max_len)


# Dicionário de Sinônimos, Codinomes de Fábrica e Erros Ortográficos Frequentes de Tablets
TABLET_MODEL_ALIASES: Dict[str, List[str]] = {
    "Tab A7 Lite": [
        "tab a7 lite",
        "a7 lite",
        "t220",
        "t225",
        "sm-t220",
        "sm-t225",
        "smt220",
        "smt225",
        "tab a7l",
        "a7l",
        "tab a 7 lite",
        "a7lite",
    ],
    "Tab A7": [
        "tab a7",
        "a7 10.4",
        "t500",
        "t505",
        "sm-t500",
        "sm-t505",
        "smt500",
        "smt505",
        "tab a 7",
        "a7 10",
    ],
    "Tab A 8.0 (2019)": [
        "tab a 8.0",
        "tab a 8",
        "t290",
        "t295",
        "sm-t290",
        "sm-t295",
        "smt290",
        "smt295",
        "tab a 2019",
        "tab t290",
        "tab t295",
    ],
    "Tab A8": [
        "tab a8",
        "a8 10.5",
        "x200",
        "x205",
        "sm-x200",
        "sm-x205",
        "smx200",
        "smx205",
        "tab a 8 10.5",
    ],
    "Tab A9": [
        "tab a9",
        "x110",
        "x115",
        "sm-x110",
        "sm-x115",
        "smx110",
        "smx115",
    ],
    "Tab A9+": [
        "tab a9+",
        "tab a9 plus",
        "a9 plus",
        "a9+",
        "x210",
        "x216",
        "sm-x210",
        "sm-x216",
    ],
    "Multilaser M10A": [
        "m10a",
        "m10-a",
        "multilaser m10a",
        "nb304",
        "nb305",
        "nb 304",
        "nb 305",
        "m10a 3g",
        "m10a 4g",
        "m 10a",
    ],
    "Multilaser M7s": [
        "m7s",
        "m7-s",
        "m7 3g",
        "multilaser m7",
        "multilaser m7s",
        "nb301",
        "nb302",
        "nb303",
        "nb 301",
        "nb 302",
        "nb 303",
        "m 7s",
        "m 7",
    ],
    "Multilaser M8": [
        "m8",
        "m8 4g",
        "multilaser m8",
        "nb353",
        "nb354",
        "m 8",
    ],
}

PART_TYPE_SYNONYMS: Dict[str, List[str]] = {
    "display": ["tela", "display", "frontal", "frontar", "telinha", "modulo", "módulo", "lcd"],
    "touch": ["touch", "toque", "vidro touch", "touchscreen"],
    "bateria": ["bateria", "pilha", "acumulador"],
    "conector": ["conector", "carga", "dock", "entrada carregador", "subplaca"],
}


class CatalogSearchService:
    """
    Search and matching engine for parts and models.
    Tolerates spelling mistakes, slang, regional technical terms and model acronyms.
    """

    @classmethod
    def clean_query(cls, text: str) -> str:
        """Cleans and standardizes raw text."""
        t = remove_accents(text.lower())
        # Mantém apenas letras, números e hífens
        t = re.sub(r"[^\w\s\-\+]", " ", t)
        return " ".join(t.split())

    @classmethod
    def detect_model_alias(cls, text: str) -> Optional[str]:
        """Detects canonical model from text using exact keyword / alias lookup or fuzzy matching."""
        clean = cls.clean_query(text)
        words = clean.split()

        # 1. Busca direta por alias exato ou substring de alias no texto
        for canonical, aliases in TABLET_MODEL_ALIASES.items():
            for alias in aliases:
                # Busca por palavra exata ou correspondência no texto
                pattern = r"(?:\b|^)" + re.escape(alias) + r"(?:\b|$)"
                if re.search(pattern, clean):
                    return canonical

        # 2. Fuzzy match por token individual ou bi-gramas para erros de digitação (ex: 'sansung a7lite', 't295')
        tokens = words
        for i in range(len(tokens)):
            single = tokens[i]
            for canonical, aliases in TABLET_MODEL_ALIASES.items():
                for alias in aliases:
                    if len(single) >= 3 and len(alias) >= 3:
                        if string_similarity(single, alias) >= 0.85:
                            return canonical

            if i + 1 < len(tokens):
                bigram = f"{tokens[i]} {tokens[i+1]}"
                for canonical, aliases in TABLET_MODEL_ALIASES.items():
                    for alias in aliases:
                        if len(bigram) >= 4 and len(alias) >= 4:
                            if string_similarity(bigram, alias) >= 0.85:
                                return canonical

        return None

    @classmethod
    def detect_part_type(cls, text: str) -> Optional[str]:
        """Identifies the requested technical part (display, touch, battery, charging port)."""
        clean = cls.clean_query(text)
        for part_type, synonyms in PART_TYPE_SYNONYMS.items():
            for syn in synonyms:
                pattern = r"(?:\b|^)" + re.escape(syn) + r"(?:\b|$)"
                if re.search(pattern, clean):
                    return part_type
        return None

    @classmethod
    def detect_quality_and_frame(cls, text: str) -> Tuple[Optional[QualityTier], Optional[bool]]:
        """Identifies desired quality tier and frame specifications."""
        clean = cls.clean_query(text)
        quality = None
        has_frame = None

        if any(w in clean for w in ["original", "nacional", "genuina", "genuina"]):
            quality = QualityTier.ORIGINAL_NACIONAL
        elif any(w in clean for w in ["paralela", "china", "primeira linha", "1 linha", "paralelo"]):
            quality = QualityTier.PARALELA_CHINA

        if "com aro" in clean or "com carcaça" in clean:
            has_frame = True
        elif "sem aro" in clean or "sem carcaca" in clean:
            has_frame = False

        return quality, has_frame

    @classmethod
    def search_best_matches(
        cls,
        products: List[Product],
        query: str,
        min_threshold: float = 0.65,
    ) -> List[Tuple[Product, float]]:
        """
        Scores all products in the catalog against the customer's query.
        Returns products sorted by score descending.
        """
        canonical_model = cls.detect_model_alias(query)
        detected_part = cls.detect_part_type(query)
        desired_quality, desired_frame = cls.detect_quality_and_frame(query)

        clean_query = cls.clean_query(query)
        scored_products: List[Tuple[Product, float]] = []

        for p in products:
            clean_name = cls.clean_query(p.name)
            clean_sku = cls.clean_query(p.sku)
            score = 0.0

            # 1. Correspondência exata de SKU
            if clean_sku in clean_query:
                score += 1.0

            # 2. Correspondência de Modelo Canônico
            if canonical_model:
                clean_canonical = cls.clean_query(canonical_model)
                if clean_canonical in clean_name:
                    score += 0.50
                elif any(cls.clean_query(alias) in clean_name for alias in TABLET_MODEL_ALIASES.get(canonical_model, [])):
                    score += 0.45
            else:
                # Similaridade de texto no nome
                words = clean_query.split()
                name_words = clean_name.split()
                matched_words = sum(1 for w in words if any(string_similarity(w, nw) >= 0.85 for nw in name_words))
                if words:
                    score += (matched_words / len(words)) * 0.4

            # 3. Correspondência do Tipo de Peça (Display vs Touch vs Bateria)
            if detected_part:
                clean_part = cls.clean_query(detected_part)
                if clean_part in clean_name or any(s in clean_name for s in PART_TYPE_SYNONYMS.get(detected_part, [])):
                    score += 0.30
                else:
                    # Penalidade se o cliente pediu touch e o produto for display
                    if detected_part == "touch" and "display" in clean_name and "touch" not in clean_name:
                        score -= 0.25
                    elif detected_part == "display" and "touch" in clean_name and "display" not in clean_name:
                        score -= 0.25

            # 4. Qualidade e Aro
            if desired_quality is not None:
                if p.quality == desired_quality:
                    score += 0.15
                else:
                    score -= 0.10

            if desired_frame is not None:
                if p.has_frame == desired_frame:
                    score += 0.10
                else:
                    score -= 0.05

            # Bônus se está em estoque
            if p.is_in_stock:
                score += 0.05

            if score >= min_threshold:
                scored_products.append((p, round(score, 3)))

        scored_products.sort(key=lambda x: x[1], reverse=True)
        return scored_products
