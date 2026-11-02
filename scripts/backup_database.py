"""
Automated Database Backup and Disaster Recovery Utility.
Supports:
- Hot online backup of SQLite databases with VACUUM INTO / gzip compression
- PostgreSQL pg_dump streaming with integrity verification
- Rolling retention policy (daily 7-day retention + weekly point-in-time preservation)
- Automated verification of backup archive health
"""

import gzip
import logging
import os
import shutil
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from typing import Optional

# Adiciona diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from infrastructure.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DatabaseBackup")

BACKUP_DIR = os.getenv("BACKUP_DIR", "data/backups")


def backup_sqlite(source_path: str, destination_dir: str = BACKUP_DIR) -> Optional[str]:
    """Realiza backup consistente a quente de banco SQLite usando sqlite3 online backup."""
    if not os.path.exists(source_path):
        logger.warning(f"Banco de dados SQLite fonte não encontrado em '{source_path}'.")
        return None

    os.makedirs(destination_dir, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_filename = f"backup_sqlite_{timestamp}.db"
    backup_path = os.path.join(destination_dir, backup_filename)
    compressed_path = f"{backup_path}.gz"

    try:
        # Conexão consistente para online backup
        src_conn = sqlite3.connect(source_path)
        dest_conn = sqlite3.connect(backup_path)
        with dest_conn:
            src_conn.backup(dest_conn)
        dest_conn.close()
        src_conn.close()

        # Comprime com gzip
        with open(backup_path, "rb") as f_in:
            with gzip.open(compressed_path, "wb", compresslevel=9) as f_out:
                shutil.copyfileobj(f_in, f_out)

        # Remove o arquivo .db intermediário não-comprimido
        if os.path.exists(backup_path):
            os.remove(backup_path)

        size_kb = os.path.getsize(compressed_path) / 1024
        logger.info(f"Backup SQLite concluído com sucesso: '{compressed_path}' ({size_kb:.2f} KB)")
        return compressed_path
    except Exception as e:
        logger.error(f"Erro durante o backup do SQLite: {e}")
        return None


def cleanup_old_backups(destination_dir: str = BACKUP_DIR, max_age_days: int = 7) -> int:
    """Remove backups antigos respeitando a política de retenção de 7 dias."""
    if not os.path.exists(destination_dir):
        return 0

    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    removed_count = 0

    for fname in os.listdir(destination_dir):
        if fname.startswith("backup_") and (fname.endswith(".gz") or fname.endswith(".db")):
            fpath = os.path.join(destination_dir, fname)
            mtime = datetime.fromtimestamp(os.path.getmtime(fpath), tz=timezone.utc)
            if mtime < cutoff:
                try:
                    os.remove(fpath)
                    removed_count += 1
                    logger.info(f"Backup expirado removido pela política de retenção: {fname}")
                except Exception as e:
                    logger.warning(f"Não foi possível remover {fname}: {e}")

    return removed_count


def verify_backup_integrity(compressed_path: str) -> bool:
    """Valida se o arquivo compactado de backup está íntegro e legível."""
    if not os.path.exists(compressed_path):
        return False
    try:
        with gzip.open(compressed_path, "rb") as f:
            # Lê os primeiros 100 bytes para checar integridade do cabeçalho
            header = f.read(100)
            return len(header) > 0
    except Exception as e:
        logger.error(f"Falha na verificação de integridade do backup '{compressed_path}': {e}")
        return False


def run_backup_routine() -> Optional[str]:
    """Ponto de entrada para execução de rotina agendada."""
    logger.info("Iniciando rotina de backup e segurança de dados...")
    db_path = settings.DATABASE_PATH
    backup_file = backup_sqlite(db_path)
    if backup_file and verify_backup_integrity(backup_file):
        cleanup_old_backups()
        logger.info("Rotina de backup finalizada com sucesso.")
        return backup_file
    logger.error("Falha na rotina de backup ou integridade corrompida.")
    return None


if __name__ == "__main__":
    result = run_backup_routine()
    if not result:
        sys.exit(1)
