# Análise Arquitetural, Viabilidade Comercial e Roadmap de Produto
## Sistema de Atendimento e Vendas Autônomo via WhatsApp (PecasBot / Conversational Engine)

---

### Metadados do Documento

| Atributo | Definição |
| :--- | :--- |
| **Identificador** | AUDIT-COM-001 |
| **Projeto** | Motor Conversacional Autônomo para WhatsApp (B2B / Varejo Especializado) |
| **Autor** | Staff Software Architect & Principal Product Strategist |
| **Classificação** | Estratégia de Produto, Arquitetura e Modelagem Comercial |
| **Versão** | 1.0.0 |
| **Status** | Aprovado para Planejamento Executivo |

---

## 1. Diagnóstico do Estado Atual: O que foi feito e Como foi feito

### 1.1 Fundações de Engenharia Consolidadas
O sistema foi desenvolvido seguindo os princípios de **Clean Architecture** (Arquitetura Limpa) e **Ports & Adapters** (Arquitetura Hexagonal), desacoplando estritamente o núcleo de regras de negócio das tecnologias externas.

O estado atual compreende:
1. **Domínio Puro (`domain/`):**
   - Entidades com validação estrita (`Product`, `Conversation`, `ReservationOrder`).
   - Máquina de Estados Finitos (`AI_ACTIVE`, `WAITING_CONFIRMATION`, `HUMAN_ACTIVE`).
   - Interfaces formais de repositórios, gateways de mensageria e provedores de IA.
2. **Casos de Uso Orquestrados (`application/`):**
   - `ProcessIncomingMessageUseCase`: Pipeline completo de triagem, cotação, confirmação de despacho em duas etapas e injeção de contexto de pedidos recentes.
   - `DebounceBuffer`: Buffer assíncrono de 3 segundos para consolidação de mensagens fragmentadas em rajada.
3. **Adaptadores de Infraestrutura e Inventário Pluggable (`infrastructure/`):**
   - `CachedInventoryProxy`: Cache em memória (Read-Through / Cache-Aside) que garante respostas de catálogo em **menos de 2 milissegundos**, protegendo APIs externas de estouro de quota.
   - `BlingV3InventoryAdapter`: Integração com o ERP Bling v3 com Circuit Breaker automático e tratamento de HTTP 429 (Rate Limit).
   - `GoogleSheetsInventoryAdapter`: Sincronização resiliente com planilhas de estoque no Google Drive e gavetas físicas.
   - `SqliteRepository`: Persistência relacional local para histórico multi-turn, rastreamento de ordens, logs de demanda reprimida e tabela anti-eco (`sent_messages`).
   - `AIAgentService`: Integração com Google Gemini 3.5 Flash com fallback semântico determinístico offline e suporte multimodal.
4. **Camada de Apresentação e Operação (`presentation/`):**
   - FastAPI assíncrono com webhooks da Evolution API.
   - Dashboard web responsivo (`/dashboard`) com autenticação por cookie HMAC SHA-256, simulador de chat em tempo real, copiloto gerencial e exportação de CSV.
5. **Qualidade e Confiabilidade:**
   - **81 testes automatizados (unitários e de integração)** passando com **100% de sucesso**.
   - **84% de cobertura global de código**.
   - Documentação de engenharia no padrão Google (`PRD-001`, `UCS-001`, `RFC-002`, `RFC-003`, `RFC-004`).

---

## 2. Análise SWOT Detalhada (Forças, Fraquezas, Oportunidades e Riscos)

