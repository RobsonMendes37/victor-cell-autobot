# 📱 Victor Cell Autobot — Sistema Autônomo de Vendas, Cotação & Expedição de Peças via WhatsApp

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.13" />
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Google_Gemini-2.0_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google Gemini" />
  <img src="https://img.shields.io/badge/Evolution_API-v2.3.7-25D366?style=for-the-badge&logo=whatsapp&logoColor=white" alt="Evolution API v2" />
  <img src="https://img.shields.io/badge/Bling_ERP-v3_REST-green?style=for-the-badge" alt="Bling ERP v3" />
  <img src="https://img.shields.io/badge/Prometheus-OpenMetrics-E6522C?style=for-the-badge&logo=prometheus&logoColor=white" alt="Prometheus" />
  <img src="https://img.shields.io/badge/Tests-118_Passed-success?style=for-the-badge" alt="Tests 118 Passed" />
  <img src="https://img.shields.io/badge/Clean_Architecture-DDD-purple?style=for-the-badge" alt="Clean Architecture" />
</p>

---

## 📖 Visão Geral Executiva

O **Victor Cell Autobot** é uma plataforma corporativa de inteligência artificial conversacional e automação operacional projetada sob medida para assistências técnicas e distribuidoras de peças de reposição para **tablets** no comércio de balcão físico e digital.

Construído sob os princípios de **Clean Architecture (Arquitetura Limpa)** e **Domain-Driven Design (DDD)**, o sistema integra o motor cognitivo **Google Gemini (2.0 Flash / 1.5 Flash)** ao WhatsApp através da **Evolution API v2**, sincronizando o catálogo com o **Bling ERP v3**, operando com persistência pluggable (**SQLite / PostgreSQL**) e telemetria aberta via **Prometheus**.

---

### 🎯 Principais Diferenciais de Engenharia

* **Cadência de Balcão Ultra-Curta (1 a 6 Palavras):** Respostas secas, diretas e instantâneas (*"R$ 40"*, *"Original 190 / China 95"*, *"Tem não"*, *"Só peças de tablet"*). Elimina saudações robóticas prolixas, menus numéricos e formalidades vazias.
* **Resiliência Extrema com Circuit Breaker:** Disjuntor em três estados (`CLOSED`, `OPEN`, `HALF_OPEN`) que protege as chamadas ao Google Gemini contra instabilidades e erros `HTTP 429 Too Many Requests`, acionando fallback imediato.
* **Busca Fuzzy & Codinomes de Fábrica (Levenshtein Puro):** Algoritmo matemático tolerante a erros de digitação e mapeamento canônico de codinomes de bancada (`t220`, `t295`, `x205`, `nb304`, etc.) sem dependências nativas em C.
* **Guarda Atômica Anti-Overbooking:** Decremento transacional de estoque executado antes da persistência do pedido, garantindo que a última peça física não seja vendida simultaneamente para dois clientes e gerando eventos de auditoria `OVERBOOKING_BLOCKED`.
* **Governança de Mudança de Preço (`PRICE_CHANGED`):** Sincronização em tempo real de preços via Webhook do ERP. Se o cliente contestar o valor cotado anteriormente, o sistema aciona **transbordo silencioso** imediato para negociação humana, sem discussões algorítmicas.
* **Governança Estrita do Fluxo Pix (100% Humano):** O robô é terminantemente proibido de enviar chave Pix ou dados bancários de forma automática. Perguntas sobre Pix transferem o cliente silenciosamente para o atendente do caixa da loja física.
* **Reabertura Inteligente da IA:** Reativação automática do robô pós-intervenção humana se a loja física fechar ou se passarem 30 minutos de inatividade e o cliente enviar uma nova cotação.
* **Cache Rápido de FAQ (<0.05ms):** Respostas instantâneas para endereço e horário de funcionamento em memória RAM local com zero consumo de tokens da cota de IA.
* **Ações Push NTFY com Deep Link no WhatsApp:** Sirene no smartphone da equipe física com botão de 1 toque (`wa.me/{phone}`) para abertura instantânea do chat do cliente.
* **Rate Limiter Anti-DoS (Janela Deslizante):** Proteção contínua limitando requisições a 25 req/min por celular e 30 req/min por IP.
* **Telemetria OpenMetrics / Prometheus:** Endpoint `GET /metrics` com contadores atômicos, latência P95 e status do disjuntor.
* **Quality Gate de Big Tech:** 100% de conformidade com MyPy (tipagem estrita), Ruff (linting), suíte completa de **118 testes automatizados** e rotina de hot backup compactado (`.db.gz`).

