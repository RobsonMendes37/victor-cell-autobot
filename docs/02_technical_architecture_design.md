		

# RFC-002: Documento de Arquitetura de Software & Design Técnico

## Arquitetura Limpa, Entidades de Domínio e Fluxo de Integração

---

## 1. Visão Arquitetural em Camadas (Clean Architecture)

Para atender ao requisito de engenharia profissional e desacoplamento, a aplicação adota os princípios de **Clean Architecture** e **Domain-Driven Design (DDD)**. Nenhuma regra de negócio depende de frameworks web (FastAPI) ou de provedores externos (Google Sheets ou Evolution API).

```
┌──────────────────────────────────────────────────────────────────┐
│                   1. INFRASTRUCTURE LAYER                         │
│  • Evolution API Client        • Gemini Multimodal (Circuit Breaker)│
│  • Bling ERP v3 / Memory / DB  • SQLite/Postgres Async Repo      │
│  • Multi-Channel StaffNotifier • Sliding Window Rate Limiter     │
│  • Prometheus Metrics Exporter • System Clock & Scheduler (UTC-3)│
└─────────────────────────────────┬────────────────────────────────┘
                                  │ implements interfaces
┌─────────────────────────────────▼────────────────────────────────┐
│                    2. APPLICATION LAYER                          │
│  • ProcessIncomingMessageUseCase                                 │
│  • RequestProductSeparationUseCase                               │
│  • TriggerHumanHandoffUseCase                                    │
│  • MessageDebounceBufferService                                  │
└─────────────────────────────────┬────────────────────────────────┘
                                  │ orchestrates
┌─────────────────────────────────▼────────────────────────────────┐
│                      3. DOMAIN LAYER                             │
│  • Entities: Customer, Conversation, Message, Product, Order     │
│  • Value Objects: PhoneNumber, Price, QualityTier, State         │
│  • Interfaces: ProductRepositoryInterface, MessagingGateway      │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. Modelagem das Entidades de Domínio

### 2.1 Diagrama de Classes e Relacionamentos

```mermaid
classDiagram
    class Customer {
        +String phone_id
        +String name
        +CustomerRole role
        +DateTime created_at
    }

    class Conversation {
        +UUID id
        +String customer_phone
        +ConversationState state
        +DateTime last_activity_at
        +DateTime human_resumed_at
        +is_ai_allowed() bool
        +pause_for_human(hours: int)
        +resume_ai()
    }

    class Message {
        +String id
        +UUID conversation_id
        +MessageDirection direction
        +AuthorType author_type
        +MediaType media_type
        +String content
        +DateTime timestamp
    }

    class Product {
        +String sku
        +String name
        +List~String~ compatible_models
        +QualityTier quality
        +Decimal price
        +int stock_quantity
        +DateTime last_updated_at
        +bool is_in_stock()
    }

    class ReservationOrder {
        +UUID id
        +String customer_phone
        +String product_sku
        +String destination_address
        +OrderStatus status
        +DateTime created_at
    }

    Customer "1" -- "*" Conversation : participates_in
    Conversation "1" -- "*" Message : contains
    Product "1" -- "*" ReservationOrder : reserved_in
```

### 2.2 Máquina de Estados da Conversa (`ConversationState`)

```mermaid
stateDiagram-v2
    [*] --> AI_ACTIVE: Nova mensagem recebida
    AI_ACTIVE --> AI_ACTIVE: Atendimento normal e cotações
    AI_ACTIVE --> WAITING_DISPATCH: Cliente confirmou pedido e passou endereço
    WAITING_DISPATCH --> AI_ACTIVE: Caixa confirmou envio de Uber
  
    AI_ACTIVE --> HUMAN_ACTIVE: Dono/Atendente respondeu no WhatsApp (fromMe=true)
    AI_ACTIVE --> HUMAN_ACTIVE: Cliente solicitou atendimento humano ou negociação
    HUMAN_ACTIVE --> AI_ACTIVE: Timeout de 3 horas sem interação manual OU comando #bot
  
    AI_ACTIVE --> CLOSED: Inatividade prolongada (24h)
    HUMAN_ACTIVE --> CLOSED: Atendimento finalizado