### 2.1 Forças (Strengths)
- **Tom Humanizado Não-Robótico de Balcão:** O comportamento minerado a partir de 37 conversas reais elimina o formato enfadonho de árvore de decisão ("digite 1 para..."), operando em frases ultra-curtas de 1 a 6 palavras com credibilidade técnica.
- **Doutrina do Silêncio e Transbordo Seguro:** Ao contrário de bots convencionais que inventam desculpas prolixas ou alucinam orçamentos, o sistema permanece em silêncio absoluto (`reply_text: ""`) diante de incertezas e notifica a equipe física via ntfy.
- **Desacoplamento Hexagonal:** Facilidade para substituir ou estender o provedor de estoque (Planilha, Bling, Tiny, Omie) sem alterar uma única linha de regras de negócio.
- **Velocidade Extrema de Resposta:** O Cache Proxy reduz a latência de verificação de disponibilidade para frações de milissegundo, permitindo que a latência total seja dominada apenas pelo tempo de geração da IA.
- **Filtro Anti-Eco e Desduplicação:** Mecanismo robusto que impede que o bot interprete suas próprias mensagens como intervenção humana.

### 2.2 Fraquezas (Weaknesses / Gaps de Comercialização)
- **Regras de Negócio Acopladas ao Nicho da Victor Cell (Hardcoded Domain Logic):**
  - O prompt mestre e certos trechos de código trazem amarras específicas: "Victor Cell", "Fortaleza/CE", "Só peças de tablet", "Uber Flash".
  - *Impacto Comercial:* Para atender um novo cliente (ex: distribuidora de autopeças ou oficina mecânica), atualmente é necessário alterar o código-fonte.
- **Falta de um Cadastro de Perfil de Loja / Tenant (Multi-Tenant Engine):**
  - O sistema opera em banco SQLite único com variáveis de ambiente estáticas (`.env`).
  - *Impacto Comercial:* Não permite gerenciar múltiplos clientes em uma única infraestrutura sem subir instâncias Docker isoladas.
- **Fricção de Onboarding Inicial:**
  - A configuração de horários, regras de envio e credenciais depende de arquivos de configuração no servidor em vez de uma interface visual amigável de configuração ("Configurações da Loja").
- **Acoplamento à Evolution API:**
  - Os endpoints da camada de apresentação esperam o formato de payload da Evolution API (Baileys). Clientes corporativos maiores podem exigir a API Oficial da Meta (Cloud API) ou plataformas consolidadas (Z-API, WppConnect, Twilio).

### 2.3 Oportunidades de Mercado (Opportunities)
- **Consultoria de Automação para Comércio Especializado:** Assistências de celulares/notebooks, lojas de autopeças, distribuidoras de materiais elétricos e confecções sofrem exatamente da mesma dor: técnicos e compradores cotando peças o dia todo no WhatsApp com necessidade de resposta imediata.
- **Modelo de Receita Recorrente (MRR):** Cobrança de taxa de implantação/onboarding (setup fee) mais mensalidade recorrente de suporte, manutenção e infraestrutura.
- **Oferta de API Cognitiva para Sistemas de PDV:** Empresas de software de gestão (ERPs de bairro e sistemas de ordem de serviço) não possuem IA conversacional própria e têm interesse em plugar uma API que gerencie o WhatsApp de seus clientes.

### 2.4 Ameaças e Riscos (Threats)
- **Políticas de Banimento do WhatsApp (Meta):** O uso de instâncias não-oficiais (Baileys/Evolution API) acarreta risco de bloqueio de números se houver denúncias de spam ou comportamento anormal (mitigado pelo fato de o bot ser receptivo e não fazer disparos em massa frios).
- **Oscilação de Quotas e Custos de APIs de IA:** Mudanças nas políticas de preços do Google Cloud (Gemini) podem comprimir a margem de lucro se o volume de tokens por cliente não for controlado.

---

## 3. Modelo de Negócio e Estratégia de Comercialização

Para que a venda da solução não gere complexidade operacional excessiva nem exija grandes times de suporte, estruturam-se **três modalidades complementares de monetização**:

