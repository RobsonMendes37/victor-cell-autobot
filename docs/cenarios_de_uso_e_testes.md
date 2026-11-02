# Guia Visual de Cenários de Uso, Operação e Testes Automatizados

**Sistema:** PecasBot Enterprise — Assistente Autônomo de Atendimento, Cotação e Despacho via WhatsApp  
**Versão:** 2.2.0  
**Data:** 02 de Novembro de 2026  

---

## 1. Visão Geral dos Cenários de Operação

| # | Cenário Operacional | Entrada do Cliente | Comportamento do Bot | Ação nos Bastidores da Loja |
| :-: | :--- | :--- | :--- | :--- |
| **1** | **Cotação de Peça de Tablet** | "Quanto tá a tela do Tab A8?" | Resposta ultra-curta (1-6 palavras): `"Tela R$ 140 / Conector R$ 25"` | Registra SKU ativa na sessão |
| **2** | **Rejeição Fora de Escopo** | "Amigo, tem tela de iPhone 11?" | Rejeição direta e polida: `"Só peças de tablet"` | Zero enrolação, foco 100% em tablets |
| **3** | **Pedido Pendente (Endereço)** | "Separa pro Uber, Rua Barão do Rio Branco 1102" | Pergunta de confirmação: `"Confirma o envio pro endereço informado?"` | Pré-anota endereço no estado `WAITING_CONFIRMATION` |
| **4** | **Confirmação Explícita de Envio** | "Sim, pode mandar!" | Confirmação e aviso: `"Separando a tela. Aguarde o Uber."` | Cria Pedido, baixa estoque e dispara alerta no celular da equipe |
| **5** | **Retirada no Balcão Físico** | "Vou passar aí no balcão pra buscar" | Confirmação de separação de balcão | Dispara alerta para separar na bancada de saída |
| **6** | **Transbordo Silencioso (Handoff)** | "Faz por 100 no Pix agora?" ou foto duvidosa | **Totalmente Silencioso:** Bot NÃO responde nada ao cliente | Alerta urgente via ntfy no celular da equipe para assumir |
| **7** | **Intervenção Manual do Dono** | Dono digita no WhatsApp pelo celular | Bot detecta e pausa IA por 3 horas | Controle 100% humano sem conflitos |
| **8** | **Fora do Expediente / Domingo** | Mensagem enviada domingo às 14h | Resposta com aviso de loja fechada e reabertura segunda 08:30 | Não promete entrega com loja fechada |
| **9** | **Painel Executivo & Auditoria** | Gestor abre `/dashboard` no PC ou celular | Painel moderno com gráficos, KPIs e trilha de auditoria | Zero emojis, ícones SVG e logs em tempo real |
| **10** | **Perfil Comercial Whitelabel** | Gestor altera nome ou nicho da loja | Aplica diretrizes em tempo real via `POST /api/system/profile` | Grava evento na auditoria |

---

## 2. Detalhamento dos Cenários de Bancada

### Cenário 1: Cotação Simples de Peça
O técnico está na bancada com o aparelho do cliente e quer saber se a loja tem a peça e qual o valor.

```text
[TÉCNICO] ➔ "Quanto tá a frontal do Tab A8?"
   │
   ▼
[BOT PECASBOT] ➔ "Tela R$ 140 / Conector R$ 25"
   │
   ▼
[BASTIDORES] ➔ O sistema registra o SKU "TEL-SAM-A8" na conversa e grava log de cotação.
```

---

### Cenário 2: Pergunta sobre Smartphone / iPhone (Fora de Escopo)
O cliente pergunta sobre uma peça que a loja não comercializa.

```text
[CLIENTE] ➔ "Vocês trocam tela de iPhone 13?"
   │
   ▼
[BOT PECASBOT] ➔ "Só peças de tablet"
   │
   ▼
[BASTIDORES] ➔ Resposta instantânea, zero desculpas prolixas, protegendo a equipe de conversas inúteis.
```

---