---

## 📐 Arquitetura do Sistema

```mermaid
graph TD
    subgraph WhatsApp / Mensageria Externa
        WA[Cliente Técnico no WhatsApp] -->|Mensagem de Texto / Áudio / Foto| EVO[Evolution API v2.3.7]
        EVO -->|POST /webhook| API[Presentation: FastAPI REST]
    end

    subgraph Borda de Segurança & Resiliência
        API --> RL[Sliding Window Rate Limiter]
        RL --> DBF[Debounce Buffer Assíncrono]
    end

    subgraph Core da Aplicação (Clean Architecture)
        DBF --> FAQ[FastFaqCacheService <0.05ms]
        FAQ -->|Dúvida Endereço/Horário| EVO
        DBF --> UC[ProcessIncomingMessageUseCase]
        UC --> CB[Circuit Breaker Gateway]
        CB -->|Normal / CLOSED| GEMINI[Google Gemini 2.0 Flash]
        CB -->|Degradação / OPEN| FALLBACK[Fast Rule Fallback]
        UC --> FUZZY[CatalogSearchService: Levenshtein + Canônicos]
        FUZZY --> INV[InventoryProvider: Bling ERP v3 / Memory / DB]
        UC --> ATOM[Atomic Stock Decrement Guard]
    end

    subgraph Expedição, Notificação & Auditoria
        ATOM -->|Reserva Confirmada| SQL[(SQLite WAL / PostgreSQL)]
        ATOM -->|Ruptura Detectada| AUDIT[Trilha de Auditoria: OVERBOOKING_BLOCKED]
        ATOM -->|Alerta Prioritário| NTFY[ntfy.sh Push: Deep Link wa.me]
        NTFY --> STAFF[Equipe Física do Caixa / Balcão]
        SQL --> DASH[Painel Web Executivo & Exportador CSV]
        API --> PROM[Endpoint Prometheus: GET /metrics]
    end
```

---

## 🗂️ Estrutura do Repositório

```
pecasbot-api/
├── application/
│   └── use_cases/
│       ├── catalog_search_service.py     # Levenshtein puro, codinomes canônicos e penalidades
│       ├── debounce_buffer.py            # Agregador assíncrono de rajadas de mensagens
│       ├── fast_faq_cache.py             # Cache em RAM para endereço/horário (Pix excluído)
│       └── process_incoming_message.py   # Orquestrador central com guarda atômica de estoque
├── domain/
│   ├── entities.py                       # Conversation (reabertura inteligente), Product, Order, StoreProfile
│   ├── gateways.py                       # Interfaces abstratas de Mensageria, IA e Notificadores
│   └── repositories.py                   # Interfaces abstratas de Banco de Dados e Inventário
├── infrastructure/
│   ├── config.py                         # Settings Pydantic, fuso UTC-3 (Fortaleza), limites de taxa
│   ├── gateways/
│   │   └── evolution_gateway.py          # Cliente HTTP da Evolution API v2 com proteção anti-loop
│   ├── inventory/
│   │   ├── bling_v3_adapter.py           # Integração Bling ERP v3 com auto-ingestão via webhook
│   │   ├── cached_proxy.py               # Cache proxy de inventário com TTL e auditoria
│   │   └── memory_adapter.py             # Repositório volátil de alta velocidade para testes
│   ├── notifiers/
│   │   ├── ntfy_channel.py               # Push prioritário com ações wa.me
│   │   └── staff_dispatcher.py           # Despachante multi-canal para a equipe interna
│   ├── repositories/
│   │   ├── db_factory.py                 # Fábrica pluggable de banco (SQLite ou PostgreSQL)
│   │   └── sqlite_repository.py          # Persistência WAL, histórico, pedidos e auditoria
│   └── services/
│       ├── circuit_breaker.py            # Circuit Breaker CLOSED/OPEN/HALF-OPEN para o Gemini
│       ├── metrics_service.py            # Coletor OpenMetrics / Prometheus e latência P95
│       └── rate_limiter.py               # Sliding Window Rate Limiter por telefone e IP
├── presentation/
│   ├── api.py                            # Endpoints FastAPI, Webhook WhatsApp, ERP e /metrics
│   └── dashboard.py                      # Dashboard Executivo corporativo (SVG limpo, zero emojis)
├── docs/                                 # Documentação de Engenharia (PRD, UCS, TAD, Guias Didáticos)
├── scripts/
│   ├── quality_gate.sh                   # Script oficial do Quality Gate (Ruff + Mypy + Pytest + Backup)
│   └── hot_backup.sh                     # Backup a quente comprimido do banco SQLite (.db.gz)
├── tests/                                # 118 testes automatizados cobrindo todos os módulos
├── Makefile                              # Comandos de automação (make check, make test, make run)
└── pyproject.toml                        # Configuração estrita do Ruff, MyPy e Pytest
```