```
                                  MODELOS DE VENDA
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
  [MODALIDADE A]                   [MODALIDADE B]                   [MODALIDADE C]
Consultoria de Implantação       Software como Serviço            API de Inteligência
+ Mensalidade (Retainer)         Gerenciado (Turnkey)             para Softwares / PDVs
R$ 3.500 setup + R$ 690/mês      R$ 490 a R$ 890/mês              R$ 0,15 por atendimento
```

### 3.1 Modalidade A: Consultoria de Implantação Personalizada + Retainer (Modelo Recomendado para Início)
- **Público-Alvo:** Pequenas e médias distribuidoras locais, assistências técnicas e atacados de autopeças.
- **Proposta de Valor:** "Automatizamos o WhatsApp da sua loja com o mesmo jeito que seu melhor atendente de balcão fala, integrado ao seu estoque existente (Planilha ou ERP)."
- **Estrutura de Preço:**
  - **Setup / Implantação (R$ 3.500 a R$ 7.000 taxa única):**
    - Levantamento e mineração dos diálogos reais da loja (estilo de resposta).
    - Higienização e conexão do catálogo de estoque (Google Sheets ou Bling/Tiny).
    - Configuração de horários, bairros atendidos e taxa de entrega.
    - Homologação em número de teste e treinamento da equipe física para assumir transbordos.
  - **Mensalidade de Suporte e Infraestrutura (R$ 590 a R$ 1.200 / mês):**
    - Hospedagem dedicada na nuvem.
    - Monitoramento de uptime e reconexão automática de WhatsApp.
    - Suporte técnico contínuo e relatórios analíticos mensais de cotação e demanda reprimida.
- **Por que é viável:** Baixa complexidade de vendas. O cliente não precisa entender de tecnologia; ele compra o resultado (horas do dono economizadas e mais vendas fechadas no balcão).

### 3.2 Modalidade B: Produto Gerenciado White-Label (Turnkey SaaS)
- **Público-Alvo:** Negócios menores que querem uma solução plug-and-play sem consultoria extensiva.
- **Proposta de Valor:** Plataforma pronta onde o cliente acessa um painel web, sobe sua planilha do Excel/Google Sheets, lê o QR Code do WhatsApp e o bot começa a operar imediatamente.
- **Estrutura de Preço:** Assinatura mensal recorrente de R$ 390 a R$ 690 / mês.

### 3.3 Modalidade C: API de Inteligência Conversacional (Microserviço Cognitivo B2B)
- **Público-Alvo:** Desenvolvedores de software de PDV e agências de marketing que já têm clientes no WhatsApp mas não sabem implementar IA semântica, debounce e transbordo humano.
- **Estrutura de Preço:** Cobrança por volume (`R$ 0,10 a R$ 0,25 por conversa concluída`) através de endpoint padronizado `POST /v1/chat/process`.

---

## 4. O que Falta para o Sistema se Tornar um Produto de Pronta Comercialização

Para que a solução possa ser vendida para diferentes comércios sem exigir refatorações manuais de código a cada contrato, foram identificados **cinco pilares técnicos essenciais**:

```
                                PILARES DE EVOLUÇÃO
                                         │
        ┌───────────────┬────────────────┼───────────────┬────────────────┐
        ▼               ▼                ▼               ▼                ▼
   [PILAR 1]        [PILAR 2]        [PILAR 3]       [PILAR 4]        [PILAR 5]
Desacoplamento   Perfil de Loja    Wizard Visual   Multi-Gateway    Métricas de
 de Negócio      Configurável      de Onboarding   de Mensageria    Consumo & Custo
 (Domain Agnostic) (StoreProfile)  (No-Code Setup) (Meta/Z-API/Evo) (Billing/Audit)
```

