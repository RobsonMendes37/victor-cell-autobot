"""
Interactive Test and Verification Script for Victor Cell PecasBot.
Validates all business flows, anti-loop safeguards, and Power BI CSV export.
"""

import asyncio

from infrastructure.repositories.memory_product_repository import MemoryProductRepository
from infrastructure.repositories.sheets_exporter import SheetsExporter
from presentation.api import sqlite_repo, use_case


async def run_tests():
    print("=" * 65)
    print("🧪 INICIANDO BATERIA DE TESTES - VICTOR CELL PECASBOT")
    print("=" * 65)

    await sqlite_repo.init_db()
    customer_phone = "5585991234567"

    import aiosqlite
    async with aiosqlite.connect(sqlite_repo.db_path) as db:
        await db.execute("DELETE FROM messages WHERE customer_phone IN (?, ?)", (customer_phone, "5585988887777"))
        await db.execute("DELETE FROM conversations WHERE customer_phone IN (?, ?)", (customer_phone, "5585988887777"))
        await db.execute("DELETE FROM orders WHERE customer_phone IN (?, ?)", (customer_phone, "5585988887777"))
        await db.commit()

    # Teste 1: Cotação de Tela A15 Original
    print("\n[TESTE 1] Cliente pergunta sobre Tela A15 Original...")
    res1 = await use_case.execute(
        customer_phone=customer_phone,
        message_text="Opa, tem tela do A15 original com aro?",
        from_me=False,
        push_name="Marcos Celulares",
    )
    assert res1["status"] == "SUCCESS"
    assert res1["intent"] == "QUOTE"
    assert res1["target_sku"] == "TEL-SAM-A15-ORIG"
    print("✅ TESTE 1 PASSOU: Cotação respondida e SKU A15 registrado na sessão.")

    # Teste 2: "Por favor" sem endereço NÃO cria pedido falso com endereço "por favor"
    print("\n[TESTE 2] Cliente diz 'separa por favor' sem passar endereço...")
    res2 = await use_case.execute(
        customer_phone=customer_phone,
        message_text="Separa uma do A15 por favor!",
        from_me=False,
        push_name="Marcos Celulares",
    )
    assert res2["status"] == "SUCCESS"
    assert res2["order_created"] is False, "Não deve criar pedido sem endereço real!"
    print("✅ TESTE 2 PASSOU: 'Por favor' não foi confundido com endereço; bot pediu o endereço.")

    # Teste 3: Pergunta de frete ("quanto fica o Uber?") NÃO cria pedido falso
    print("\n[TESTE 3] Cliente pergunta apenas o valor do Uber...")
    res3 = await use_case.execute(
        customer_phone="5585988887777",
        message_text="Quanto fica o Uber até o centro?",
        from_me=False,
        push_name="Cliente Dúvida",
    )
    assert res3["status"] == "SUCCESS"
    assert res3["intent"] in ["GENERAL_QUESTION", "QUOTE"]
    assert res3["order_created"] is False
    print("✅ TESTE 3 PASSOU: Dúvida sobre Uber explicada sem criar pedido indevido.")

    # Teste 4: Cliente envia endereço real e cria pedido da peça certa (A15)
    print(
        "\n[TESTE 4] Cliente confirma com endereço real: 'Rua Floriano Peixoto, 1250 - Centro'..."
    )
    res4 = await use_case.execute(
        customer_phone=customer_phone,
        message_text="Manda pro endereço Rua Floriano Peixoto, 1250 - Centro",
        from_me=False,
        push_name="Marcos Celulares",
    )
    assert res4["status"] == "SUCCESS"
    assert res4["intent"] == "ORDER_PENDING_CONFIRMATION"
    assert res4["order_created"] is False
    print("✅ TESTE 4 PASSOU: Endereço pré-anotado e bot pediu confirmação explícita.")

    # Teste 4.1: Cliente confirma explicitamente
    print("\n[TESTE 4.1] Cliente confirma: Pode sim, manda ver!...")
    res4 = await use_case.execute(
        customer_phone=customer_phone,
        message_text="Pode sim, pode confirmar!",
        from_me=False,
        push_name="Marcos Celulares",
    )
    assert res4["order_created"] is True
    assert res4["target_sku"] == "TEL-SAM-A15-ORIG"

    orders = await sqlite_repo.list_orders()
    assert len(orders) >= 1
    latest = orders[0]
    assert latest.product_sku == "TEL-SAM-A15-ORIG"
    assert "Floriano Peixoto" in latest.destination_address
    print(
        f"✅ TESTE 4 PASSOU: Pedido #{latest.id} criado com a peça correta (A15 Original - R$ {latest.product_price:.2f})."
    )

    # Teste 5: Eco do próprio bot não silencia a IA
    print("\n[TESTE 5] Webhook recebe eco da própria resposta do bot (fromMe=true)...")
    await sqlite_repo.record_sent_message("bot_msg_echo_01")
    res5 = await use_case.execute(
        customer_phone=customer_phone,
        message_text="Opa, perfeito! Já deixo separada...",
        from_me=True,
        message_id="bot_msg_echo_01",
    )
    assert res5["status"] == "SKIPPED_BOT_ECHO"
    print("✅ TESTE 5 PASSOU: Eco do bot ignorado, IA continua ativa.")

    # Teste 6: Dono da loja responde no WhatsApp pelo celular
    print("\n[TESTE 6] Dono da loja intervém no celular pessoal...")
    res6 = await use_case.execute(
        customer_phone=customer_phone,
        message_text="Opa Marcos, já tô levando a tela pro balcão!",
        from_me=True,
        message_id="human_msg_real_01",
    )
    assert res6["status"] == "PAUSED_BY_HUMAN_INTERVENTION"
    print("✅ TESTE 6 PASSOU: Intervenção humana detectada, IA silenciada.")

    # Teste 7: Reativação com comando #bot
    print("\n[TESTE 7] Dono reativa com #bot...")
    res7 = await use_case.execute(
        customer_phone=customer_phone,
        message_text="#bot atendimento liberado",
        from_me=True,
    )
    assert res7["status"] == "AI_RESUMED"
    print("✅ TESTE 7 PASSOU: IA reativada pelo dono.")

    # Teste 8: Exportação da Planilha para Power BI (Linha 1 Título, Linha 2 Colunas, Linha 3 Dados)
    print("\n[TESTE 8] Exportando catálogo e logs para formato Google Sheets / Power BI...")
    exporter = SheetsExporter(output_dir="data")
    prod_repo = MemoryProductRepository()
    all_products = await prod_repo.list_all()
    cat_path = exporter.export_catalog_csv(all_products)
    log_path = exporter.export_orders_log_csv(orders)

    with open(cat_path, "r", encoding="utf-8-sig") as f:
        lines = [f.readline().strip() for _ in range(3)]
        assert "Victor Cell" in lines[0], "Linha 1 deve ser o Título do Projeto"
        assert "SKU,Produto" in lines[1], "Linha 2 deve ser o cabeçalho das colunas"
        assert "TEL-SAM-A15-ORIG" in lines[2], "Linha 3 deve conter o primeiro registro de dados"

    print(
        f"✅ TESTE 8 PASSOU: Planilhas geradas em {cat_path} e {log_path} seguindo o layout exato para Power BI."
    )

    print("\n" + "=" * 65)
    print("🎉 TODOS OS 8 TESTES PASSARAM COM 100% DE SUCESSO!")
    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(run_tests())
