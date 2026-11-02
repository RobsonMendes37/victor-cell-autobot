# UCS-001: Especificação Formal de Casos de Uso (Use Case Specifications)
## Sistema Autônomo de Atendimento, Cotação e Despacho de Peças via WhatsApp (PecasBot)

---

### Metadados do Documento

| Atributo | Definição |
| :--- | :--- |
| **Identificador** | UCS-001-PECSBOT |
| **Organização** | Victor Cell (Fortaleza/CE) |
| **Autor** | Staff Requirements Engineer / Engenharia de Software |
| **Padrão de Especificação** | Google Engineering Documentation Standard (Cockburn / IEEE 830) |
| **Versão** | 2.1.0 (Produção Homologada) |
| **Status** | Aprovado |
| **Classificação** | Técnico / Engenharia de Software |
| **Documento Pai** | [PRD-001: Especificação de Requisitos de Produto](file:///home/robson/Projetos_Desenvolvimento/victor-cell/pecasbot-api/docs/01_product_requirements_document.md) |

---

## 1. Matriz de Rastreabilidade (Requisitos vs. Casos de Uso)

| Caso de Uso | Título do Caso de Uso | Requisitos Funcionais Atendidos (PRD-001) |
| :--- | :--- | :--- |
| **UC-01** | Cotação Direta de Peça de Tablet em Horário Comercial | FR-01, FR-04, FR-11, FR-12 |
| **UC-02** | Cotação Fora do Expediente Comercial e Aos Domingos | FR-01, FR-04, FR-06, FR-12 |
| **UC-03** | Rejeição Determinística de Telefonia Móvel (Não-Tablets) | FR-01, FR-05 |
| **UC-04** | Protocolo Multimodal e Triagem Visual de Imagens | FR-01, FR-07, FR-08 |
| **UC-05** | Fechamento de Pedido e Despacho Uber Flash em Duas Fases | FR-01, FR-09, FR-12 |
| **UC-06** | Reserva de Peça para Retirada no Balcão Físico | FR-01, FR-09, FR-12, FR-13 |
| **UC-07** | Transbordo Silencioso para Atendimento Humano | FR-01, FR-08 |
| **UC-08** | Intervenção Manual de Operador e Filtro Anti-Eco | FR-02, FR-03 |
| **UC-09** | Consulta de Status Operacional e Rastreio Pós-Venda | FR-01, FR-09, FR-12 |
| **UC-10** | Consulta Analítica e Auditoria via Copilot do Gestor | FR-10, FR-15 |

---

## 2. Atores do Sistema

### 2.1 Ator Primário: Cliente Técnico (Solicitante)
Usuário externo que interage através de mensagens de texto, áudio gravado ou fotografias no canal corporativo do WhatsApp. Representa técnicos de bancada, oficinas parceiras e compradores que buscam rapidez na confirmação de preço e disponibilidade de componentes.

### 2.2 Ator Secundário: Operador de Expedição / Caixa da Loja
Usuário interno físico presente na sede da Victor Cell. Recebe ordens de separação consolidadas via aplicativo ntfy e assume o atendimento no WhatsApp para cotação manual de frete Uber Flash, fornecimento de chave Pix e emissão de comprovantes.

### 2.3 Ator Secundário: Gestor / Proprietário da Loja
Usuário corporativo responsável pelo controle gerencial, auditoria do inventário e configurações do sistema (incluindo ativação do Master Kill-Switch e consulta ao Copilot).

### 2.4 Ator de Sistema: Agente Autônomo PecasBot
Componente de software hospedado em nuvem executando o pipeline de ingestão de webhooks, debounce de rajadas de mensagens, classificação semântica com Google Gemini 3.5 Flash, controle da máquina de estados no SQLite e mediação de estoque com Cache Proxy.

---

## 3. Especificação Detalhada dos Casos de Uso

---

### UC-01: Cotação Direta de Peça de Tablet em Horário Comercial

#### Metadados do Caso de Uso
- **Identificador:** UC-01
- **Ator Primário:** Cliente Técnico
- **Atores Secundários:** Agente Autônomo PecasBot, Provedor de Inventário
- **Gatilho:** Cliente envia mensagem solicitando preço ou disponibilidade de peça de tablet durante o expediente regular (Seg a Sex: 08:30 às 18:00 | Sáb: 08:30 às 13:00).
- **Pré-condições:**
  1. A instância da Evolution API está conectada e operando normalmente.
  2. A conversa com o número do cliente está no estado `AI_ACTIVE` no SQLite.
  3. A hora local do servidor encontra-se dentro da janela de expediente da loja.
- **Pós-condições de Sucesso:**
  1. O cliente recebe resposta objetiva em estilo de balcão (1 a 6 palavras).
  2. O SKU cotado é registrado no campo `active_sku` da conversa.
  3. Um registro de cotação com sucesso (`had_stock = 1`) é persistido na tabela `quote_logs`.

#### Fluxo Principal de Sucesso (Main Success Scenario)
1. O Cliente Técnico envia a mensagem: `"Quanto tá o touch do tablet M7?"`.
2. O Agente Autônomo aplica o debounce de 3 segundos e submete a mensagem ao pipeline.
3. O sistema avalia a hora do sistema e confirma que a loja está aberta (`is_open = true`).
4. O Agente consulta o `CachedInventoryProxy` e identifica o produto correspondente: SKU `T2040-TOUCH` com saldo disponível de 10 unidades e valor R$ 45,00.
5. O modelo semântico gera a resposta direta e sem floreios: `"R$ 45"`.
6. O sistema despacha a mensagem via Evolution API para o WhatsApp do cliente.
7. O sistema atualiza o registro da conversa no SQLite: `active_sku = "T2040-TOUCH"`, `state = AI_ACTIVE`.
8. O caso de uso é concluído.

#### Fluxos Alternativos e Ramificações
- **A1. Peça com Diferenciação Técnica (Aro / Linha / Qualidade):**
  - No passo 4, se o modelo consultado possui versões com especificações distintas (ex: Tela Tab A8 X200 Wi-Fi vs Conector de Carga):
  - O sistema formata a resposta discriminando os itens em uma única linha enxuta: `"Tela R$ 140 / Conector R$ 25"`.
  - O caso de uso prossegue para o passo 6.
- **A2. Mensagens Fragmentadas Recebidas em Rajada:**
  - No passo 1, o cliente envia três mensagens em 2 segundos: `"Tem touch"`, `"do M7?"`, `"quanto custa?"`.
  - O buffer de debounce unifica as três entradas em uma única string semântica e executa o passo 2 apenas uma vez.

#### Fluxos de Exceção
- **E1. Peça Esgotada no Catálogo (`stock_quantity == 0` ou `has_stock == false`):**
  - No passo 4, o item é localizado mas o saldo físico é nulo.
  - O Agente gera a resposta padrão de recusa enxuta: `"Tem não"`.
  - O sistema grava log com `had_stock = 0` (demanda reprimida) e conclui a execução.
- **E2. Provedor de Estoque Externo Indisponível (Queda de Rede / 429):**
  - No passo 4, a comunicação com o Bling ERP ou Google Sheets falha.
  - O `CachedInventoryProxy` aciona o espelho local SQLite em < 2ms e serve a cotação sem interrupção para o cliente.

---

### UC-02: Cotação Fora do Expediente Comercial e Aos Domingos

#### Metadados do Caso de Uso
- **Identificador:** UC-02
- **Ator Primário:** Cliente Técnico
- **Atores Secundários:** Agente Autônomo PecasBot
- **Gatilho:** Cliente consulta valores ou disponibilidade fora do expediente comercial ou em qualquer horário de domingo.
- **Pré-condições:**
  1. A hora local de Fortaleza/CE (UTC-3) indica que a loja física está fechada (`is_open = false`).
  2. A conversa encontra-se no estado `AI_ACTIVE`.
- **Pós-condições de Sucesso:**
  1. O cliente recebe o valor exato da peça em estoque.
  2. A mensagem informa com precisão que a loja está fechada e indica o horário de reabertura.
  3. O cliente não é induzido a crer que há expedição imediata ou possibilidade de retirada física no momento.

#### Fluxo Principal de Sucesso
1. O Cliente Técnico envia mensagem no domingo às 15:30: `"Tem touch do M10A?"`.
2. O sistema avalia a regra de expediente e calcula: `is_open = false`, `schedule_notice = "Fechado hoje (domingo), abre amanhã 08:30"`.
3. O `CachedInventoryProxy` localiza o produto (SKU `TOU-MUL-M10A`, Touch R$ 90, Display R$ 180).
4. O Agente formata a resposta concatenando a cotação direta ao aviso de reabertura: `"Touch 90 / Display 180. Fechado hoje (domingo), abre amanhã 08:30."`.
5. A mensagem é enviada ao WhatsApp do cliente.
6. O caso de uso é concluído.

#### Fluxos Alternativos
- **A1. Cotação em Dia de Semana Após às 18:00:**
  - No passo 2, o cálculo determina que é terça-feira às 21:00.
  - O sufixo aplicado é `"Fechado agora, abre amanhã 08:30."`.
  - A resposta gerada é: `"Touch 90 / Display 180. Fechado agora, abre amanhã 08:30."`.

---

### UC-03: Rejeição Determinística de Telefonia Móvel (Não-Tablets)

#### Metadados do Caso de Uso
- **Identificador:** UC-03
- **Ator Primário:** Cliente Técnico
- **Atores Secundários:** Agente Autônomo PecasBot
- **Gatilho:** Mensagem do cliente contendo solicitação de componentes, acessórios ou serviços para smartphones, iPhones, capas ou películas.
- **Pré-condições:** A mensagem contém termos lexicais associados a celulares (ex: "A15", "iPhone", "Moto G", "celular", "capinha").
- **Pós-condições de Sucesso:**
  1. O cliente recebe recusa categórica imediata informando a restrição de escopo.
  2. Nenhuma busca de SKU é realizada no catálogo de tablets.
  3. A conversa permanece em `AI_ACTIVE`.

#### Fluxo Principal de Sucesso
1. O Cliente envia a mensagem: `"Tem tela de celular iPhone 11?"`.
2. O subsistema semântico identifica que o item pertence à categoria de telefonia móvel / fora de foco.
3. O sistema aborta buscas no inventário e formula a resposta determinística de balcão: `"Só peças de tablet"`.
4. Caso a loja esteja fechada no momento da consulta, o sufixo de reabertura é adicionado: `"Só peças de tablet. Fechado hoje (domingo), abre amanhã 08:30."`.
5. A resposta é despachada ao cliente.
6. O caso de uso é concluído.

---

### UC-04: Protocolo Multimodal e Triagem Visual de Imagens

#### Metadados do Caso de Uso
- **Identificador:** UC-04
- **Ator Primário:** Cliente Técnico
- **Atores Secundários:** Operador de Expedição, Agente Autônomo PecasBot, Servidor ntfy
- **Gatilho:** Cliente envia uma fotografia de tablet danificado ou de carcaça para identificação de modelo.
- **Pré-condições:** O webhook da Evolution API recebe mensagem do tipo `imageMessage` com bytes acessíveis ou URL de download.
- **Pós-condições de Sucesso:**
  1. Se a frente estiver apagada, o cliente é instruído a enviar a traseira.
  2. Se a traseira for identificada com 100% de certeza, a cotação é entregue.
  3. Se houver qualquer dúvida ou ilegibilidade, o bot silencia-se completamente (`reply_text: ""`) e notifica o operador humano.

#### Fluxo Principal de Sucesso (Frente com Tela Apagada)
1. O Cliente envia foto de um tablet com tela frontal quebrada e apagada.
2. O módulo de visão computacional analisa os bytes da imagem e detecta ausência de dados do modelo na face frontal.
3. O Agente formula a resposta curta instruindo o envio da carcaça traseira: `"Foto dele parte trás"`.
4. A mensagem é enviada ao cliente.
5. O estado da conversa é mantido em `AI_ACTIVE`.
6. O caso de uso é concluído.

#### Fluxos Alternativos
- **A1. Foto da Traseira com Modelo 100% Legível:**
  - No passo 2, o modelo identifica claramente a etiqueta traseira (ex: "Multilaser M7 3G Plus").
  - O Agente localiza o produto no catálogo e responde com o preço diretamente: `"Touch R$ 45"`.
  - O fluxo é concluído com sucesso.
- **A2. Foto Ilegível, Borrada, com Reflexo ou Código Raspado (Doutrina do Silêncio):**
  - No passo 2, a imagem apresenta reflexo ou modelo raspado, gerando incerteza técnica.
  - O Agente define: `intent = "HUMAN_HANDOFF"`, `reply_text = ""`, `requires_staff_alert = true`.
  - Nenhuma mensagem é enviada ao cliente.
  - O sistema emite notificação sonora prioritária no canal ntfy do balcão:
    - *Título:* `"Foto ilegível / Modelo com dúvida para conferência humana"`
    - *Mensagem:* `"Cliente: [Nome] ([Telefone]) enviou foto para conferência de bancada."`
  - A conversa no SQLite transita para `HUMAN_ACTIVE` (silêncio de 3 horas).
  - O técnico humano abre o WhatsApp e responde diretamente.

---

### UC-05: Fechamento de Pedido e Despacho Uber Flash em Duas Fases

#### Metadados do Caso de Uso
- **Identificador:** UC-05
- **Ator Primário:** Cliente Técnico
- **Atores Secundários:** Operador de Expedição, Agente Autônomo PecasBot, Servidor ntfy
- **Gatilho:** Cliente solicita envio de peça previamente cotada através de serviço de entrega rápida (Uber Flash).
- **Pré-condições:**
  1. A conversa possui um `active_sku` registrado no contexto recente (menos de 2 horas).
  2. A loja física está em horário de expediente (`is_open = true`).
- **Pós-condições de Sucesso:**
  1. O endereço de destino é validado e armazenado.
  2. O cliente confirma formalmente a solicitação na Fase 2.
  3. Uma ordem com status `PENDING_SEPARATION` é gravada no banco SQLite.
  4. Um alerta de expedição é disparado para a equipe física providenciar a separação e o Uber Flash.

#### Fluxo Principal de Sucesso (Two-Phase Commit)
1. O Cliente envia a mensagem: `"Pode mandar entregar pelo Uber Flash na Rua Floriano Peixoto 1250 Centro"`.
2. O sistema extrai o endereço através do analisador léxico: `"Rua Floriano Peixoto 1250 Centro"`.
3. **[Fase 1 - Pré-Confirmação]:**
   - O sistema detecta a intenção `ORDER_PENDING_CONFIRMATION`.
   - A conversa transita para o estado `WAITING_CONFIRMATION`.
   - O endereço é armazenado temporariamente no campo `notes` da conversa.
   - O bot responde com a pergunta de fechamento: `"Anotado: Rua Floriano Peixoto 1250 Centro. Posso confirmar o envio pelo Uber Flash?"`.
4. O Cliente responde de forma afirmativa: `"Pode confirmar sim, patrão!"`.
5. **[Fase 2 - Confirmação e Efetivação]:**
   - O sistema valida que a conversa estava em `WAITING_CONFIRMATION` e reconhece a afirmação.
   - O sistema classifica o evento como `ORDER_DISPATCH`.
   - Um novo pedido é persistido no SQLite com status `PENDING_SEPARATION`, gerando o identificador `ped_[timestamp]_[id]`.
   - O sistema gera a resposta final ao cliente: `"Certo, separando aqui pra mandar pelo Uber Flash pro endereço: Rua Floriano Peixoto 1250 Centro. Já te passo o Pix."`.
6. O sistema emite notificação de despacho prioritária via ntfy para o aplicativo dos funcionários:
   - *Conteúdo:* `"Separar Peça: [SKU] | Destino: Rua Floriano Peixoto 1250 Centro | Cliente: [Telefone] | Chamar Uber Flash!"`.
7. O operador humano do balcão assume o chat para informar o valor exato da corrida do Uber e enviar a chave Pix.
8. O caso de uso é concluído.

#### Fluxos Alternativos
- **A1. Cliente Pede Uber Sem Fornecer o Endereço:**
  - No passo 1, o cliente diz apenas: `"Separa aí, manda por Uber Flash"`.
  - O sistema identifica ausência de endereço e responde: `"Passa o endereço pra calcular o Uber"`.
  - O estado da conversa permanece em `AI_ACTIVE`.
- **A2. Cliente Desiste ou Nega a Confirmação na Fase 2:**
  - No passo 4, o cliente responde: `"Não, espera que eu vejo com o cliente primeiro"`.
  - O sistema detecta a negativa, cancela o estado de espera e retorna a conversa para `AI_ACTIVE`, respondendo: `"Tranquilo, precisando só chamar"`.
  - Nenhum pedido é gerado no SQLite e nenhum alarme é emitido para a expedição.
- **A3. Solicitação de Envio com a Loja Fechada:**
  - No passo 1, a mensagem é enviada às 22:00.
  - O sistema responde: `"Anotado. A gente abre amanhã 08:30 pra despachar."`.
  - O pedido é anotado em fila de espera para abertura matinal.

---

### UC-06: Reserva de Peça para Retirada no Balcão Físico

#### Metadados do Caso de Uso
- **Identificador:** UC-06
- **Ator Primário:** Cliente Técnico
- **Atores Secundários:** Operador de Expedição, Agente Autônomo PecasBot, Servidor ntfy
- **Gatilho:** Cliente informa que deseja reservar a peça e comparecerá pessoalmente à loja física para retirar.
- **Pré-condições:** O cliente cotou uma peça válida que consta com saldo no inventário.
- **Pós-condições de Sucesso:**
  1. A equipe do balcão é notificada para separar fisicamente a peça na gaveta correspondente.
  2. O cliente é orientado de forma concisa sobre a localização da peça.

#### Fluxo Principal de Sucesso
1. O Cliente envia a mensagem: `"Separa essa tela do M7 que eu passo aí no balcão pra pegar em 20 minutos"`.
2. O sistema reconhece a intenção de separação em balcão (`"passo aí"`, `"balcão"`).
3. O sistema formula a resposta enxuta de balcão: `"Separando aqui no balcão"`.
4. A mensagem é despachada ao cliente.
5. O sistema emite alerta via ntfy:
   - *Título:* `"CLIENTE PEDINDO PRA SEPARAR NO BALCÃO"`
   - *Mensagem:* `"Peça: T2040-TOUCH | Cliente: [Telefone] | Retirada em balcão solicitada."`
6. O operador retira a peça da gaveta física e a deixa identificada no caixa.
7. O caso de uso é concluído.

---

### UC-07: Transbordo Silencioso para Atendimento Humano

#### Metadados do Caso de Uso
- **Identificador:** UC-07
- **Ator Primário:** Cliente Técnico
- **Atores Secundários:** Operador de Expedição, Agente Autônomo PecasBot, Servidor ntfy
- **Gatilho:** Cliente aborda assuntos que exigem avaliação discricionária humana (reparo de placa-mãe, pedido de desconto, garantia/troca ou peças não cadastradas).
- **Pré-condições:** A conversa encontra-se em `AI_ACTIVE`.
- **Pós-condições de Sucesso:**
  1. O cliente **não recebe nenhuma resposta automática da IA** (`reply_text: ""`), garantindo que o atendimento não pareça robótico.
  2. O sistema silencia a IA para aquele número por 3 horas no SQLite (`state = HUMAN_ACTIVE`).
  3. O operador humano recebe alerta imediato com o motivo do transbordo para intervir pessoalmente.

#### Fluxo Principal de Sucesso
1. O Cliente envia a mensagem: `"Vocês fazem reparo de placa em curto ou reballing de processador?"`.
2. O classificador semântico identifica o termo restrito `"reparo de placa"` e define: `intent = "HUMAN_HANDOFF"`, `reply_text = ""`, `requires_staff_alert = true`.
3. O sistema atualiza o registro da conversa no SQLite: `state = HUMAN_ACTIVE`, `human_resumed_at = [timestamp_atual]`, `human_silence_duration_hours = 3`.
4. O sistema dispara notificação sonora via ntfy para o celular da equipe:
   - *Título:* `"Dúvida técnica / Reparo de placa no balcão"`
   - *Mensagem:* `"Cliente [Telefone] perguntou sobre reparo de placa. Assuma a conversa no WhatsApp!"`
5. Nenhuma mensagem é postada no canal do cliente pelo bot.
6. O técnico de bancada humano abre o WhatsApp e responde com a avaliação técnica apropriada.
7. O caso de uso é concluído.

#### Fluxos Alternativos
- **A1. Tentativa de Negociação de Preço / Desconto:**
  - No passo 1, o cliente pergunta: `"Faz por menos se eu pagar no dinheiro à vista?"`.
  - O sistema detecta negociação de preço, mantém silêncio absoluto para o cliente e notifica o gestor para avaliar margem comercial.
- **A2. Acionamento de Garantia ou Devolução:**
  - No passo 1, o cliente afirma: `"A tela que peguei ontem veio com touch falhando no canto"`.
  - O sistema silencia a IA, evita qualquer atrito automatizado e aciona o responsável pelas trocas físicas.

---

### UC-08: Intervenção Manual de Operador e Filtro Anti-Eco

#### Metadados do Caso de Uso
- **Identificador:** UC-08
- **Ator Primário:** Operador de Expedição / Dono da Loja
- **Atores Secundários:** Agente Autônomo PecasBot
- **Gatilho:** O operador humano digita e envia uma mensagem diretamente no aplicativo do WhatsApp para um cliente que estava conversando com o bot.
- **Pré-condições:** O webhook da Evolution API reporta evento `messages.upsert` com `fromMe: true`.
- **Pós-condições de Sucesso:**
  1. A IA detecta a intervenção humana real e suspende suas atividades para aquele cliente por 3 horas.
  2. Mensagens subsequentes enviadas pelo próprio bot não são interpretadas como intervenção humana (Anti-Echo).

#### Fluxo Principal de Sucesso
1. O Operador Humano digita no celular: `"Fala patrão, pode vir que separei a peça aqui pra você"`.
2. A Evolution API emite o webhook correspondente com `fromMe = true` e identificador de mensagem `wa_human_9981`.
3. O backend consulta a tabela `sent_messages` no SQLite para verificar se `wa_human_9981` foi despachado pelo próprio bot.
4. O sistema constata que o ID não consta na tabela, confirmando tratar-se de uma pessoa física real.
5. O sistema atualiza a conversa: `state = HUMAN_ACTIVE`, registrando o timestamp atual.
6. A IA desativa todas as respostas automáticas para este cliente pelas próximas 3 horas.
7. O caso de uso é concluído.

#### Fluxos Alternativos
- **A1. Reativação Manual da Automação via Painel:**
  - O gestor abre o painel administrativo (`/dashboard`) e clica em `"Retomar IA"` na conversa com o cliente.
  - O backend altera o estado para `AI_ACTIVE` e limpa os prazos de silêncio, reabilitando o atendimento automático imediatamente.

---

### UC-09: Consulta de Status Operacional e Rastreio Pós-Venda

#### Metadados do Caso de Uso
- **Identificador:** UC-09
- **Ator Primário:** Cliente Técnico
- **Atores Secundários:** Agente Autônomo PecasBot
- **Gatilho:** Cliente que já realizou um pedido recente pergunta se a peça já foi despachada ou se o motorista do Uber já saiu.
- **Pré-condições:** O cliente possui um pedido gravado com status `PENDING_SEPARATION` no SQLite nas últimas 24 horas.
- **Pós-condições de Sucesso:**
  1. O sistema reconhece o pedido em andamento e informa o status de separação sem recriar pedidos ou acionar alarmes duplicados.

#### Fluxo Principal de Sucesso
1. O Cliente envia a mensagem: `"E aí amigo, deu certo o meu pedido? Já despachou o Uber?"`.
2. O sistema executa o caso de uso e consulta os pedidos recentes atrelados ao número telefônico através do método `get_recent_orders_by_phone`.
3. O repositório retorna o pedido ativo com status `PENDING_SEPARATION`.
4. O Agente reconhece a consulta pós-venda e responde de forma tranquilizadora e direta: `"Pedido tá em separação aqui pra despachar."`.
5. A resposta é entregue no WhatsApp do cliente.
6. O sistema garante que `order_created = false`, preservando a integridade das ordens existentes.
7. O caso de uso é concluído.

---

### UC-10: Consulta Analítica e Auditoria via Copilot do Gestor

#### Metadados do Caso de Uso
- **Identificador:** UC-10
- **Ator Primário:** Gestor / Proprietário da Loja
- **Atores Secundários:** Agente Autônomo PecasBot (Google Gemini 3.5 Flash)
- **Gatilho:** O gestor formula uma pergunta sobre a operação comercial, estoque ou vendas no chat executivo do painel web.
- **Pré-condições:** O gestor está autenticado na sessão do dashboard via cookie seguro.
- **Pós-condições de Sucesso:**
  1. O gestor recebe análise executiva estruturada (padrão Google Executive Briefing, 150 a 250 palavras) baseada em dados reais consolidados do banco SQLite e inventário.

#### Fluxo Principal de Sucesso
1. O Gestor acessa o painel web e digita na aba Copilot: `"Qual a peça mais procurada hoje e como está nossa operação de balcão?"`.
2. O backend reúne o contexto operacional em tempo real:
   - Volume de conversas ativas em `AI_ACTIVE` vs `HUMAN_ACTIVE`;
   - Ranking de cotações das últimas 24 horas extraído de `quote_logs`;
   - Saldo dos componentes mais demandados no inventário.
3. O Agente de IA processa o prompt executivo sob as diretrizes de concisão analítica (sem rodeios formais).
4. O sistema retorna o parecer resumido indicando os itens líderes de procura (ex: Touch M7 e Tela Tab A8) e recomendando atenção para reposição de peças com estoque baixo.
5. A resposta é exibida na interface web.
6. O caso de uso é concluído.

---

---

### UC-11: Auditoria em Tempo Real e Inspeção Técnica de Sistema

#### Metadados do Caso de Uso
- **Identificador:** UC-11
- **Ator Primário:** Administrador do Sistema / Gestor da Operação
- **Atores Secundários:** Motor de Auditoria (`AuditLogEntry`), API REST
- **Gatilho:** O administrador acessa a aba "Auditoria & Logs" no painel executivo para auditar decisões da IA, transbordos ou gargalos de latência.
- **Pré-condições:** Usuário autenticado com sessão administrativa válida.
- **Pós-condições de Sucesso:**
  1. O sistema renderiza a trilha cronológica imutável com filtros por nível (`INFO`, `WARN`, `ERROR`), componente (`AI_ENGINE`, `ROUTER`, `NOTIFIER`, `REPO`, `ADMIN`, `ERP_SYNC`) e busca textual em tempo real.

#### Fluxo Principal de Sucesso
1. O Administrador abre a aba "Auditoria & Logs" no dashboard.
2. O frontend executa requisição HTTP `GET /api/audit/logs?limit=100`.
3. O endpoint valida o cookie HMAC, consulta o repositório ativo (`SqliteRepository` ou `PostgresRepository`) e retorna a lista ordenada de eventos.
4. A tabela desktop exibe colunas com Timestamp, Nível (badge colorido), Componente (tag monoespaçada), Ação, Ator, Latência (ms) e Detalhes JSON.
5. Em celulares, o sistema exibe cards touch otimizados com dados de auditoria colapsáveis.
6. O Administrador pode clicar nos botões de filtro rápido (`INFO`, `WARN`, `ERROR`) ou digitar termos para filtragem instantânea sem recarregar a página.
7. O caso de uso é concluído.

---

### UC-12: Parametrização Comercial Whitelabel e Perfil da Loja

#### Metadados do Caso de Uso
- **Identificador:** UC-12
- **Ator Primário:** Gestor Comercial / Administrador do Tenant
- **Atores Secundários:** Repositório de Perfil de Loja (`StoreProfile`), Motor Cognitivo (`AIAgentService`)
- **Gatilho:** O gestor acessa a aba "Perfil da Loja" para ajustar o nome da empresa, cidade, nicho, palavras fora de escopo ou mensagens de recusa.
- **Pré-condições:** Usuário autenticado no dashboard.
- **Pós-condições de Sucesso:**
  1. O perfil da loja é persistido no banco de dados e passa a orientar imediatamente o prompt e o fallback semântico da IA.
  2. Um log de auditoria `STORE_PROFILE_UPDATED` é registrado automaticamente.

#### Fluxo Principal de Sucesso
1. O Gestor abre a aba "Perfil da Loja" no painel.
2. O sistema recupera a configuração ativa via `GET /api/system/profile` e preenche o formulário.
3. O Gestor altera as configurações (ex: nome da empresa para "Alpha Peças", palavras fora de escopo e mensagens de recusa).
4. O Gestor clica em "Salvar Diretrizes Comerciais".
5. O frontend envia `POST /api/system/profile` com payload JSON validado via Pydantic.
6. O repositório salva o perfil no banco com timestamp UTC atualizado.
7. O sistema emite log de auditoria com nível `INFO`, componente `ADMIN` e ator `dashboard_admin`.
8. O frontend exibe toast de confirmação e atualiza os dados na tela.
9. As próximas mensagens recebidas no WhatsApp utilizam imediatamente a nova identidade e regras de escopo.
10. O caso de uso é concluído.

## 4. Matriz de Análise de Modos de Falha e Efeitos (FMEA)

| Modo de Falha | Efeito Potencial | Causa Raiz | Mecanismo de Prevenção / Contingência | Severidade |
| :--- | :--- | :--- | :--- | :---: |
| **Alucinação de Modelo Inexistente** | Prometer peça de tablet incompatível para o cliente. | IA Generativa sem restrição de catálogo fechado. | Injeção estrita de catálogo via prompt e validação obrigatória contra `InventoryProvider`. | **Alta** |
| **Auto-Silenciamento em Loop** | Bot silenciar a si mesmo ao interpretar sua própria resposta como intervenção humana. | Webhook da Evolution API reportando `fromMe: true` de envios automatizados. | Tabela `sent_messages` no SQLite filtra todos os IDs de mensagens disparadas pelo bot antes de avaliar handoff. | **Crítica** |
| **Sobrecarga por Rajadas de Mensagens** | Múltiplas respostas desencontradas para um mesmo cliente em segundos. | Usuário do WhatsApp digitando frases quebradas de 2 palavras. | Debounce Buffer assíncrono unifica rajadas ocorridas em janela de 3 segundos em uma única execução. | **Média** |
| **Queda da API de Estoque Externa** | Travamento do atendimento e impossibilidade de cotar produtos. | Instabilidade no Bling ERP ou indisponibilidade temporária do Google Sheets. | Circuit Breaker trip após 3 falhas consecutivas; contingência imediata com espelho local em SQLite. | **Alta** |
| **Criação de Pedidos Falsos / Acidentais** | Expedição separar peças sem confirmação real do cliente. | Cliente mencionando endereço em tom hipotético ou apenas perguntando valor do frete. | Protocolo Two-Phase Commit: estado `WAITING_CONFIRMATION` exige pergunta explícita do bot e afirmação posterior do cliente. | **Crítica** |

---

## 5. Checklist de Verificação de Conformidade Arquitetural

- [x] O vocabulário de respostas segue rigorosamente o limite de 1 a 6 palavras para cotações.
- [x] Rejeição expressa para qualquer menção a celulares ou iPhones (`"Só peças de tablet"`).
- [x] Ausência completa de saudações formais longas, emojis e jargões corporativos de chatbots.
- [x] O transbordo humano é 100% silencioso para o cliente (`reply_text: ""` com alerta sonoro via ntfy).
- [x] Despachos pelo Uber Flash exigem validação em 2 etapas (endereço pré-anotado + confirmação do cliente).
- [x] Contingência offline de catálogo garantida com tempo de resposta inferior a 2 milissegundos via `CachedInventoryProxy`.
- [x] Disjuntor geral de emergência (Master Kill-Switch) operacional via banco SQLite e painel administrativo.
