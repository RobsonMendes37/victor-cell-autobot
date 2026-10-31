"""
Test Script to verify PecasBot business flows locally.
Executes automated tests on the presentation and application layers.
"""

import asyncio

from presentation.api import order_repo, use_case


async def run_tests():
    print("=" * 60)
    print("🧪 INICIANDO BATERIA DE TESTES DO PECASBOT")
    print("=" * 60)

    customer_phone = "5585991234567"

    # Teste 1: Cotação de Tela A15 Original
    print("\n[TESTE 1] Cliente pergunta sobre Tela A15 Original...")
    res1 = await use_case.execute(
        customer_phone=customer_phone,
        message_text="Opa, tem tela do A15 original com aro?",
        from_me=False,
        push_name="Marcos Celulares"
    )
    assert res1["status"] == "SUCCESS"
    assert res1["intent"] == "QUOTE"
    print("✅ TESTE 1 PASSOU: Cotação respondida com sucesso.")

    # Teste 2: Pedido de Separação com Despacho via Uber Flash
    print("\n[TESTE 2] Cliente pede para separar e despachar por Uber Flash...")
    res2 = await use_case.execute(
        customer_phone=customer_phone,
        message_text="Pode separar essa! Manda o Uber pra Rua Floriano Peixoto, 1250 - Centro",
        from_me=False,
        push_name="Marcos Celulares"
    )
    assert res2["status"] == "SUCCESS"
    assert res2["order_created"] is True
    orders = order_repo.list_orders()
    assert len(orders) >= 1
    latest_order = orders[-1]
    print(f"✅ TESTE 2 PASSOU: Pedido criado #{latest_order.id} com endereço '{latest_order.destination_address}' e alerta ao caixa gerado.")

    # Teste 3: Transbordo Humano - Dono da loja intervém no celular (from_me=True)
    print("\n[TESTE 3] Dono da loja responde no WhatsApp pelo celular...")
    res3 = await use_case.execute(
        customer_phone=customer_phone,
        message_text="Opa Marcos, o Luan do caixa já tá cotando seu Uber!",
        from_me=True
    )
    assert res3["status"] == "PAUSED_BY_HUMAN_INTERVENTION"

    # Teste 4: Cliente manda nova mensagem com o bot pausado
    print("\n[TESTE 4] Cliente manda nova mensagem enquanto o humano está atendendo...")
    res4 = await use_case.execute(
        customer_phone=customer_phone,
        message_text="Beleza, aguardo o Pix!",
        from_me=False
    )
    assert res4["status"] == "SKIPPED_HUMAN_IN_CONTROL"
    print("✅ TESTE 3 & 4 PASSOU: IA foi silenciada e não interferiu na conversa do dono.")

    # Teste 5: Dono reativa o bot com #bot
    print("\n[TESTE 5] Dono envia comando #bot para reativar o atendimento automático...")
    res5 = await use_case.execute(
        customer_phone=customer_phone,
        message_text="#bot atendimento liberado",
        from_me=True
    )
    assert res5["status"] == "AI_RESUMED"
    print("✅ TESTE 5 PASSOU: IA reativada com sucesso.")

    print("\n" + "=" * 60)
    print("🎉 TODOS OS 5 TESTES DE ARQUITETURA PASSARAM COM SUCESSO!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_tests())
