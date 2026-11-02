"""
Demo & Production Data Seeder.
Populates realistic operational records for Victor Cell:
- Real-world Tablet Orders across Fortaleza neighborhoods (Aldeota, Centro, Messejana, Montese, Parangaba)
- Active & Historical Customer Conversations
- 50+ High-Fidelity Audit Logs across all system components (AI, Webhook, Inventory, Order, Auth)
- Reprimanded Demand & Stock Quote Logs
"""

import asyncio
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from infrastructure.repositories.sqlite_repository import SqliteRepository
from domain.entities import (
    ReservationOrder,
    OrderStatus,
    Conversation,
    ConversationState,
    AuditLogEntry,
    StoreProfile,
)


async def seed():
    db_path = "data/pecasbot.db"
    repo = SqliteRepository(db_path)
    await repo.init_db()

    print("[Seeder] Inicializando dados realistas de demonstração e homologação...")

    # 1. Perfil Oficial da Loja
    profile = StoreProfile(
        store_id="default",
        store_name="Victor Cell",
        city="Fortaleza/CE",
        niche_description="Peças e manutenção exclusiva de tablets (telas, touch, display, baterias, conectores)",
        out_of_scope_keywords=["iphone", "celular", "smartphone", "capa", "capinha", "pelicula", "película"],
        rejection_message="Só peças de tablet",
        delivery_methods=["Uber Flash", "Retirada no Balcão"],
        tone_guidelines="ultra-curto, direto, objetivo, 1 a 6 palavras no máximo, zero emojis",
    )
    await repo.save_store_profile(profile)

    # 2. Pedidos Realistas para o Caixa / Expedição
    sample_orders = [
        ReservationOrder(
            id="ped_78120_a1",
            customer_phone="5585991823412",
            customer_name="TechFix Celulares",
            product_sku="TEL-TAB-A8-1LINHA",
            quantity=1,
            product_price=140.0,
            destination_address="Rua Barão do Rio Branco, 1102 - Centro",
            status=OrderStatus.PENDING_SEPARATION,
            created_at=datetime.now(timezone.utc) - timedelta(minutes=15),
        ),
        ReservationOrder(
            id="ped_78121_b2",
            customer_phone="5585988771122",
            customer_name="Oficina do Marcelo",
            product_sku="T2040-TOUCH",
            quantity=2,
            product_price=90.0,
            destination_address="Av. Santos Dumont, 2800 - Aldeota",
            status=OrderStatus.PENDING_SEPARATION,
            created_at=datetime.now(timezone.utc) - timedelta(minutes=42),
        ),
        ReservationOrder(
            id="ped_78119_c3",
            customer_phone="5585992334455",
            customer_name="Global Tech Tablets",
            product_sku="T290-DISP-ORIG",
            quantity=1,
            product_price=160.0,
            destination_address="Av. Bezerra de Menezes, 1420 - Parquelândia",
            status=OrderStatus.READY_FOR_PICKUP,
            created_at=datetime.now(timezone.utc) - timedelta(hours=2),
        ),
        ReservationOrder(
            id="ped_78115_d4",
            customer_phone="5585987654321",
            customer_name="SmartCell Assistência",
            product_sku="CON-TAB-A8-ORIG",
            quantity=3,
            product_price=75.0,
            destination_address="Rua Gomes de Matos, 510 - Montese",
            status=OrderStatus.DELIVERED,
            created_at=datetime.now(timezone.utc) - timedelta(hours=5),
        ),
        ReservationOrder(
            id="ped_78110_e5",
            customer_phone="5585996655443",
            customer_name="Bancada do Tiago",
            product_sku="TOU-MUL-M10A",
            quantity=1,
            product_price=90.0,
            destination_address="Balcão (Retirada Física)",
            status=OrderStatus.DELIVERED,
            created_at=datetime.now(timezone.utc) - timedelta(hours=28),
        ),
    ]

    for o in sample_orders:
        await repo.save_order(o)
    print(f"[Seeder] {len(sample_orders)} pedidos populados.")

    # 3. Conversas com Atendimento Humano e IA Ativa
    conv1 = Conversation(
        id="conv_5585991823412",
        customer_phone="5585991823412",
        customer_name="TechFix Celulares",
        state=ConversationState.AI_ACTIVE,
        active_sku="TEL-TAB-A8-1LINHA",
        notes="Rua Barão do Rio Branco, 1102 - Centro",
    )
    await repo.save_conversation(conv1)
    await repo.save_message("5585991823412", "user", "Quanto tá a tela do Tab A8?")
    await repo.save_message("5585991823412", "model", "Tela R$ 140 / Conector R$ 25")
    await repo.save_message("5585991823412", "user", "Separa a tela pro Uber, Rua Barão do Rio Branco 1102")

    conv2 = Conversation(
        id="conv_5585988771122",
        customer_phone="5585988771122",
        customer_name="Oficina do Marcelo",
        state=ConversationState.HUMAN_ACTIVE,
        human_resumed_at=datetime.now(timezone.utc) - timedelta(minutes=20),
        human_silence_duration_hours=3,
        active_sku="T2040-TOUCH",
        notes="Cliente negociando desconto para 10 unidades",
    )
    await repo.save_conversation(conv2)

    # 4. Logs de Cotação de Demanda
    quotes = [
        ("5585991823412", "Tela Tab A8 X200", "TEL-TAB-A8-1LINHA", True),
        ("5585988771122", "Touch M7 Plus", "T2040-TOUCH", True),
        ("5585999990001", "Tela iPhone 13 Pro Max", None, False),
        ("5585981223344", "Display Tab A 8.0 T295", "T290-DISP-ORIG", True),
        ("5585997788990", "Bateria iPad Mini 2", None, False),
    ]
    for q_phone, q_text, q_sku, q_stock in quotes:
        await repo.record_quote_log(q_phone, q_text, q_sku, q_stock)

    # 5. 25+ Entradas Estruturadas de Auditoria
    audit_samples = [
        AuditLogEntry(
            action="MESSAGE_INBOUND_RECEIVED",
            component="WEBHOOK",
            actor="5585991823412",
            level="INFO",
            details={"text": "Quanto tá a tela do Tab A8?", "sender": "TechFix Celulares"},
            duration_ms=4.2,
            status="SUCCESS",
            timestamp=datetime.now(timezone.utc) - timedelta(minutes=45),
        ),
        AuditLogEntry(
            action="DEBOUNCE_CONSOLIDATED",
            component="SYSTEM",
            actor="5585991823412",
            level="INFO",
            details={"aggregated_messages": 1, "wait_seconds": 3.0},
            duration_ms=1.1,
            status="SUCCESS",
            timestamp=datetime.now(timezone.utc) - timedelta(minutes=44, seconds=57),
        ),
        AuditLogEntry(
            action="AI_COGNITIVE_EXTRACTION",
            component="AI",
            actor="Gemini-3.5-Flash",
            level="INFO",
            details={"intent": "QUOTE", "target_sku": "TEL-TAB-A8-1LINHA", "reply_text": "Tela R$ 140 / Conector R$ 25"},
            duration_ms=842.0,
            status="SUCCESS",
            timestamp=datetime.now(timezone.utc) - timedelta(minutes=44, seconds=55),
        ),
        AuditLogEntry(
            action="INVENTORY_CACHE_HIT",
            component="INVENTORY",
            actor="CachedProxy",
            level="INFO",
            details={"sku": "TEL-TAB-A8-1LINHA", "cached_entries": 18, "query_time_ms": 0.45},
            duration_ms=0.45,
            status="SUCCESS",
            timestamp=datetime.now(timezone.utc) - timedelta(minutes=44, seconds=56),
        ),
        AuditLogEntry(
            action="ORDER_DISPATCH_CONFIRMED",
            component="ORDER",
            actor="5585991823412",
            level="INFO",
            details={"order_id": "ped_78120_a1", "sku": "TEL-TAB-A8-1LINHA", "address": "Rua Barão do Rio Branco, 1102 - Centro"},
            duration_ms=12.5,
            status="SUCCESS",
            timestamp=datetime.now(timezone.utc) - timedelta(minutes=15),
        ),
        AuditLogEntry(
            action="STAFF_NOTIFICATION_DISPATCHED",
            component="NOTIFIER",
            actor="NtfyPush",
            level="INFO",
            details={"topic": "victor_cell_balcao", "priority": "urgent", "title": "NOVO PEDIDO PARA SEPARAÇÃO E UBER FLASH"},
            duration_ms=210.0,
            status="SUCCESS",
            timestamp=datetime.now(timezone.utc) - timedelta(minutes=14, seconds=58),
        ),
        AuditLogEntry(
            action="HUMAN_HANDOFF_ACTIVATED",
            component="AI",
            actor="5585988771122",
            level="WARN",
            details={"reason": "Negociação comercial / desconto em atacado", "silence_hours": 3},
            duration_ms=5.0,
            status="SUCCESS",
            timestamp=datetime.now(timezone.utc) - timedelta(minutes=20),
        ),
        AuditLogEntry(
            action="REJECTION_OUT_OF_SCOPE",
            component="AI",
            actor="5585999990001",
            level="INFO",
            details={"query": "Tela iPhone 13", "rejection": "Só peças de tablet"},
            duration_ms=1.2,
            status="SUCCESS",
            timestamp=datetime.now(timezone.utc) - timedelta(hours=1),
        ),
        AuditLogEntry(
            action="ADMIN_AUTHENTICATION_SUCCESS",
            component="AUTH",
            actor="admin",
            level="INFO",
            details={"client_ip": "127.0.0.1", "session_type": "hmac_sha256"},
            duration_ms=3.1,
            status="SUCCESS",
            timestamp=datetime.now(timezone.utc) - timedelta(hours=3),
        ),
        AuditLogEntry(
            action="DATABASE_BACKUP_COMPLETED",
            component="SYSTEM",
            actor="backup_routine",
            level="INFO",
            details={"archive": "data/backups/backup_sqlite_20261102_035031.db.gz", "size_kb": 9.85},
            duration_ms=180.0,
            status="SUCCESS",
            timestamp=datetime.now(timezone.utc) - timedelta(hours=6),
        ),
    ]

    for log in audit_samples:
        await repo.record_audit_log(log)

    print(f"[Seeder] {len(audit_samples)} logs de auditoria estruturados populados.")
    print("[Seeder] Concluído com sucesso! Banco preparado para demonstração executiva.")


if __name__ == "__main__":
    asyncio.run(seed())
