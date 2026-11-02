# RFC-003: Esquema de Dados, Integrações & Engenharia de Prompts
## Contratos de Dados, Webhooks e Configuração do Gemini

---

## 1. Esquema do Banco de Dados no Google Sheets

A pasta de trabalho no Google Sheets é estruturada em 3 abas independentes, otimizadas para leitura rápida pela API e conexão nativa com o **Power BI** e **Looker Studio**:

### 1.1 Aba: `Estoque_Catalogo` (Fonte de Consulta do Agente)

| Coluna | Nome da Coluna | Tipo | Exemplo | Descrição / Regra |
| :--- | :--- | :--- | :--- | :--- |
| **A** | `sku` | Texto | `TEL-SAM-A15-ORIG` | Código único da peça |
| **B** | `categoria` | Texto | `Tela Frontal` | Tela, Conector, Bateria, Tampa |
| **C** | `marca` | Texto | `Samsung` | Fabricante do aparelho |
| **D** | `modelo_comercial` | Texto | `Galaxy A15 (4G/5G)` | Nome como o técnico fala |
| **E** | `codigos_tecnicos` | Texto | `SM-A155F, SM-A156B` | Códigos gravados no chassi |
| **F** | `tipo_qualidade` | Texto | `Original Nacional` | Original Nacional, 1ª Linha, Paralela Incell |
| **G** | `com_aro` | Booleano | `SIM` | SIM / NÃO |
| **H** | `preco_balcao` | Moeda | `190.00` | Preço de venda praticado |
| **I** | `qtd_estoque` | Inteiro | `4` | Saldo físico disponível |
| **J** | `garantia_dias` | Inteiro | `90` | Período de garantia |
| **K** | `data_ultima_alteracao` | Data/Hora | `2026-10-31 08:30` | Auditoria de atualização de estoque |

---

### 1.2 Aba: `Pedidos_Despacho` (Fila Operacional do Caixa / Uber)

| Coluna | Nome da Coluna | Tipo | Exemplo |
| :--- | :--- | :--- | :--- |
| **A** | `id_pedido` | UUID | `ped_98a72b` |
| **B** | `timestamp` | Data/Hora | `2026-10-31 09:15:22` |
| **C** | `cliente_telefone` | Texto | `5585991234567` |
| **D** | `cliente_nome` | Texto | `Marcos (Oficina do Celular)` |
| **E** | `sku_produto` | Texto | `TEL-SAM-A15-ORIG` |
| **F** | `quantidade` | Inteiro | `1` |
| **G** | `valor_produto` | Moeda | `190.00` |
| **H** | `endereco_entrega` | Texto | `Rua Floriano Peixoto, 1250 - Centro` |
| **I** | `modalidade` | Texto | `UBER_FLASH` |
| **J** | `status_operacional` | Texto | `AGUARDANDO_COTAÇÃO_UBER` |
| **K** | `responsavel_caixa` | Texto | `Luan Balcão` |

---

### 1.3 Aba: `Logs_Atendimentos_BI` (Alimentação do Power BI)

Registra todas as interações do WhatsApp para gerar inteligência de vendas:
* `id_interacao`
* `data`
* `telefone_cliente`
* `termo_buscado` (ex: "tela a15")
* `peca_encontrada` (SIM / NÃO)
* `converteu_em_pedido` (SIM / NÃO)
* `motivo_perda` (Sem estoque / Preço / Desistência / Humano assumiu)

---

## 2. Contratos de Integração: Evolution API

### 2.1 Webhook Recebido (Mensagem de Entrada)
A Evolution API envia um `POST` no endpoint `/webhook/whatsapp` do FastAPI com o seguinte payload resumido:

```json
{
  "event": "messages.upsert",
  "instance": "pecas-loja-01",
  "data": {
    "key": {
      "remoteJid": "5585991234567@s.whatsapp.net",
      "fromMe": false,
      "id": "3EB07A8F82C4"
    },
    "pushName": "Marcos Celulares",
    "messageType": "conversation",
    "message": {
      "conversation": "Opa meu amigo, tem tela do A15 original com aro?"
    },
    "messageTimestamp": 1730376123
  }
}
```

> **Detecção de Áudio:** Se `messageType == "audioMessage"`, o payload traz a chave `base64` ou a URL do arquivo `.ogg` para envio direto à API do Gemini.  
> **Detecção de Mensagem do Dono:** Se `"fromMe": true`, o sistema silencia a IA na hora para aquele `remoteJid`.

### 2.2 Chamada de Envio de Resposta
Para responder ao cliente, o FastAPI realiza um `POST` no endpoint da Evolution API:

```http
POST http://evolution-api:8080/message/sendText/pecas-loja-01
Content-Type: application/json
apikey: sua_chave_secreta_aqui

{
  "number": "5585991234567",
  "text": "Opa Marcos, beleza? Temos sim! A tela do A15 Original com aro tá saindo a R$ 190,00 com 90 dias de garantia. Já quer que eu passe pros meninos do balcão deixarem separadinha pro seu Uber?"
}
```

---

## 3. Engenharia de Prompts & Agente Gemini

### 3.1 Prompt de Sistema (System Instructions)

```text
Você é o atendente de balcão da "Victor Cell" (Fortaleza/CE), especializada exclusivamente em peças de TABLETS.
Seu papel é atender técnicos de bancada e lojistas de forma ultra-rápida, direta e sem rodeios.

DIRETRIZES DE PERSONALIDADE E TOM DE VOZ (DOUTRIÑA DO BALCÃO):
1. RESPOSTAS ULTRA-CURTAS: Limite suas respostas a 1 até 6 palavras para cotações e consultas comuns (ex: "R$ 40", "Original 190 / China 95", "Tem não").
2. ZERO ENTUSIASMO ARTIFICIAL: Proibido saudações longas, "Opa meu amigo", "Show de bola", "Como posso ajudar" ou emojis decorativos.
3. ESCOPO ESTRITO (TABLETS): Não vendemos nem consertamos celulares, iPhones ou notebooks. Responda seco: "Só peças de tablet".
4. REGRA DE OURO DO PIX: O bot NUNCA envia chave Pix nem dados bancários. Dúvidas sobre Pix vão para o operador humano do caixa.
5. DIVERGÊNCIA DE PREÇO OU DESCONTO: O bot não concede descontos nem discute preço antigo. Silencie e transfira para o atendente humano.
6. HORÁRIO E REABERTURA: Se a loja estiver fechada ou for domingo, informe o preço seguido do aviso: "Fechado hoje, abre amanhã 08:30.".

FERRAMENTAS (TOOLS / FUNCTION CALLING):
- `consultar_catalogo(termo_busca, qualidade, com_aro)`: Consulta o estoque e preços em tempo real.
- `registrar_pedido_uber(nome_cliente, telefone, sku, endereco)`: Notifica os funcionários do caixa para cotar o Uber e separar a peça.
- `acionar_atendente_humano(motivo)`: Pausa a IA e transfere quando o cliente solicitar desconto grande ou tratar de garantia.
```

### 3.2 Declaração das Funções (Function Calling / Tools)

```json
[
  {
    "name": "consultar_catalogo",
    "description": "Busca peças no estoque com base no modelo, categoria e procedência.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "termo_modelo": { "type": "STRING", "description": "Ex: Galaxy A15, Tab A8, Moto G22" },
        "qualidade": { "type": "STRING", "enum": ["QUALQUER", "ORIGINAL", "PARALELA_CHINA", "PRIMEIRA_LINHA"] },
        "com_aro": { "type": "BOOLEAN", "description": "True se com aro, False se sem aro" }
      },
      "required": ["termo_modelo"]
    }
  },
  {
    "name": "registrar_pedido_uber",
    "description": "Registra o pedido de separação de peça e aciona a equipe do caixa para cotar o Uber Flash.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "sku": { "type": "STRING", "description": "Código SKU da peça escolhida" },
        "endereco_completo": { "type": "STRING", "description": "Rua, número, bairro e referência do cliente" }
      },
      "required": ["sku", "endereco_completo"]
    }
  }
]
```

---

## 4. Esquema da Tabela de Auditoria Técnica (`audit_logs`)

No SQLite e PostgreSQL, a tabela `audit_logs` armazena trilhas imutáveis de governança técnica:

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | VARCHAR(36) | Chave primária UUID |
| `timestamp` | TIMESTAMP | Data e hora em fuso UTC / Fortaleza |
| `action` | VARCHAR(50) | Ação auditada (`PRICE_CHANGED`, `OVERBOOKING_BLOCKED`, `CIRCUIT_BREAKER_TRIPPED`, `HUMAN_HANDOFF`) |
| `level` | VARCHAR(10) | `INFO`, `WARN`, `ERROR` |
| `component` | VARCHAR(30) | `INVENTORY`, `ORDER`, `AI_ENGINE`, `ROUTER` |
| `actor` | VARCHAR(50) | Telefone do cliente, `SYSTEM` ou `ERP_WEBHOOK` |
| `details` | JSON / TEXT | Dados detalhados (ex: `old_price`, `new_price`, `sku`, `reason`) |
| `status` | VARCHAR(20) | `SUCCESS`, `FAILURE`, `DEGRADED` |