### Pilar 1: Desacoplamento da Lógica de Negócio (Domain-Agnostic Engine)
- **Situação Atual:** As regras "Só peças de tablet", "Uber Flash" e os exemplos de few-shot estão gravados diretamente no arquivo `agent_service.py`.
- **Necessidade:** O motor de IA deve receber um objeto `StoreProfile` injetado em tempo de execução, contendo:
  - Nome comercial da empresa.
  - Nicho de atuação (ex: "Peças de Tablet", "Autopeças de Moto", "Farmácia de Manipulação").
  - Instrução de escopo e produtos recusados (ex: "Trabalhamos apenas com suspensão e freios; não atendemos lataria").
  - Métodos de envio e entrega disponíveis (ex: "Uber Flash", "Motoboy próprio", "Correios / Sedex", "Retirada no Balcão").
  - Tom de voz e vocabulário técnico regional.

### Pilar 2: Tabela de Configuração e Perfil no SQLite (`store_profile`)
- **Situação Atual:** O arquivo `.env` controla apenas configurações de infraestrutura.
- **Necessidade:** Persistir as definições comerciais no SQLite para que possam ser consultadas e alteradas dinamicamente via API sem reiniciar a aplicação.

### Pilar 3: Interface Visual de Configurações no Dashboard
- **Situação Atual:** O dashboard exibe métricas, simulador e copilot, mas não possui formulário para editar horários de funcionamento, regras de entrega e textos de recusa.
- **Necessidade:** Uma aba "Configurações da Loja" onde o próprio cliente ou o consultor preenche os dados em 5 minutos.

### Pilar 4: Abstração de Gateway de Mensageria
- **Situação Atual:** Webhooks formatados para Evolution API v2.
- **Necessidade:** Implementar adaptadores para APIs alternativas (como Z-API e WhatsApp Cloud API oficial da Meta) através de contratos unificados de eventos de entrada e saída.

### Pilar 5: Telemetria de Uso e Controle de Custos de Tokens
- **Situação Atual:** O sistema registra conversas e cotações, mas não contabiliza tokens consumidos por requisição do Gemini.
- **Necessidade:** Registro de consumo de tokens por conversa no SQLite para possibilitar auditoria exata do custo operacional de IA por cliente.

---

## 5. Plano de Execução em Fases (Implementation Roadmap)

Seguindo o rigor metodológico solicitado (Planejar $\rightarrow$ Analisar $\rightarrow$ Corrigir $\rightarrow$ Executar com Testes Automatizados):

### Fase 1: Arquitetura de Perfil de Loja Configurável (`StoreProfile`)
1. **Modelagem:** Criar entidade `StoreProfile` em `domain/entities.py` com campos estruturados:
   - `store_name: str`
   - `niche_description: str`
   - `out_of_scope_policy: str`
   - `rejection_message: str`
   - `delivery_methods: List[str]`
   - `pickup_allowed: bool`
   - `tone_guidelines: str`
2. **Persistência:** Implementar métodos `get_store_profile()` e `save_store_profile()` em `SqliteRepository`.
3. **Engenharia de Prompt Dinâmica:** Atualizar `AIAgentService` para aceitar `StoreProfile`, gerando o prompt de forma 100% dinâmica e eliminando referências fixas em código.
4. **Retrocompatibilidade Garantida:** Se nenhum perfil for fornecido, o sistema aplica o perfil padrão da Victor Cell (Tablets / Balcão), preservando 100% dos 81 testes existentes.

### Fase 2: Gestão via API e Dashboard de Configuração
1. Criar endpoints REST:
   - `GET /api/system/profile` (Retorna perfil da loja em JSON).
   - `POST /api/system/profile` (Atualiza perfil comercial em tempo de execução).
2. Adicionar formulário de edição de perfil no template do Dashboard (`presentation/dashboard.py`).

### Fase 3: Validação de Qualidade e Cobertura
1. Implementar testes unitários para a entidade `StoreProfile` e seus métodos de persistência.
2. Implementar testes de integração para o prompt dinâmico em outros nichos (ex: loja de autopeças cotando amortecedor e recusando som automotivo).
3. Garantir 100% de sucesso da suíte ampliada de testes.
