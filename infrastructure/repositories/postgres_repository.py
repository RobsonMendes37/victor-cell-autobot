"""
PostgreSQL Repository Implementation using asyncpg.
Enterprise persistence adapter for multi-tenant deployments, point-in-time recovery and large-scale concurrency.
Implements ConversationRepositoryInterface, OrderRepositoryInterface and AuditLogInterface.
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import asyncpg

from domain.entities import (
    AuditLogEntry,
    Conversation,
    ConversationState,
    OrderStatus,
    ReservationOrder,
    StoreProfile,
)

logger = logging.getLogger(__name__)


class PostgresRepository:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self._pool: Optional[asyncpg.Pool] = None
        self._initialized = False

    async def _get_pool(self) -> asyncpg.Pool:
        if self._pool is None:
            self._pool = await asyncpg.create_pool(self.dsn, min_size=2, max_size=20)
        return self._pool

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()
            self._pool = None

    async def init_db(self) -> None:
        """Executa DDL de inicialização do schema no PostgreSQL."""
        if self._initialized:
            return
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    customer_phone TEXT UNIQUE NOT NULL,
                    customer_name TEXT,
                    state TEXT NOT NULL,
                    last_activity_at TIMESTAMPTZ NOT NULL,
                    human_resumed_at TIMESTAMPTZ,
                    human_silence_duration_hours INTEGER DEFAULT 3,
                    active_sku TEXT,
                    notes TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_pg_conv_phone ON conversations(customer_phone);

                CREATE TABLE IF NOT EXISTS messages (
                    id BIGSERIAL PRIMARY KEY,
                    customer_phone TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_pg_msg_phone ON messages(customer_phone, timestamp);

                CREATE TABLE IF NOT EXISTS orders (
                    id TEXT PRIMARY KEY,
                    customer_phone TEXT NOT NULL,
                    customer_name TEXT NOT NULL,
                    product_sku TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    product_price NUMERIC(10, 2) NOT NULL,
                    destination_address TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL,
                    expires_at TIMESTAMPTZ NOT NULL
                );

                CREATE TABLE IF NOT EXISTS sent_messages (
                    message_id TEXT PRIMARY KEY,
                    sent_at TIMESTAMPTZ NOT NULL
                );

                CREATE TABLE IF NOT EXISTS cached_products (
                    sku TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    compatible_models TEXT NOT NULL,
                    quality TEXT NOT NULL,
                    has_frame BOOLEAN NOT NULL,
                    price NUMERIC(10, 2) NOT NULL,
                    stock_quantity INTEGER NOT NULL,
                    warranty_days INTEGER DEFAULT 90,
                    has_stock BOOLEAN DEFAULT TRUE,
                    updated_at TIMESTAMPTZ NOT NULL
                );

                CREATE TABLE IF NOT EXISTS quote_logs (
                    id BIGSERIAL PRIMARY KEY,
                    customer_phone TEXT NOT NULL,
                    query_text TEXT NOT NULL,
                    target_sku TEXT,
                    had_stock BOOLEAN DEFAULT TRUE,
                    timestamp TIMESTAMPTZ NOT NULL
                );

                CREATE TABLE IF NOT EXISTS system_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                INSERT INTO system_settings (key, value) VALUES ('global_ai_enabled', '1')
                ON CONFLICT (key) DO NOTHING;

                CREATE TABLE IF NOT EXISTS store_profile (
                    store_id TEXT PRIMARY KEY,
                    store_name TEXT NOT NULL,
                    city TEXT NOT NULL,
                    niche_description TEXT NOT NULL,
                    out_of_scope_keywords TEXT NOT NULL,
                    rejection_message TEXT NOT NULL,
                    delivery_methods TEXT NOT NULL,
                    tone_guidelines TEXT NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL
                );

                CREATE TABLE IF NOT EXISTS audit_logs (
                    id TEXT PRIMARY KEY,
                    timestamp TIMESTAMPTZ NOT NULL,
                    level TEXT NOT NULL,
                    component TEXT NOT NULL,
                    action TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    details JSONB NOT NULL,
                    duration_ms DOUBLE PRECISION,
                    status TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_pg_audit_ts ON audit_logs(timestamp DESC);
                CREATE INDEX IF NOT EXISTS idx_pg_audit_comp ON audit_logs(component, level);
            """)
        self._initialized = True
        logger.info("[PostgresRepository] Schema do PostgreSQL inicializado e homologado.")

    async def get_or_create(self, customer_phone: str) -> Conversation:
        await self.init_db()
        clean_phone = "".join(filter(str.isdigit, customer_phone))
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM conversations WHERE customer_phone = $1", clean_phone
            )
            if row:
                return Conversation(
                    id=row["id"],
                    customer_phone=row["customer_phone"],
                    customer_name=row["customer_name"],
                    state=ConversationState(row["state"]),
                    last_activity_at=row["last_activity_at"],
                    human_resumed_at=row["human_resumed_at"],
                    human_silence_duration_hours=row["human_silence_duration_hours"],
                    active_sku=row["active_sku"],
                    notes=row["notes"],
                )
            new_conv = Conversation(
                id=f"conv_{clean_phone}",
                customer_phone=clean_phone,
            )
            await conn.execute(
                """
                INSERT INTO conversations (
                    id, customer_phone, customer_name, state, last_activity_at,
                    human_resumed_at, human_silence_duration_hours, active_sku, notes
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (customer_phone) DO NOTHING
                """,
                new_conv.id,
                new_conv.customer_phone,
                new_conv.customer_name,
                new_conv.state.value,
                new_conv.last_activity_at,
                new_conv.human_resumed_at,
                new_conv.human_silence_duration_hours,
                new_conv.active_sku,
                new_conv.notes,
            )
            return new_conv

    async def save_conversation(self, conv: Conversation) -> None:
        await self.init_db()
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO conversations (
                    id, customer_phone, customer_name, state, last_activity_at,
                    human_resumed_at, human_silence_duration_hours, active_sku, notes
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (customer_phone) DO UPDATE SET
                    customer_name = EXCLUDED.customer_name,
                    state = EXCLUDED.state,
                    last_activity_at = EXCLUDED.last_activity_at,
                    human_resumed_at = EXCLUDED.human_resumed_at,
                    human_silence_duration_hours = EXCLUDED.human_silence_duration_hours,
                    active_sku = EXCLUDED.active_sku,
                    notes = EXCLUDED.notes
                """,
                conv.id,
                conv.customer_phone,
                conv.customer_name,
                conv.state.value,
                conv.last_activity_at,
                conv.human_resumed_at,
                conv.human_silence_duration_hours,
                conv.active_sku,
                conv.notes,
            )

    save = save_conversation

    async def save_message(self, customer_phone: str, role: str, content: str) -> None:
        await self.init_db()
        clean_phone = "".join(filter(str.isdigit, customer_phone))
        now = datetime.now(timezone.utc)
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO messages (customer_phone, role, content, timestamp) VALUES ($1, $2, $3, $4)",
                clean_phone,
                role,
                content,
                now,
            )

    async def get_recent_messages(
        self, customer_phone: str, limit: int = 8, max_age_hours: int = 2
    ) -> List[Dict[str, str]]:
        await self.init_db()
        clean_phone = "".join(filter(str.isdigit, customer_phone))
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT role, content FROM (
                    SELECT id, role, content FROM messages
                    WHERE customer_phone = $1 AND timestamp >= $2
                    ORDER BY timestamp DESC LIMIT $3
                ) sub ORDER BY id ASC
                """,
                clean_phone,
                cutoff,
                limit,
            )
            return [{"role": r["role"], "content": r["content"]} for r in rows]

    async def save_order(self, order: ReservationOrder) -> str:
        await self.init_db()
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO orders (
                    id, customer_phone, customer_name, product_sku,
                    quantity, product_price, destination_address,
                    status, created_at, expires_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ON CONFLICT (id) DO UPDATE SET
                    status = EXCLUDED.status,
                    destination_address = EXCLUDED.destination_address
                """,
                order.id,
                order.customer_phone,
                order.customer_name,
                order.product_sku,
                order.quantity,
                order.product_price,
                order.destination_address,
                order.status.value,
                order.created_at,
                order.expires_at,
            )
        return order.id

    async def list_orders(self) -> List[ReservationOrder]:
        await self.init_db()
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM orders ORDER BY created_at DESC")
            return [
                ReservationOrder(
                    id=r["id"],
                    customer_phone=r["customer_phone"],
                    customer_name=r["customer_name"],
                    product_sku=r["product_sku"],
                    quantity=r["quantity"],
                    product_price=float(r["product_price"]),
                    destination_address=r["destination_address"],
                    status=OrderStatus(r["status"]),
                    created_at=r["created_at"],
                    expires_at=r["expires_at"],
                )
                for r in rows
            ]

    async def get_recent_orders_by_phone(
        self, customer_phone: str, limit: int = 3
    ) -> List[ReservationOrder]:
        await self.init_db()
        clean_phone = "".join(filter(str.isdigit, customer_phone))
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM orders WHERE customer_phone = $1 ORDER BY created_at DESC LIMIT $2",
                clean_phone,
                limit,
            )
            return [
                ReservationOrder(
                    id=r["id"],
                    customer_phone=r["customer_phone"],
                    customer_name=r["customer_name"],
                    product_sku=r["product_sku"],
                    quantity=r["quantity"],
                    product_price=float(r["product_price"]),
                    destination_address=r["destination_address"],
                    status=OrderStatus(r["status"]),
                    created_at=r["created_at"],
                    expires_at=r["expires_at"],
                )
                for r in rows
            ]

    async def record_sent_message(self, message_id: str) -> None:
        if not message_id:
            return
        await self.init_db()
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO sent_messages (message_id, sent_at) VALUES ($1, $2) ON CONFLICT (message_id) DO NOTHING",
                message_id,
                datetime.now(timezone.utc),
            )

    async def is_sent_by_bot(self, message_id: str) -> bool:
        if not message_id:
            return False
        await self.init_db()
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            val = await conn.fetchval(
                "SELECT 1 FROM sent_messages WHERE message_id = $1", message_id
            )
            return val is not None

    async def delete_old_sent_messages(self, max_age_hours: int = 24) -> None:
        await self.init_db()
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM sent_messages WHERE sent_at < $1", cutoff)

    async def record_quote_log(
        self, phone: str, query: str, sku: Optional[str] = None, had_stock: bool = True
    ) -> None:
        await self.init_db()
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO quote_logs (customer_phone, query_text, target_sku, had_stock, timestamp)
                VALUES ($1, $2, $3, $4, $5)
                """,
                phone,
                query,
                sku,
                had_stock,
                datetime.now(timezone.utc),
            )

    async def get_global_ai_status(self) -> bool:
        await self.init_db()
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            val = await conn.fetchval(
                "SELECT value FROM system_settings WHERE key = 'global_ai_enabled'"
            )
            return val != "0"

    async def set_global_ai_status(self, enabled: bool) -> None:
        await self.init_db()
        val = "1" if enabled else "0"
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO system_settings (key, value) VALUES ('global_ai_enabled', $1)
                ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
                """,
                val,
            )

    async def get_store_profile(self, store_id: str = "default") -> StoreProfile:
        await self.init_db()
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM store_profile WHERE store_id = $1", store_id
            )
            if row:
                return StoreProfile(
                    store_id=row["store_id"],
                    store_name=row["store_name"],
                    city=row["city"],
                    niche_description=row["niche_description"],
                    out_of_scope_keywords=[
                        k.strip().lower()
                        for k in row["out_of_scope_keywords"].split(",")
                        if k.strip()
                    ],
                    rejection_message=row["rejection_message"],
                    delivery_methods=[
                        d.strip() for d in row["delivery_methods"].split(",") if d.strip()
                    ],
                    tone_guidelines=row["tone_guidelines"],
                    updated_at=row["updated_at"],
                )
            default_profile = StoreProfile(store_id=store_id)
            await self.save_store_profile(default_profile)
            return default_profile

    async def save_store_profile(self, profile: StoreProfile) -> None:
        await self.init_db()
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO store_profile (
                    store_id, store_name, city, niche_description,
                    out_of_scope_keywords, rejection_message, delivery_methods,
                    tone_guidelines, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (store_id) DO UPDATE SET
                    store_name = EXCLUDED.store_name,
                    city = EXCLUDED.city,
                    niche_description = EXCLUDED.niche_description,
                    out_of_scope_keywords = EXCLUDED.out_of_scope_keywords,
                    rejection_message = EXCLUDED.rejection_message,
                    delivery_methods = EXCLUDED.delivery_methods,
                    tone_guidelines = EXCLUDED.tone_guidelines,
                    updated_at = EXCLUDED.updated_at
                """,
                profile.store_id,
                profile.store_name,
                profile.city,
                profile.niche_description,
                ", ".join(profile.out_of_scope_keywords),
                profile.rejection_message,
                ", ".join(profile.delivery_methods),
                profile.tone_guidelines,
                profile.updated_at,
            )

    async def record_audit_log(self, entry: AuditLogEntry) -> None:
        await self.init_db()
        pool = await self._get_pool()
        details_json = json.dumps(entry.details or {}, ensure_ascii=False)
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO audit_logs (
                    id, timestamp, level, component, action, actor, details, duration_ms, status
                ) VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, $8, $9)
                """,
                entry.id,
                entry.timestamp,
                entry.level,
                entry.component,
                entry.action,
                entry.actor,
                details_json,
                entry.duration_ms,
                entry.status,
            )

    async def list_audit_logs(
        self,
        limit: int = 100,
        level: Optional[str] = None,
        component: Optional[str] = None,
    ) -> List[AuditLogEntry]:
        await self.init_db()
        pool = await self._get_pool()
        query = "SELECT * FROM audit_logs WHERE 1=1"
        args: list[object] = []
        idx = 1
        if level:
            query += f" AND level = ${idx}"
            args.append(level.upper())
            idx += 1
        if component:
            query += f" AND component = ${idx}"
            args.append(component.upper())
            idx += 1
        query += f" ORDER BY timestamp DESC LIMIT ${idx}"
        args.append(limit)

        async with pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            logs = []
            for r in rows:
                det = json.loads(r["details"]) if isinstance(r["details"], str) else (r["details"] or {})
                logs.append(
                    AuditLogEntry(
                        id=r["id"],
                        timestamp=r["timestamp"],
                        level=r["level"],
                        component=r["component"],
                        action=r["action"],
                        actor=r["actor"],
                        details=det,
                        duration_ms=r["duration_ms"],
                        status=r["status"],
                    )
                )
            return logs
