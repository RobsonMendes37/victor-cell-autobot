# RFC-004: Guia de Infraestrutura, DevOps & Implantação
## Oracle Cloud Always Free, Docker Compose & Operação 24/7

---

## 1. Topologia de Infraestrutura na Oracle Cloud

A hospedagem aproveita a instância **Oracle Cloud Always Free (ARM Ampere)** já disponível na conta do desenvolvedor (12 GB RAM, 2 OCPUs, Ubuntu Linux).

```
 Internet (WhatsApp / Clientes)
               │
               ▼ HTTPS (Porta 443)
┌─────────────────────────────────────────────────────────────┐
│ Oracle Cloud VM (Instância Always Free - Ubuntu)            │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ Caddy / Nginx (SSL Automático Let's Encrypt)        │   │
│   └───────────────┬──────────────────────┬──────────────┘   │
│                   │ :8080                │ :8000            │
│                   ▼                      ▼                  │
│       ┌──────────────────────┐  ┌───────────────────────┐  │
│       │ Evolution API v2     │  │ PecasBot (FastAPI)    │  │
│       │ (Gateway WhatsApp)   │  │ (Cérebro da Aplicação)│  │
│       └──────────┬───────────┘  └───────────┬───────────┘  │
│                  │                          │               │
│                  ▼                          ▼               │
│       ┌──────────────────────┐  ┌───────────────────────┐  │
│       │ Redis (Sessões WA)   │  │ Cache de Estoque /    │  │
│       │                      │  │ Google Sheets API     │  │
│       └──────────────────────┘  └───────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Configuração do `docker-compose.yml`

Abaixo está a especificação completa para orquestrar todos os serviços de forma isolada e com reinicialização automática (`restart: unless-stopped`):

```yaml
version: '3.8'

services:
  # 1. Banco de Cache/Sessão para a Evolution API
  redis:
    image: redis:7-alpine
    container_name: pecas_redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - bot_network

  # 2. Gateway do WhatsApp (Evolution API v2 - Open Source)
  evolution-api:
    image: atendai/evolution-api:v2.1.2
    container_name: pecas_evolution
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      - SERVER_URL=https://api-wa.seudominio.com
      - AUTHENTICATION_API_KEY=ChaveSecretaSuperForte123
      - CACHE_REDIS_ENABLED=true
      - CACHE_REDIS_URI=redis://redis:6379
      - WEBHOOK_GLOBAL_URL=http://pecas-backend:8000/webhook/whatsapp
      - WEBHOOK_GLOBAL_ENABLED=true
      - WEBHOOK_EVENTS_MESSAGES_UPSERT=true
    volumes:
      - evolution_instances:/evolution/instances
    depends_on:
      - redis
    networks:
      - bot_network

  # 3. Backend Python (FastAPI + Gemini + Google Sheets)
  pecas-backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: pecas_backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY_1=AIzaSy...
      - GEMINI_API_KEY_2=AIzaSy...
      - GOOGLE_SHEETS_CREDENTIALS_JSON=/app/credentials.json
      - GOOGLE_SHEET_ID=1A2B3C4D5E...
      - EVOLUTION_API_URL=http://evolution-api:8080
      - EVOLUTION_API_KEY=ChaveSecretaSuperForte123
      - CAIXA_STAFF_PHONE_GROUP=5585999999999-group@g.us
      - STORE_OPENING_TIME=08:30
      - STORE_CLOSING_TIME=18:00
    volumes:
      - ./backend/credentials.json:/app/credentials.json:ro
      - ./backend/data:/app/data
    depends_on:
      - evolution-api
    networks:
      - bot_network

volumes:
  redis_data:
  evolution_instances:

networks:
  bot_network:
    driver: bridge
```

---

## 3. Segurança e Regras de Rede (Oracle Cloud Firewall)

Na Oracle Cloud, além do firewall interno do Ubuntu (`ufw`), é obrigatório liberar as portas na **Ingress Security List** da VCN:
1. **Portas Abertas Publicamente:**
   * `80` (HTTP - Redirecionamento Caddy/Nginx)
   * `443` (HTTPS - Tráfego Seguro SSL)
2. **Portas Privadas (Acesso apenas local via Docker Network):**
   * `8080` (Evolution API protegida por API Key)
   * `8000` (FastAPI Webhooks)
   * `6379` (Redis)

---

## 4. Runbook Operacional: Emparelhamento e Manutenção

### 4.1 Passo a Passo para Conectar o WhatsApp da Loja
1. Com os containers rodando na VM da Oracle, acesse o painel da Evolution API ou dispare a criação da instância:
   ```bash
   curl -X POST https://api-wa.seudominio.com/instance/create \
     -H "apikey: ChaveSecretaSuperForte123" \
     -H "Content-Type: application/json" \
     -d '{"instanceName": "pecas-loja-01", "qrcode": true}'
   ```
2. O terminal ou a interface exibirá o **QR Code ASCII**.
3. O dono da loja abre o WhatsApp no celular, vai em **Aparelhos Conectados $\rightarrow$ Conectar um Aparelho** e lê o código.
4. Pronto! A conexão está persistida no volume `evolution_instances`. Mesmo que o servidor reinicie, a conexão restabelece automaticamente.

### 4.2 Monitoramento de Logs em Tempo Real
Para acompanhar as mensagens e o raciocínio da IA em tempo real:
```bash
# Ver os logs do cérebro FastAPI
docker compose logs -f pecas-backend

# Ver o tráfego do gateway do WhatsApp
docker compose logs -f evolution-api
```
