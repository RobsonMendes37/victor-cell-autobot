# 📱 Guia Visual de Cenários de Uso e Testes
### Victor Cell — Assistente Inteligente de Vendas e Despacho via WhatsApp

> **Objetivo deste documento:** Apresentar de forma visual, simples e não técnica como o sistema atende os clientes no dia a dia, como ele reage em cada situação e o que acontece nos bastidores da loja física.

---

## 🧭 Mapa Rápido dos Cenários

| # | Cenário | O que o Cliente faz | O que o Bot faz | O que acontece na Loja |
| :-: | :--- | :--- | :--- | :--- |
| **1** | **Cotação de Peça** | Pergunta o preço de uma tela | Informa valores (Original vs Paralela) e garantias | Guarda a peça na memória |
| **2** | **"Separa por favor"** | Pede pra separar sem passar endereço | Confirma a peça e pede o endereço completo | Não cria pedido incompleto |
| **3** | **Pedido de Uber Flash** | Envia o endereço completo de entrega | Confirma o pedido e avisa sobre o Pix/Uber | Toca alerta no WhatsApp do caixa |
| **4** | **Dúvida de Frete** | Pergunta só quanto custa o Uber | Explica como funciona o cálculo | Não cria pedido indevido |
| **5** | **Foto de Peça / Etiqueta** | Manda foto de etiqueta ou peça quebrada | Identifica o modelo exato pela imagem | Busca a peça certa no estoque |
| **6** | **Mensagem de Áudio** | Manda áudio gravado na bancada | Ouve o áudio e responde em texto cordial | Atendimento sem fricção |
| **7** | **Dono Assume a Conversa** | Dono digita no chat pelo celular | O bot se cala automaticamente por 3h | O humano assume o controle |
| **8** | **Fora do Expediente** | Manda mensagem domingo ou à noite | Tira dúvidas e agenda para a manhã seguinte | Não promete entrega com loja fechada |
| **9** | **Painel Power BI** | Dono abre o dashboard no computador | Exibe gráficos de faturamento e peças | Dados atualizados automaticamente |

---

## 🔍 Detalhamento Visual dos Cenários

### Cenário 1: Cotação Simples de Peça
O técnico está na bancada com o aparelho do cliente e quer saber se a loja tem a peça e qual o valor.

```text
[TÉCNICO] ➔ "Opa, bom dia! Tem tela do Galaxy A15?"
   │
   ▼
[BOT VICTOR CELL] ➔ "Opa, bom dia meu patrão! Temos o A15 sim! Temos duas opções na bancada:
                     1. Original Nacional (com aro): R$ 190,00 (90 dias de garantia)
                     2. Paralela China Incell (sem aro): R$ 95,00
                     Qual das duas você prefere que a gente separe pro seu serviço?"
   │
   ▼
[BASTIDORES] ➔ O sistema registra que o cliente está interessado na tela do A15.
               Se ele disser "separa essa" em seguida, o bot já sabe exatamente qual é!
```

---

### Cenário 2: Cliente pede para separar sem passar o endereço
O cliente decide comprar, mas manda apenas uma mensagem rápida. O bot não se confunde e pede os dados de entrega.

```text
[TÉCNICO] ➔ "Separa uma original por favor!"
   │
   ▼
[BOT VICTOR CELL] ➔ "Show de bola, meu amigo! Já deixo separada aqui no balcão.
                     Você vem retirar aqui na loja ou quer que a gente chame o Uber Flash?
                     Se for pra mandar por Uber, me passa o endereço completo com número e bairro!"
   │
   ▼
[BASTIDORES] ➔ O bot entende que "por favor" é cortesia, não endereço.
               Nenhum alerta falso é disparado até os dados estarem completos.
```

---

### Cenário 3: Confirmação de Entrega via Uber Flash (Alerta no Caixa)
O cliente envia o endereço de entrega para despacho imediato.

```text
[TÉCNICO] ➔ "Manda por Uber Flash pra Rua Floriano Peixoto, 1250 - Centro"
   │
   ▼
[BOT VICTOR CELL] ➔ "Fechado, patrão! Já anotei aqui: Rua Floriano Peixoto, 1250 - Centro.
                     Os meninos do caixa já vão cotar a corrida no app do Uber Flash
                     e em instantes te mandam o valor do frete e a chave Pix, beleza?"
   │
   ├────────────────────────────────────────────────────────────────────────┐
   ▼                                                                        ▼
[ESTOQUE DO SISTEMA]                                          [WHATSAPP DO CAIXA / BALCÃO]
Baixa automática de 1 unidade                                 Alerta urgente toca no celular dos rapazes:
da Tela A15 Original no estoque                               "🚨 NOVO DESPACHO VIA UBER FLASH!
                                                               • Cliente: Marcos Celulares (85 99123-4567)
                                                               • Peça: Tela A15 Original (R$ 190,00)
                                                               • Endereço: Rua Floriano Peixoto, 1250
                                                               • Validade da Reserva: 2 Horas
                                                               👉 Ação: Cotar Uber no app e mandar o Pix!"
```

---

### Cenário 4: Pergunta sobre Frete sem Intenção de Compra
O cliente quer apenas ter uma noção do valor de entrega antes de fechar serviço com o cliente dele.

