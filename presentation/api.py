"""
FastAPI Presentation Layer for PecasBot.
Includes:
- Anti-Echo Filter (checks SQLite sent_messages before silencing bot on fromMe: true)
- Group & Broadcast Message Filter (drops @g.us and status@broadcast)
- Debounce Buffer Integration (waits 3s to aggregate multiple quick WhatsApp messages)
- Health Check & System Status Endpoints
- Dynamic Google Sheets / Memory Product Repository selection
"""

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request, Response, status

from application.use_cases.debounce_buffer import DebounceBuffer
from application.use_cases.process_incoming_message import ProcessIncomingMessageUseCase
from infrastructure.config import settings
from infrastructure.gateways.evolution_gateway import EvolutionGateway
from infrastructure.repositories.google_sheets_repository import GoogleSheetsRepository
from infrastructure.repositories.memory_product_repository import MemoryProductRepository
from infrastructure.repositories.sqlite_repository import SqliteRepository
from infrastructure.services.agent_service import AIAgentService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PecasBotAPI")

# Initialize singletons
if settings.GOOGLE_SHEET_ID:
    product_repo = GoogleSheetsRepository(
        sheet_id=settings.GOOGLE_SHEET_ID,
        api_key=settings.GOOGLE_SHEETS_API_KEY,
    )
    logger.info(f"Usando GoogleSheetsRepository com Sheet ID: {settings.GOOGLE_SHEET_ID}")
else:
    product_repo = MemoryProductRepository()
    logger.info("Usando MemoryProductRepository padrão")

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
    sqlite_repo=sqlite_repo,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize SQLite database
    sqlite_repo.init_db()
    logger.info("PecasBot API inicializado com sucesso (banco SQLite pronto e repositório configurado).")
    yield
    # Shutdown
    logger.info("Encerrando PecasBot API...")


app = FastAPI(
    title="Victor Cell - PecasBot API",
    description="API de atendimento e despacho autônomo para peças de smartphone",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint for Docker container liveness and monitoring."""
    local_time = settings.get_local_now().strftime("%Y-%m-%d %H:%M:%S")
    open_status = settings.is_store_open()
    return {
        "status": "healthy",
        "store": "Victor Cell Peças",
        "local_time_fortaleza": local_time,
        "is_store_open": open_status,
        "sheet_integration": bool(settings.GOOGLE_SHEET_ID),
    }


@app.get("/products")
async def list_products():
    """Returns currently available products in the active repository."""
    return await product_repo.list_all()


@app.post("/webhook")
async def evolution_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_secret_token: str = Header(None, alias="X-Secret-Token"),
):
    """
    Main webhook endpoint receiving events from Evolution API v2.
    Includes:
    - Secret Token verification (if configured in settings)
    - Group message filter (@g.us)
    - Status/Broadcast filter (status@broadcast)
    - Anti-echo self-silence filter
    - Debounce aggregation for customer typing multiple sequential messages
    """
    # 1. Validar token de segurança se configurado
    if settings.WEBHOOK_SECRET_TOKEN and x_secret_token != settings.WEBHOOK_SECRET_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de segurança do webhook inválido.",
        )

    try:
        body: Dict[str, Any] = await request.json()
    except Exception as e:
        logger.error(f"Erro ao ler JSON do webhook: {e}")
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    event = body.get("event")
    data = body.get("data", {})

    # Processamos apenas eventos de mensagens recebidas/atualizadas
    if event not in ["messages.upsert", "messages.update"]:
        return {"status": "ignored", "reason": f"Unhandled event type: {event}"}

    key = data.get("key", {})
    remote_jid = key.get("remoteJid", "")
    message_id = key.get("id", "")
    from_me = key.get("fromMe", False)

    # 2. Filtrar grupos e status broadcast
    if "@g.us" in remote_jid or remote_jid == "status@broadcast":
        return {"status": "ignored", "reason": "Group or broadcast message"}

    # Extrair texto da mensagem
    message_content = data.get("message", {})
    text = (
        message_content.get("conversation")
        or message_content.get("extendedTextMessage", {}).get("text")
        or message_content.get("imageMessage", {}).get("caption")
        or ""
    )

    # 3. Tratamento de mensagens enviadas pela própria loja (fromMe: true)
    if from_me:
        # Verificar se é echo da mensagem enviada pelo próprio bot
        if sqlite_repo.is_bot_sent_message(message_id):
            return {"status": "ignored", "reason": "Bot echo ignored"}

        # Se foi digitado por atendente humano no WhatsApp Web/celular: pausar a IA por 3 horas
        phone = remote_jid.split("@")[0]
        conv = await sqlite_repo.get_by_phone(phone)
        if conv:
            conv.pause_ai(hours=3)
            await sqlite_repo.save(conv)
            logger.info(f"Atendente humano assumiu chat com {phone}. IA pausada por 3h.")
            return {"status": "ai_paused", "phone": phone}

        return {"status": "ignored", "reason": "Store outgoing message"}

    # Extrair metadados do remetente
    phone = remote_jid.split("@")[0]
    customer_name = data.get("pushName") or "Cliente"

    # 4. Agendamento com Debounce Buffer (espera 3s para agregar frases picadas)
    async def run_use_case_aggregated(full_text: str):
        try:
            await use_case.execute(
                customer_phone=phone,
                customer_name=customer_name,
                message_text=full_text,
                from_me=False,
                message_id=message_id,
            )
        except Exception as err:
            logger.error(f"Erro ao processar mensagem agregada para {phone}: {err}", exc_info=True)

    await debounce_buffer.add_message(
        phone=phone,
        text_chunk=text,
        dispatch_callback=run_use_case_aggregated,
    )

    return {"status": "queued_in_debounce", "phone": phone}