### Cenário 3: Confirmação de Pedido em Duas Fases (Two-Phase Commit)
Evita que corridas de Uber Flash sejam solicitadas por engano quando o cliente apenas informa um endereço de forma hipotética.

```text
[CLIENTE] ➔ "Separa a tela pro Uber, Rua Barão do Rio Branco 1102"
   │
   ▼
[BOT PECASBOT] ➔ "Confirma o envio pro endereço informado?"
   │
   ▼
[CLIENTE] ➔ "Sim, pode mandar o Uber!"
   │
   ▼
[BOT PECASBOT] ➔ "Separando a tela. Aguarde o Uber."
   │
   ▼
[BASTIDORES] ➔ Pedido #ORD-xxx gravado no banco relacional.
               Estoque decrementado em 1 unidade.
               Alerta sonoro de alta prioridade emitido no celular da equipe via ntfy.sh.
```

---

### Cenário 4: Transbordo Silencioso para Atendimento Humano
Quando o cliente pede desconto, negocia valores ou envia foto que gera incerteza técnica.

```text
[CLIENTE] ➔ "Amigo, faz por 110 à vista no Pix que eu busco agora?"
   │
   ▼
[BOT PECASBOT] ➔ (Silêncio Absoluto - Nenhuma mensagem é enviada ao cliente)
   │
   ▼
[CELULAR DA EQUIPE] ➔ Notificação sonora imediata:
                       "⚠️ ATENDIMENTO HUMANO REQUISITADO"
                       "Cliente: Carlos (85 99999-1234) - Motivo: Negociação de Preço"
                       "A IA não respondeu. Assuma diretamente no WhatsApp!"
```

---

## 3. Matriz da Suíte de Testes Automatizados (89 Testes / 100% Aprovados)

O sistema possui uma suíte completa de testes automatizados garantindo que nenhuma regressão ocorra:

| Arquivo de Teste | Quantidade | Escopo Validado |
| :--- | :---: | :--- |
| `tests/test_domain.py` | 6 | Entidades puras, regras de garantia, estados de conversa e horários comerciais. |
| `tests/test_domain_extended.py` | 5 | Casos de borda de agendamento de domingo e expiração de reservas. |
| `tests/test_agent_service_deep.py` | 8 | Extração de endereços reais, fallbacks semânticos, cotação e handoff. |
| `tests/test_evolution_gateway.py` | 5 | Envio de mensagens, gravação de mensagens enviadas, alertas ntfy e áudio/imagem base64. |
| `tests/test_sqlite_repository_deep.py` | 8 | Persistência de sessões, ciclo de vida de pedidos, disjuntor global e anti-loop. |
| `tests/test_inventory_adapters_deep.py` | 8 | Circuit breaker do Bling ERP, webhook de saldo, rate limiting e resiliência de cache. |
| `tests/test_inventory_pluggable.py` | 4 | Resolução de factory de inventário e proxy de leitura transparente. |
| `tests/test_google_sheets_repository_deep.py` | 2 | Parser de linhas de planilha e integração Google Sheets API. |
| `tests/test_debounce_buffer_deep.py` | 1 | Agregação assíncrona de rajadas de mensagens no WhatsApp em janela de 3 segundos. |
| `tests/test_api_endpoints.py` | 27 | Autenticação HMAC, sessões, relatórios de conversão, filtros de analytics e webhooks. |
| `tests/test_use_cases.py` | 7 | Orquestração ponta a ponta do `ProcessIncomingMessageUseCase`, pós-venda e handoff. |
| `tests/test_audit_and_enterprise_features.py` | 8 | Multi-tenancy (`StoreProfile`), Trilha de Auditoria, Notificador Multi-Canal e Postgres. |
| **Total** | **89** | **100% de Aprovação em 49.40s** |

---

## 4. Como Executar a Suíte de Qualidade

```bash
# Executa o Quality Gate completo (Ruff Lint + Mypy Typecheck + Pytest 89 testes + Hot Backup)
./scripts/quality_gate.sh

# Ou via Makefile
make check
```