---

## ⚡ Tabela de Endpoints da API

| Método | Endpoint | Descrição / Protocolo |
| :--- | :--- | :--- |
| `GET` | `/dashboard` | Interface do Painel Executivo Web (SVGs corporativos, zero emojis) |
| `GET` | `/health` | Liveness probe (status, fuso de Fortaleza, expediente comercial) |
| `GET` | `/metrics` | Exportador OpenMetrics / Prometheus v0.0.4 |
| `POST` | `/webhook` | Receptor de eventos da Evolution API (`MESSAGES_UPSERT`) com Rate Limit |
| `POST` | `/webhook/erp/stock` | Webhook de auto-ingestão de estoque e preço do Bling ERP |
| `GET` | `/api/reports/stats` | JSON com KPIs, rupturas evitadas, gráficos e pedidos recentes |
| `GET` | `/api/reports/orders.csv` | Exportação de despachos em CSV compatível com Power BI / Excel |
| `POST` | `/api/system/profile` | Atualização dinâmica de perfil comercial Whitelabel (`StoreProfile`) |
| `GET` | `/api/conversations` | Lista conversas ativas e status de silêncio da IA |
| `POST` | `/api/conversations/{phone}/resume` | Reativação silenciosa da IA via painel |
| `POST` | `/api/conversations/{phone}/pause` | Pausa manual da IA por 3 horas |
| `POST` | `/api/simulator/chat` | Simulador web de mensagens com validação de Rate Limit por IP |

---

## 🛡️ Execução da Suíte de Qualidade (Quality Gate)

O projeto adota o padrão de excelência de Big Tech, exigindo aprovação em todas as etapas antes de qualquer deploy em produção:

```bash
# Executa a verificação completa (Ruff Lint + MyPy Tipagem Estrita + 118 Testes + Hot Backup DB)
./scripts/quality_gate.sh

# Ou via Makefile
make check
```

---

## 📚 Documentação Completa do Projeto

Para se aprofundar em qualquer aspecto da arquitetura e do código:
* **[Guia Definitivo de Engenharia e Código Didático](file:///home/robson/Projetos_Desenvolvimento/victor-cell/pecasbot-api/docs/guia_engenharia_arquitetura_e_codigo_didatico.md)**: Explicação linha por linha de todos os 11 módulos, resiliência, algoritmos e governança de preços.
* **[Guia Visual de Cenários de Uso e Testes](file:///home/robson/Projetos_Desenvolvimento/victor-cell/pecasbot-api/docs/cenarios_de_uso_e_testes.md)**: Catálogo detalhado dos 118 testes e cenários de balcão.
* **[Manual de Comportamentos e Respostas no WhatsApp](file:///home/robson/Projetos_Desenvolvimento/victor-cell/pecasbot-api/docs/manual_comportamentos_e_respostas_whatsapp.md)**: Regras de linguagem de balcão, matriz de intenções e fluxos de atendimento.
* **[PRD-001: Especificação de Requisitos de Produto](file:///home/robson/Projetos_Desenvolvimento/victor-cell/pecasbot-api/docs/01_product_requirements_document.md)**: Especificação formal Google RFC/PRD.
* **[RFC-002: Arquitetura Técnica & Design](file:///home/robson/Projetos_Desenvolvimento/victor-cell/pecasbot-api/docs/02_technical_architecture_design.md)**: Modelagem DDD e fluxos de integração.
