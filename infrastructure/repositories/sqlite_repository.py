"""
SQLite Asynchronous Repository using aiosqlite with WAL mode enabled.
Persists Conversations, Orders, Messages (history), and Sent Message IDs.
"""

import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

import aiosqlite

from domain.entities import (
    Conversation,
    ConversationState,
    OrderStatus,
    ReservationOrder,
)
from domain.repositories import (
    ConversationRepositoryInterface,
    OrderRepositoryInterface,
)
from infrastructure.config import settings


class SqliteRepository(ConversationRepositoryInterface, OrderRepositoryInterface):
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.DATABASE_PATH
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)

    async def init_db(self) -> None:
        """Initializes database schema and activates WAL mode for high concurrency."""
        async with aiosqlite.connect(self.db_path) as db:
            # Ativa WAL Mode (Write-Ahead Logging) para alta concorrência
            await db.execute("PRAGMA journal_mode = WAL;")
            await db.execute("PRAGMA synchronous = NORMAL;")

            # 1. Tabela de Conversas
            await db.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    customer_phone TEXT PRIMARY KEY,
                    id TEXT NOT NULL,
                    state TEXT NOT NULL,
                    last_activity_at TEXT NOT NULL,
                    human_resumed_at TEXT,
                    human_silence_duration_hours INTEGER DEFAULT 3,
                    active_sku TEXT,
                    notes TEXT
                )
            """)

            # 2. Tabela de Mensagens para Histórico Multi-Turn
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_phone TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_phone ON messages(customer_phone, timestamp);
            """)

            # 3. Tabela de Pedidos para o Caixa/Expedição
            await db.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id TEXT PRIMARY KEY,
                    customer_phone TEXT NOT NULL,
                    customer_name TEXT NOT NULL,
                    product_sku TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    product_price REAL NOT NULL,
                    destination_address TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL
                )
            """)

            # 4. Tabela de Mensagens Enviadas pelo Bot (Proteção contra loops)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sent_messages (
                    message_id TEXT PRIMARY KEY,
                    sent_at TEXT NOT NULL
                )
            """)
            await db.commit()

    # --- Conversas e Histórico Multi-Turn ---

    async def get_or_create(self, customer_phone: str) -> Conversation:
        await self.init_db()
        clean_phone = "".join(filter(str.isdigit, customer_phone))
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM conversations WHERE customer_phone = ?",
                (clean_phone,),
            )
            row = await cursor.fetchone()

            if row:
                human_resumed_at = (
                    datetime.fromisoformat(row["human_resumed_at"])
                    if row["human_resumed_at"]
                    else None
                )
                return Conversation(
                    id=row["id"],
                    customer_phone=row["customer_phone"],
                    state=ConversationState(row["state"]),
                    last_activity_at=datetime.fromisoformat(row["last_activity_at"]),
                    human_resumed_at=human_resumed_at,
                    human_silence_duration_hours=row["human_silence_duration_hours"],
                    active_sku=row["active_sku"],
                    notes=row["notes"],
                )
            else:
                new_conv = Conversation(
                    id=clean_phone,
                    customer_phone=clean_phone,
                    state=ConversationState.AI_ACTIVE,
                )
                await self.save(new_conv)
                return new_conv

    async def save(self, conversation: Conversation) -> None:
        clean_phone = "".join(filter(str.isdigit, conversation.customer_phone))
        human_resumed_str = (
            conversation.human_resumed_at.isoformat() if conversation.human_resumed_at else None
        )
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO conversations (
                    customer_phone, id, state, last_activity_at,
                    human_resumed_at, human_silence_duration_hours, active_sku, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(customer_phone) DO UPDATE SET
                    state = excluded.state,
                    last_activity_at = excluded.last_activity_at,
                    human_resumed_at = excluded.human_resumed_at,
                    human_silence_duration_hours = excluded.human_silence_duration_hours,
                    active_sku = excluded.active_sku,
                    notes = excluded.notes
            """,
                (
                    clean_phone,
                    conversation.id,
                    conversation.state.value,
                    conversation.last_activity_at.isoformat(),
                    human_resumed_str,
                    conversation.human_silence_duration_hours,
                    conversation.active_sku,
                    conversation.notes,
                ),
            )
            await db.commit()

    async def save_message(self, customer_phone: str, role: str, content: str) -> None:
        """Saves a message turn to history."""
        clean_phone = "".join(filter(str.isdigit, customer_phone))
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO messages (customer_phone, role, content, timestamp)
                VALUES (?, ?, ?, ?)
            """,
                (clean_phone, role, content, datetime.now(timezone.utc).isoformat()),
            )
            await db.commit()

    async def get_recent_messages(
        self, customer_phone: str, limit: int = 8
    ) -> List[Dict[str, str]]:
        """Retrieves recent conversation turns for multi-turn context."""
        clean_phone = "".join(filter(str.isdigit, customer_phone))
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT role, content FROM messages
                WHERE customer_phone = ?
                ORDER BY id DESC LIMIT ?
            """,
                (clean_phone, limit),
            )
            rows = await cursor.fetchall()
            # Inverte para ordem cronológica (mais antiga para mais recente)
            return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

    # --- Pedidos ---

    async def save_order(self, order: ReservationOrder) -> str:
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO orders (
                    id, customer_phone, customer_name, product_sku,
                    quantity, product_price, destination_address,
                    status, created_at, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    status = excluded.status,
                    destination_address = excluded.destination_address
            """,
                (
                    order.id,
                    order.customer_phone,
                    order.customer_name,
                    order.product_sku,
                    order.quantity,
                    order.product_price,
                    order.destination_address,
                    order.status.value,
                    order.created_at.isoformat(),
                    order.expires_at.isoformat(),
                ),
            )
            await db.commit()
        return order.id

    async def list_orders(self) -> List[ReservationOrder]:
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM orders ORDER BY created_at DESC")
            rows = await cursor.fetchall()
            orders = []
            for r in rows:
                orders.append(
                    ReservationOrder(
                        id=r["id"],
                        customer_phone=r["customer_phone"],
                        customer_name=r["customer_name"],
                        product_sku=r["product_sku"],
                        quantity=r["quantity"],
                        product_price=r["product_price"],
                        destination_address=r["destination_address"],
                        status=OrderStatus(r["status"]),
                        created_at=datetime.fromisoformat(r["created_at"]),
                        expires_at=datetime.fromisoformat(r["expires_at"]),
                    )
                )
            return orders

    # --- Proteção Contra Auto-Silenciamento ---

    async def record_sent_message(self, message_id: str) -> None:
        if not message_id:
            return
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO sent_messages (message_id, sent_at) VALUES (?, ?)",
                (message_id, datetime.now(timezone.utc).isoformat()),
            )
            await db.commit()

    async def is_sent_by_bot(self, message_id: str) -> bool:
        if not message_id:
            return False
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT 1 FROM sent_messages WHERE message_id = ?",
                (message_id,),
            )
            row = await cursor.fetchone()
            return row is not None

    async def is_bot_sent_message(self, message_id: str) -> bool:
        return await self.is_sent_by_bot(message_id)

    async def get_by_phone(self, customer_phone: str) -> Optional[Conversation]:
        return await self.get_or_create(customer_phone)