```

---

## 3. Diagrama de Sequência: Ciclo de Vida da Mensagem

O diagrama abaixo detalha o caminho percorrido por um áudio enviado por um técnico solicitando cotação e posterior despacho com o Uber:

```mermaid
sequenceDiagram
    autonumber
    actor Cliente as Técnico Parceiro
    participant Evo as Evolution API (WA Gateway)
    participant Buffer as Debounce Buffer (FastAPI)
    participant Core as ProcessMessageUseCase
    participant Gemini as Gemini Multimodal API
    participant Cache as ProductRepo (Sheets Cache)
    participant Caixa as Grupo do Caixa/Expedição

    Cliente->>Evo: Envia Áudio ("Tem tela do A15 original?")
    Evo->>Buffer: Webhook POST (Audio URL + metadata)
    Note over Buffer: Aguarda 6 segundos por mensagens sequenciais
    Buffer->>Core: Dispara lote de mensagens agregadas
    Core->>Gemini: Transcreve áudio + Extrai intenção (MODEL=A15, TIER=ORIGINAL, INTENT=QUOTE)
    Gemini-->>Core: Retorna Intenção estruturada em JSON
    Core->>Cache: find_by_model("Galaxy A15", QualityTier.ORIGINAL)
    Cache-->>Core: Retorna Product(SKU="TEL-A15-ORIG", Preço=190.00, Estoque=4)
    Core->>Gemini: Gera resposta humanizada com tom de balcão
    Gemini-->>Core: "Temos sim, patrão! Original tá R$ 190. Quer que separe?"
    Core->>Evo: Envia resposta para o WhatsApp do Cliente
    Evo-->>Cliente: Mensagem entregue no chat

    opt Cliente decide comprar e mandar Uber
        Cliente->>Evo: "Pode separar! Manda o Uber pra Rua Floriano, 1250"
        Evo->>Buffer: Webhook POST
        Buffer->>Core: Processa intenção (INTENT=ORDER_DISPATCH)
        Core->>Caixa: Dispara Alerta com Endereço e Peça Reservada
        Core->>Evo: Responde ao cliente orientando sobre cotação do Uber
        Evo-->>Cliente: "Fechado! Meninos do caixa já estão cotando o Uber..."
    end
```

---

## 4. Padrões de Resiliência e Desempenho

### 4.1 Estratégia de Cache de Alta Performance (Google Sheets)

Para contornar o limite de 60 requisições/minuto da API do Google Drive/Sheets:

* **In-Memory Cache (com TTL de 3 minutos):** O backend realiza uma leitura periódica do catálogo completo para a memória RAM (dicionário indexado por palavras-chave e SKUs).
* **Busca Local em Milissegundos:** As buscas de produtos feitas pelo Gemini utilizam o catálogo já carregado na memória, resultando em respostas com latência inferior a 30ms.
* **Escrita Assíncrona:** Apenas inclusões de novos pedidos e logs de auditoria disparam chamadas de escrita direta na planilha, enfileiradas de forma assíncrona (`BackgroundTasks` do FastAPI).

### 4.2 Detecção e Transbordo Transparente

A Evolution API envia eventos para o webhook tanto de mensagens recebidas quanto de mensagens enviadas.

* Quando o payload traz `"key": { "fromMe": true }`, o sistema reconhece que um operador humano usou o WhatsApp Web ou o aparelho físico da loja.
* O use case `HandleHumanInterventionUseCase` é executado, atualizando a entidade `Conversation` para `state = ConversationState.HUMAN_ACTIVE` e definindo `human_resumed_at = now()`.
* Nenhuma resposta automatizada é gerada enquanto a conversa permanecer nesse estado, garantindo que a IA nunca interfira na conversa do dono.

---

## 5. Padrões Avançados de Resiliência, Integridade e Governança

### 5.1 Circuit Breaker para Provedor de IA (Google Gemini)
Para proteger a esteira de atendimento contra picos de latência, indisponibilidade temporária na nuvem ou códigos `HTTP 429 Too Many Requests`:
* **Máquina de Estados:** `CLOSED` (operação normal), `OPEN` (interrompe chamadas ao Gemini e aciona fallback imediato com aviso cordial), `HALF_OPEN` (sondagem de recuperação).
* **Thresholds:** Abre após 3 falhas consecutivas e realiza sondagem após 30 segundos.

### 5.2 Busca Fuzzy Resiliente e Normalização de Codinomes de Fábrica
* **Levenshtein Puro:** Distância de edição sem dependências externas compiladas em C, garantindo portabilidade absoluta.
* **Tolerância a Gírias:** Mapeamento de codinomes (`t220`, `t295`, `x205`, `nb304`) para modelos comerciais Samsung e Multilaser.
* **Matriz de Discriminação:** Penalização semântica para evitar entregar display quando o cliente solicitou apenas o touch.

### 5.3 Guarda Atômica Anti-Overbooking
A dedução de estoque ocorre antes de salvar a ordem:
* Operação atômica em nível de repositório (`decrement_stock`).
* Se saldo insuficiente, o pedido é abortado com aviso ao cliente ("peça acabou de esgotar") e evento `OVERBOOKING_BLOCKED` persistido na auditoria.

### 5.4 Governança de Mudança de Preço (`PRICE_CHANGED`)
* **Sincronização Ativa:** Webhook `POST /webhook/erp/stock` atualiza catálogo e registra log imutável de alteração de preço.
* **Proteção Comercial:** Cotação sempre reflete o milissegundo atual. Em caso de contestação de valor pelo cliente, a IA é silenciada e aciona `HUMAN_HANDOFF` imediato com notificação prioritária no WhatsApp do atendente humano.

### 5.5 Governança de Pix (Transbordo Humano Silencioso)
* O bot **nunca** responde chave Pix automaticamente. Toda menção ou pergunta sobre Pix aciona transbordo silencioso para o caixa humano.
