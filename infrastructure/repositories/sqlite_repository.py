"""
SQLite Asynchronous Repository using aiosqlite with WAL mode enabled.
Persists Conversations, Orders, Messages (history), and Sent Message IDs.
"""

import os
from datetime import datetime, timezone, timedelta
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



def _format_relative_time(timestamp_iso: str, now: datetime) -> str:
    try:
        dt = datetime.fromisoformat(timestamp_iso)
        diff = now - dt
        seconds = diff.total_seconds()
        if seconds < 120:
            return "Agora"
        minutes = int(seconds // 60)
        if minutes < 60:
            return f"Há {minutes} min"
        hours = int(minutes // 60)
        if hours < 24:
            return f"Há {hours}h atrás"
        days = int(hours // 24)
        if days == 1:
            return "Ontem"
        return f"Há {days} dias"
    except Exception:
        return "Anteriormente"

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
                    customer_name TEXT,
                    state TEXT NOT NULL,
                    last_activity_at TEXT NOT NULL,
                    human_resumed_at TEXT,
                    human_silence_duration_hours INTEGER DEFAULT 3,
                    active_sku TEXT,
                    notes TEXT
                )
            """)
            try:
                await db.execute("ALTER TABLE conversations ADD COLUMN customer_name TEXT;")
            except Exception:
                pass

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

            # 5. Tabela de Cache Local do Catálogo (Resiliência Offline)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS cached_products (
                    sku TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    compatible_models TEXT NOT NULL,
                    quality TEXT NOT NULL,
                    has_frame INTEGER NOT NULL,
                    price REAL NOT NULL,
                    stock_quantity INTEGER NOT NULL,
                    warranty_days INTEGER DEFAULT 90,
                    has_stock INTEGER DEFAULT 1,
                    updated_at TEXT NOT NULL
                )
            """)

            # 6. Tabela de Inteligência Comercial e Demanda (Cotações de Clientes)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS quote_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_phone TEXT NOT NULL,
                    query_text TEXT NOT NULL,
                    target_sku TEXT,
                    had_stock INTEGER DEFAULT 1,
                    timestamp TEXT NOT NULL
                )
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_quote_logs_sku ON quote_logs(target_sku, timestamp);
            """)
                        # 7. Tabela de Configurações Globais do Sistema (Disjuntor Geral da IA)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS system_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            await db.execute("""
                INSERT OR IGNORE INTO system_settings (key, value) VALUES ('global_ai_enabled', '1');
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
                cust_name = row["customer_name"] if "customer_name" in row.keys() else None
                return Conversation(
                    id=row["id"],
                    customer_phone=row["customer_phone"],
                    customer_name=cust_name,
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
                    customer_phone, id, customer_name, state, last_activity_at,
                    human_resumed_at, human_silence_duration_hours, active_sku, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(customer_phone) DO UPDATE SET
                    customer_name = COALESCE(excluded.customer_name, conversations.customer_name),
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
                    conversation.customer_name,
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
        self, customer_phone: str, limit: int = 15, max_age_hours: int = 48
    ) -> List[Dict[str, str]]:
        """
        Recupera histórico recente com âncoras temporais relativas
        dentro da janela deslizante (padrão 48 horas, até 15 mensagens).
        """
        clean_phone = "".join(filter(str.isdigit, customer_phone))
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=max_age_hours)
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT role, content, timestamp FROM messages
                WHERE customer_phone = ? AND timestamp >= ?
                ORDER BY id DESC LIMIT ?
            """,
                (clean_phone, cutoff.isoformat(), limit),
            )
            rows = await cursor.fetchall()
            messages = []
            for r in reversed(rows):
                time_str = _format_relative_time(r["timestamp"], now)
                messages.append({
                    "role": r["role"],
                    "content": f"[{time_str}] {r['content']}",
                    "raw_content": r["content"],
                    "timestamp": r["timestamp"],
                })
            return messages

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

    async def get_recent_orders_by_phone(
        self, customer_phone: str, limit: int = 3
    ) -> List[ReservationOrder]:
        """Recupera os pedidos mais recentes deste número para contextualizar pós-venda/rastreio."""
        clean_phone = "".join(filter(str.isdigit, customer_phone))
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT * FROM orders
                WHERE customer_phone = ?
                ORDER BY created_at DESC LIMIT ?
            """,
                (clean_phone, limit),
            )
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

    async def list_conversations(self, limit: int = 30) -> List[Conversation]:
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM conversations ORDER BY last_activity_at DESC LIMIT ?",
                (limit,),
            )
            rows = await cursor.fetchall()
            conversations = []
            for row in rows:
                human_resumed_at = (
                    datetime.fromisoformat(row["human_resumed_at"])
                    if row["human_resumed_at"]
                    else None
                )
                cust_name = row["customer_name"] if "customer_name" in row.keys() else None
                conversations.append(
                    Conversation(
                        id=row["id"],
                        customer_phone=row["customer_phone"],
                        customer_name=cust_name,
                        state=ConversationState(row["state"]),
                        last_activity_at=datetime.fromisoformat(row["last_activity_at"]),
                        human_resumed_at=human_resumed_at,
                        human_silence_duration_hours=row["human_silence_duration_hours"],
                        active_sku=row["active_sku"],
                        notes=row["notes"],
                    )
                )
            return conversations

    async def cache_products(self, products: list) -> None:
        """Salva uma cópia do catálogo do Google Sheets no SQLite para resiliência offline."""
        await self.init_db()
        from datetime import datetime, timezone
        now_str = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            for p in products:
                models_str = ", ".join(p.compatible_models) if hasattr(p, "compatible_models") else ""
                q_val = p.quality.value if hasattr(p.quality, "value") else str(p.quality)
                await db.execute(
                    """
                    INSERT OR REPLACE INTO cached_products (
                        sku, name, category, compatible_models, quality, has_frame, price, stock_quantity, warranty_days, has_stock, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        p.sku,
                        p.name,
                        p.category,
                        models_str,
                        q_val,
                        1 if p.has_frame else 0,
                        float(p.price),
                        int(p.stock_quantity),
                        int(p.warranty_days),
                        1 if getattr(p, "has_stock", True) else 0,
                        now_str,
                    ),
                )
            await db.commit()

    async def get_cached_products(self) -> list:
        """Recupera catálogo do cache SQLite caso a API do Google Sheets esteja fora do ar."""
        await self.init_db()
        from domain.entities import Product, QualityTier
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM cached_products ORDER BY category, name")
            rows = await cursor.fetchall()
            products = []
            for r in rows:
                models = [m.strip() for m in r["compatible_models"].split(",") if m.strip()]
                q_val = r["quality"]
                q_enum = QualityTier.ORIGINAL_NACIONAL
                for t in QualityTier:
                    if t.value == q_val:
                        q_enum = t
                        break
                products.append(
                    Product(
                        sku=r["sku"],
                        name=r["name"],
                        category=r["category"],
                        compatible_models=models,
                        quality=q_enum,
                        has_frame=bool(r["has_frame"]),
                        price=float(r["price"]),
                        stock_quantity=int(r["stock_quantity"]),
                        warranty_days=int(r["warranty_days"]), has_stock=bool(r["has_stock"]) if "has_stock" in r.keys() else (int(r["stock_quantity"]) > 0),
                    )
                )
            return products

    async def record_quote_log(self, phone: str, query: str, sku: str = None, had_stock: bool = True) -> None:
        """Registra intenções de compra/cotações para análise de demanda reprimida."""
        await self.init_db()
        from datetime import datetime, timezone
        now_str = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO quote_logs (customer_phone, query_text, target_sku, had_stock, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (phone, query, sku, 1 if had_stock else 0, now_str),
            )
            await db.commit()

    # --- Disjuntor Geral de Emergência da IA (Master Kill Switch) ---

    async def get_global_ai_status(self) -> bool:
        """Retorna True se a IA está ligada globalmente, False se o disjuntor de emergência foi acionado."""
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT value FROM system_settings WHERE key = 'global_ai_enabled'")
            row = await cursor.fetchone()
            if row:
                return row[0] == "1"
            return True

    async def set_global_ai_status(self, enabled: bool) -> None:
        """Liga ou desliga o disjuntor geral da IA para todas as conversas."""
        await self.init_db()
        val = "1" if enabled else "0"
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO system_settings (key, value) VALUES ('global_ai_enabled', ?)",
                (val,)
            )
            await db.commit()