```text
[CLIENTE] ➔ "Quanto custa mais ou menos o Uber até a Messejana?"
   │
   ▼
[BOT VICTOR CELL] ➔ "Opa meu amigo! O valor do Uber Flash a gente calcula na hora exata de mandar,
                     direto pelo app, porque a taxa varia de acordo com o trânsito e o horário.
                     Quando você for fechar a peça, é só mandar o endereço completo que os
                     meninos do caixa calculam a rota certinho pra você, sem acréscimo nenhum!"
   │
   ▼
[BASTIDORES] ➔ Nenhuma peça é reservada e nenhum alerta é enviado ao caixa.
```

---

### Cenário 5: Cliente envia Foto da Peça ou da Etiqueta (Multimodal)
O técnico não sabe o código do modelo do tablet ou está na dúvida se a carcaça/conector é compatível.

```text
[TÉCNICO] ➔ [Envia foto da tampa traseira do tablet mostrando o código 'SM-X200']
   │
   ▼
[INTELIGÊNCIA GEMINI VISION] ➔ Analisa a foto, dá zoom na inscrição e lê: "Samsung Tab A8 SM-X200"
   │
   ▼
[BOT VICTOR CELL] ➔ "Opa, vi aqui na foto! É o Samsung Tab A8 (modelo SM-X200).
                     A gente tem a tela frontal 1ª linha por R$ 140,00 e o conector
                     de carga por R$ 25,00. Qual dessas peças você tá precisando?"
```

---

### Cenário 6: Cliente envia Mensagem de Áudio
O técnico está com as mãos ocupadas soldando na bancada e grava um áudio no WhatsApp.

```text
[TÉCNICO] ➔ 🎙️ [Áudio de 6 segundos: "Fala parceiro, tem conector do Tab A8 pronta entrega?"]
   │
   ▼
[INTELIGÊNCIA GEMINI AUDIO] ➔ Escuta o áudio, filtra o barulho de fundo e entende a dúvida técnica.
   │
   ▼
[BOT VICTOR CELL] ➔ "Opa meu patrão! Temos sim a pronta entrega! O conector do Tab A8 tá saindo a R$ 25,00.
                     Vai precisar de quantas unidades pra bancada hoje?"
```

---

### Cenário 7: O Dono da Loja Intervém no Chat (Silenciamento Automático)
O cliente pede um desconto especial e o dono decide negociar pessoalmente pelo celular.

```text
[CLIENTE] ➔ "Se eu levar 3 telas dessa, você consegue fazer por R$ 160 cada?"
   │
   ▼
[DONO DA LOJA DIGITA NO CELULAR] ➔ "Opa meu amigo, sou o Victor! Deixa comigo que fecho as 3 por R$ 170 pra você!"
   │
   ▼
[BOT VICTOR CELL DETECTA] ➔ "O dono começou a falar no WhatsApp. Silenciando IA por 3 horas nesta conversa."
   │
   ▼
[CLIENTE RESPONDE] ➔ "Fechado Victor, pode mandar!"
   │
   ▼
[BOT PERMANECE EM SILÊNCIO] ➔ A IA não se intromete e deixa o dono concluir a venda.
   │
   ▼
[DONO DIGITA #bot] ➔ O dono envia o comando secreto e a IA volta a atender no piloto automático.
```

---

### Cenário 8: Mensagem Fora do Horário Comercial (Domingo ou Noite)
Um cliente manda mensagem no sábado à noite ou domingo com a loja física fechada.

```text
[CLIENTE (Domingo 21h)] ➔ "Tem bateria do A15 original? Separa uma aí!"
   │
   ▼
[BOT VICTOR CELL] ➔ "Show de bola, meu patrão! Temos a bateria original do A15 sim (R$ 110,00).
                     Como nossa expedição física já encerrou o expediente por hoje, já deixei
                     o seu pedido na fila prioritária de amanhã!
                     Às 08:30 em ponto os meninos do caixa cotam o Uber Flash e te mandam
                     o Pix para despachar logo na primeira hora, combinado?"
```

---

### Cenário 9: Painel de Controle e Gestão (Power BI)
Tudo o que acontece nas conversas vira inteligência de vendas para o proprietário da loja.

```text
              [CONVERSAS DO WHATSAPP]
                        │
                        ▼ (Registrado automaticamente)
        ┌───────────────────────────────────────────┐
        │ 📁 data/Logs_Expedicao_PowerBI.csv        │
        │ 📁 data/Estoque_Catalogo.csv              │
        └─────────────────────┬─────────────────────┘
                              │
                              ▼ Conecta direto
                  ┌───────────────────────┐
                  │   📊 PAINEL POWER BI   │
                  └───────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
[Peças Mais Vendidas]   [Faturamento Diário]   [Bairros c/ mais Uber]
Telas A15 lideram       R$ 1.850,00 em pedidos Centro e Messejana
com 42% das saídas      fechados via bot       concentram 68% dos envios
```

---

## 💡 Como Testar Tudo Isso na Prática?

Você pode testar todos esses cenários com apenas 1 comando no terminal da máquina:

```bash
cd /home/robson/Projetos_Desenvolvimento/victor-cell/pecasbot-api
.venv/bin/python test_bot.py
```

O script executará cada um desses 8 passos com mensagens reais e mostrará os alertas gerados para o balcão e os arquivos prontos para o Power BI!
