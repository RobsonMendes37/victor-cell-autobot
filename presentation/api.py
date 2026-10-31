"""
FastAPI Presentation Layer with SQLite Persistence & Group Filters.
Exposes Webhooks for Evolution API v2, health checks, and local testing.
"""

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from application.use_cases.debounce_buffer import DebounceBuffer
from application.use_cases.process_incoming_message import ProcessIncomingMessageUseCase
from infrastructure.config import settings
from infrastructure.gateways.evolution_gateway import EvolutionGateway
from infrastructure.repositories.memory_product_repository import MemoryProductRepository
from infrastructure.repositories.sqlite_repository import SqliteRepository
from infrastructure.services.agent_service import AIAgentService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PecasBotAPI")

# Initialize singletons
product_repo = MemoryProductRepository()
sqlite_repo = SqliteRepository(settings.DATABASE_PATH)
gateway = EvolutionGateway(message_recorder=sqlite_repo.record_sent_message)
ai_service = AIAgentService()
debounce_buffer = DebounceBuffer(wait_seconds=settings.DEBOUNCE_WAIT_SECONDS)

use_case = ProcessIncomingMessageUseCase(
    conversation_repo=sqlite_repo,
    product_repo=product_repo,
    order_repo=sqlite_repo,
    messaging_gateway=gateway,
    ai_service=ai_service,
    sqlite_repo=sqlite_repo
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializa tabelas SQLite no startup
    await sqlite_repo.init_db()
    logger.info("Banco SQLite inicializado com sucesso.")
    yield


app = FastAPI(
    title="Victor Cell - PecasBot API",
    description="Assistente Autônomo de Vendas e Despacho de Peças para Tablets e Celulares via WhatsApp",
    version="1.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "service": "Victor Cell - PecasBot API",
        "status": "online",
        "is_store_open": settings.is_store_open(),
        "database": settings.DATABASE_PATH
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "store_open": settings.is_store_open(),
        "timezone": settings.STORE_TIMEZONE,
        "evolution_gateway": settings.EVOLUTION_API_URL,
        "caixa_staff_phone": settings.CAIXA_STAFF_PHONE
    }


@app.get("/products")
async def list_products():
    """Lists current catalog with in-memory prices and stock."""
    return await product_repo.list_all()


@app.get("/orders")
async def list_orders():
    """Lists current reservation/dispatch orders stored in SQLite."""
    return await sqlite_repo.list_orders()


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Webhook receiver for Evolution API v2.
    Listens to 'messages.upsert' events.
    Filters out groups (@g.us) and status broadcasts.
    """
    try:
        body = await request.json()
        event = body.get("event")
        data = body.get("data", {})

        # Só processa eventos de novas mensagens
        if event != "messages.upsert":
            return {"status": "IGNORED_EVENT", "event": event}

        key = data.get("key", {})
        remote_jid = key.get("remoteJid", "")
        from_me = key.get("fromMe", False)
        push_name = data.get("pushName", "Cliente")
        message_id = key.get("id")
        message_obj = data.get("message", {})

        # 1. Filtro de Grupos e Status: Ignora mensagens de grupos (@g.us) e status broadcast
        if "@g.us" in remote_jid or "status@broadcast" in remote_jid:
            return {"status": "IGNORED_GROUP_OR_STATUS"}

        # 2. Extrai texto de mensagem simples, conversa ou legenda de imagem
        message_text = (
            message_obj.get("conversation") or
            message_obj.get("extendedTextMessage", {}).get("text") or
            message_obj.get("imageMessage", {}).get("caption") or
            ""
        )

        # Se for áudio, sinaliza
        if "audioMessage" in message_obj:
            message_text = "[Áudio do cliente no WhatsApp]"

        if not message_text.strip() and not from_me:
            return {"status": "EMPTY_MESSAGE"}

        # 3. Executa o caso de uso de negócio
        result = await use_case.execute(
            customer_phone=remote_jid,
            message_text=message_text,
            from_me=from_me,
            push_name=push_name,
            message_id=message_id
        )
        return {"received": True, "result": result}

    except Exception as e:
        logger.error(f"Erro ao processar webhook do WhatsApp: {e}", exc_info=True)
        return {"status": "ERROR", "message": str(e)}


@app.post("/simulate")
async def simulate_incoming_message(payload: Dict[str, Any]):
    """
    Endpoint de testes interativos locais.
    Payload: {"phone": "5585991234567", "message": "tem tela do a15 original?", "from_me": false}
    """
    phone = payload.get("phone", "5585991234567")
    message = payload.get("message", "")
    from_me = payload.get("from_me", False)
    name = payload.get("name", "Técnico Teste")
    msg_id = payload.get("id", "sim_msg_01")

    result = await use_case.execute(
        customer_phone=phone,
        message_text=message,
        from_me=from_me,
        push_name=name,
        message_id=msg_id
    )
    return result
