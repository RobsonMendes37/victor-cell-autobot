"""
Database Repository Factory (Pluggable Persistence Provider).
Dynamically instantiates PostgresRepository (for scalable enterprise multi-client deployment)
or SqliteRepository (for lightweight self-hosted deployment) based on configuration.
"""

import logging
from typing import Any, Optional
from infrastructure.config import settings
from infrastructure.repositories.sqlite_repository import SqliteRepository

logger = logging.getLogger(__name__)


def create_database_repository(
    database_url: Optional[str] = None,
    sqlite_path: Optional[str] = None,
) -> Any:
    """
    Factory method to initialize the active persistence backend.
    Checks DATABASE_URL first; if not provided or empty, falls back to SQLite.
    """
    dsn = database_url or settings.DATABASE_URL
    if dsn and (dsn.startswith("postgres://") or dsn.startswith("postgresql://")):
        try:
            from infrastructure.repositories.postgres_repository import PostgresRepository
            logger.info(f"[DatabaseFactory] Inicializando repositório PostgreSQL (Enterprise DSN configurado).")
            return PostgresRepository(dsn=dsn)
        except Exception as e:
            logger.error(f"[DatabaseFactory] Falha ao instanciar PostgresRepository ({e}). Recorrendo ao SQLite.")

    path = sqlite_path or settings.DATABASE_PATH
    logger.info(f"[DatabaseFactory] Inicializando repositório SQLite: '{path}'.")
    return SqliteRepository(db_path=path)
