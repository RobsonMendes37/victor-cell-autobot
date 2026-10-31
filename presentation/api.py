"""
FastAPI Presentation Layer for PecasBot.
Includes:
- Anti-Echo Filter (checks SQLite sent_messages before silencing bot on fromMe: true)
- Group & Broadcast Message Filter (drops @g.us and status@broadcast)
- Debounce Buffer Integration (waits 3s to aggregate multiple quick WhatsApp messages)
- Health Check & System Status Endpoints
- Dynamic Google Sheets / Memory Product Repository selection
- Modern Web Dashboard & Power BI Analytics Hub at /dashboard
- Direct CSV & JSON Data Feeds for Power BI Desktop
- Evolution API WhatsApp QR Code pairing endpoint
"""

import io
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict

import httpx
import pytz
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, StreamingResponse

from application.use_cases.debounce_buffer import DebounceBuffer
from application.use_cases.process_incoming_message import ProcessIncomingMessageUseCase
from domain.entities import QualityTier
from infrastructure.config import settings
from infrastructure.gateways.evolution_gateway import EvolutionGateway
from infrastructure.repositories.google_sheets_repository import GoogleSheetsRepository
from infrastructure.repositories.memory_product_repository import MemoryProductRepository
from infrastructure.repositories.sheets_exporter import SheetsExporter
from infrastructure.repositories.sqlite_repository import SqliteRepository
from infrastructure.services.agent_service import AIAgentService
from presentation.dashboard import render_dashboard_html

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
exporter = SheetsExporter()

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
    description="API de atendimento e despacho autônomo para peças de smartphone com painel Power BI",
    version="1.0.0",
    lifespan=lifespan,
)


# --- ROTAS VISUAIS E POWER BI DASHBOARD ---


@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """Serves the interactive Power BI management and WhatsApp connection dashboard."""
    return HTMLResponse(content=render_dashboard_html(), status_code=200)


@app.get("/api/reports/stats")
async def get_report_stats():
    """Returns summarized KPIs and recent orders for the dashboard and analytics."""
    orders = await sqlite_repo.list_orders()
    products = await product_repo.list_all()

    total_revenue = sum(o.product_price * o.quantity for o in orders)
    uber_orders = sum(1 for o in orders if o.destination_address)

    # Breakdown por Qualidade e Categoria
    quality_counts: Dict[str, int] = {
        QualityTier.ORIGINAL_NACIONAL.value: 0,
        QualityTier.PARALELA_CHINA.value: 0,
        QualityTier.PRIMEIRA_LINHA.value: 0,
    }
    category_counts: Dict[str, int] = {}

    for o in orders:
        matched = next((p for p in products if p.sku == o.product_sku), None)
        if matched:
            q_val = matched.quality.value
            quality_counts[q_val] = quality_counts.get(q_val, 0) + o.quantity
            category_counts[matched.category] = category_counts.get(matched.category, 0) + o.quantity

    fortaleza_tz = pytz.timezone(settings.STORE_TIMEZONE)
    recent_orders = []
    for o in orders[:25]:
        recent_orders.append({
            "id": o.id,
            "created_at": o.created_at.astimezone(fortaleza_tz).strftime("%d/%m %H:%M"),
            "customer_name": o.customer_name,
            "customer_phone": o.customer_phone,
            "product_sku": o.product_sku,
            "quantity": o.quantity,
            "product_price": o.product_price,
            "destination_address": o.destination_address,
            "status": o.status.value,
            "expires_at": o.expires_at.astimezone(fortaleza_tz).strftime("%H:%M"),
        })

    return {
        "total_revenue": total_revenue,
        "total_orders": len(orders),
        "uber_orders": uber_orders,
        "total_products": len(products),
        "is_store_open": settings.is_store_open(),
        "quality_breakdown": quality_counts,
        "category_breakdown": category_counts,
        "recent_orders": recent_orders,
    }


@app.get("/api/reports/orders.csv")
async def get_orders_csv():
    """
    Direct CSV Feed for Power BI Desktop Web connector.
    Strictly follows:
    - Line 1: Title
    - Line 2: Headers
    - Line 3+: Data rows
    """
    orders = await sqlite_repo.list_orders()
    csv_path = exporter.export_orders_log_csv(orders)

    with open(csv_path, "rb") as f:
        content = f.read()

    return StreamingResponse(
        io.BytesIO(content),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=Logs_Expedicao_PowerBI.csv"},
    )


@app.post("/api/reports/sync-sheets")
async def sync_google_sheets():
    """Forces cache refresh from Google Sheets."""
    if isinstance(product_repo, GoogleSheetsRepository):
        product_repo._last_cache_update = None
        products = await product_repo.list_all()
        return {"status": "synced", "total_items": len(products)}
    return {"status": "ignored", "reason": "Not using GoogleSheetsRepository"}


# --- WHATSAPP PAIRING VIA EVOLUTION API ---


@app.get("/api/whatsapp/qrcode")
async def get_whatsapp_qrcode():
    """Fetches connection status or QR code from Evolution API v2."""
    url = f"{settings.EVOLUTION_API_URL}/instance/connect/{settings.EVOLUTION_INSTANCE_NAME}"
    headers = {"apikey": settings.EVOLUTION_API_KEY}
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            res = await client.get(url, headers=headers)
            if res.status_code == 200:
                data = res.json()
                # A Evolution API v2 retorna base64 do QRCode em data.get('base64') ou data.get('code')
                qr_base64 = data.get("base64") or data.get("qrcode", {}).get("base64")
                if qr_base64:
                    if not qr_base64.startswith("data:image"):
                        qr_base64 = f"data:image/png;base64,{qr_base64}"
                    return {"status": "qrcode", "qrcode": qr_base64}
                state = data.get("instance", {}).get("state")
                if state == "open":
                    return {"status": "connected"}
                return {"status": "waiting", "data": data}
            elif res.status_code == 404:
                # Criar a instância se ainda não existir
                create_url = f"{settings.EVOLUTION_API_URL}/instance/create"
                payload = {
                    "instanceName": settings.EVOLUTION_INSTANCE_NAME,
                    "token": settings.EVOLUTION_API_KEY,
                    "qrcode": True,
                }
                c_res = await client.post(create_url, json=payload, headers=headers)
                if c_res.status_code in [200, 201]:
                    c_data = c_res.json()
                    qr = c_data.get("qrcode", {}).get("base64")
                    if qr:
                        return {"status": "qrcode", "qrcode": qr}
                    return {"status": "created", "message": "Instância criada. Clique novamente para gerar o QR code."}
                return {"status": "error", "message": f"Erro ao criar instância: {c_res.text}"}
            else:
                return {"status": "error", "message": f"Evolution API status {res.status_code}: {res.text}"}
    except Exception as e:
        return {"status": "offline", "message": f"Evolution API inacessível em {settings.EVOLUTION_API_URL}: {e}"}


# --- ENDPOINTS PADRÃO ---


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
@app.post("/webhook/whatsapp")
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
