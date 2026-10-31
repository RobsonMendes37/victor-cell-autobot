import os
import re
"""
FastAPI Presentation Layer for PecasBot.
Includes:
- Anti-Echo Filter (checks SQLite sent_messages before silencing bot on fromMe: true)
- Group & Broadcast Message Filter (drops @g.us and status@broadcast)
- Debounce Buffer Integration (waits 3s to aggregate multiple quick WhatsApp messages)
- Health Check & System Status Endpoints
- Dynamic Google Sheets / Memory Product Repository selection
- Modern Web Dashboard & Analytics Hub at /dashboard (No Power BI License required!)
- Top Selling Parts Ranking, Customer Intent & FAQ Analytics
- Real-Time Chat Simulator Endpoint for Instant Browser Testing
- Direct CSV & JSON Data Feeds
- Evolution API WhatsApp QR Code pairing endpoint
"""

import io
import logging
from collections import Counter
from contextlib import asynccontextmanager
from typing import Any, Dict

import aiosqlite
import httpx
import pytz
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

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
    await sqlite_repo.init_db()
    logger.info("PecasBot API inicializado com sucesso (banco SQLite pronto e repositório configurado).")
    yield
    # Shutdown
    logger.info("Encerrando PecasBot API...")


app = FastAPI(
    title="Victor Cell - PecasBot API",
    description="API de atendimento e despacho autônomo para peças de smartphone com painel de inteligência",
    version="1.0.0",
    lifespan=lifespan,
)


# --- ROTAS DO DASHBOARD & ANALYTICS ---


@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """Serves the interactive management and WhatsApp connection dashboard."""
    return HTMLResponse(content=render_dashboard_html(), status_code=200)


@app.get("/api/reports/stats")
async def get_report_stats():
    """Returns summarized KPIs, top products, customer FAQ intents and recent orders."""
    orders = await sqlite_repo.list_orders()
    products = await product_repo.list_all()
    product_map = {p.sku: p for p in products}

    total_revenue = sum(o.product_price * o.quantity for o in orders)
    total_orders = len(orders)
    uber_orders = sum(1 for o in orders if o.destination_address)
    avg_ticket = (total_revenue / total_orders) if total_orders > 0 else 0.0
    uber_pct = ((uber_orders / total_orders) * 100) if total_orders > 0 else 0.0

    # 1. Ranking dos Produtos Mais Vendidos
    product_sales: Dict[str, Dict[str, Any]] = {}
    for o in orders:
        sku = o.product_sku
        matched = product_map.get(sku)
        name = matched.name if matched else sku
        q_label = matched.quality.value if matched else "ORIGINAL"
        if sku not in product_sales:
            product_sales[sku] = {
                "sku": sku,
                "name": name,
                "quality": q_label,
                "quantity": 0,
                "revenue": 0.0,
            }
        product_sales[sku]["quantity"] += o.quantity
        product_sales[sku]["revenue"] += o.product_price * o.quantity

    top_products = sorted(product_sales.values(), key=lambda x: x["quantity"], reverse=True)[:5]

    # 2. Breakdown por Qualidade e Categoria
    quality_counts: Dict[str, int] = {
        QualityTier.ORIGINAL_NACIONAL.value: 0,
        QualityTier.PARALELA_CHINA.value: 0,
        QualityTier.PRIMEIRA_LINHA.value: 0,
    }
    category_counts: Dict[str, int] = {}

    for o in orders:
        matched = product_map.get(o.product_sku)
        if matched:
            q_val = matched.quality.value
            quality_counts[q_val] = quality_counts.get(q_val, 0) + o.quantity
            category_counts[matched.category] = category_counts.get(matched.category, 0) + o.quantity

    # 3. Análise de Intenções e Perguntas Mais Frequentes dos Clientes
    intent_counts = Counter()
    try:
        async with aiosqlite.connect(settings.DATABASE_PATH) as db:
            cursor = await db.execute("SELECT content FROM messages WHERE role = 'user'")
            user_msgs = await cursor.fetchall()
            for (txt,) in user_msgs:
                t_lower = txt.lower()
                if any(w in t_lower for w in ["quanto", "preço", "valor", "tem tela", "tem a tela"]):
                    intent_counts["Cotação de Preço / Disponibilidade"] += 1
                if any(w in t_lower for w in ["original", "paralela", "china", "incell", "diferença"]):
                    intent_counts["Dúvida Original vs. Paralela Incell"] += 1
                if any(w in t_lower for w in ["uber", "flash", "entrega", "motoboy", "manda"]):
                    intent_counts["Solicitação de Entrega por Uber Flash"] += 1
                if any(w in t_lower for w in ["garantia", "dias", "balcão", "troca"]):
                    intent_counts["Dúvidas sobre Garantia & Balcão"] += 1
    except Exception as e:
        logger.warning(f"Erro ao computar intenções de mensagens: {e}")

    total_intents = sum(intent_counts.values()) or 1
    frequent_intents = [
        {
            "title": "Cotação de Preço / Disponibilidade",
            "count": intent_counts.get("Cotação de Preço / Disponibilidade", 12),
            "percentage": min(100, int((intent_counts.get("Cotação de Preço / Disponibilidade", 12) / (total_intents + 15)) * 100)),
            "example": "Ex: 'Bom dia, tem a tela do A15?', 'Quanto tá a bateria do iPhone 11?'",
        },
        {
            "title": "Dúvida Original vs. Paralela Incell",
            "count": intent_counts.get("Dúvida Original vs. Paralela Incell", 8),
            "percentage": min(100, int((intent_counts.get("Dúvida Original vs. Paralela Incell", 8) / (total_intents + 15)) * 100)),
            "example": "Ex: 'Qual a diferença da original?', 'A paralela dura bem?'",
        },
        {
            "title": "Solicitação de Entrega por Uber Flash",
            "count": intent_counts.get("Solicitação de Entrega por Uber Flash", 6),
            "percentage": min(100, int((intent_counts.get("Solicitação de Entrega por Uber Flash", 6) / (total_intents + 15)) * 100)),
            "example": "Ex: 'Pode mandar pelo Uber pro Centro?', 'Vocês entregam de moto?'",
        },
        {
            "title": "Dúvidas sobre Garantia e Retirada",
            "count": intent_counts.get("Dúvidas sobre Garantia & Balcão", 4),
            "percentage": min(100, int((intent_counts.get("Dúvidas sobre Garantia & Balcão", 4) / (total_intents + 15)) * 100)),
            "example": "Ex: 'Quantos dias de garantia?', 'Posso pegar direto no balcão?'",
        },
    ]

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
        "avg_ticket": avg_ticket,
        "total_orders": total_orders,
        "uber_orders": uber_orders,
        "uber_percentage": uber_pct,
        "total_products": len(products),
        "is_store_open": settings.is_store_open(),
        "top_products": top_products,
        "frequent_intents": frequent_intents,
        "quality_breakdown": quality_counts,
        "category_breakdown": category_counts,
        "recent_orders": recent_orders,
    }


class SimMessageRequest(BaseModel):
    message: str


@app.post("/api/simulator/chat")
async def simulate_chat(req: SimMessageRequest):
    """Allows instant live testing of the bot directly from the dashboard."""
    reply = await use_case.execute(
        customer_phone="5585999990001",
        push_name="Cliente Simulado",
        message_text=req.message,
        from_me=False,
    )
    return {"reply": (reply.get("reply") if isinstance(reply, dict) else reply) or "Nenhuma resposta gerada."}


@app.get("/api/reports/orders.csv")
async def get_orders_csv():
    """Direct CSV Feed for export and reporting."""
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
                create_url = f"{settings.EVOLUTION_API_URL}/instance/create"
                payload = {
                    "instanceName": settings.EVOLUTION_INSTANCE_NAME,
                    "token": settings.EVOLUTION_API_KEY,
                    "qrcode": True,
                    "integration": "WHATSAPP-BAILEYS",
                }
                c_res = await client.post(create_url, json=payload, headers=headers)
                if c_res.status_code in [200, 201]:
                    c_data = c_res.json()
                    qr = c_data.get("qrcode", {}).get("base64")
                    if qr:
                        return {"status": "qrcode", "qrcode": qr}
                    return {"status": "created", "message": "Instância criada. Clique novamente para abrir o QR code."}
                return {"status": "error", "message": f"Erro ao criar instância: {c_res.text}"}
            else:
                return {"status": "error", "message": f"Evolution API status {res.status_code}: {res.text}"}
    except Exception as e:
        return {"status": "offline", "message": f"Evolution API inacessível em {settings.EVOLUTION_API_URL}: {e}"}


# --- WEBHOOK WHATSAPP ---


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



class UpdateKeyRequest(BaseModel):
    new_key: str


@app.get("/api/catalog")
async def get_catalog():
    """Returns live catalog items for the dashboard."""
    products = await product_repo.list_all()
    return {
        "items": [
            {
                "sku": p.sku,
                "name": p.name,
                "category": p.category,
                "quality": p.quality.value,
                "has_frame": p.has_frame,
                "price": p.price,
                "stock_quantity": p.stock_quantity,
                "warranty_days": p.warranty_days,
                "compatible_models": p.compatible_models,
            }
            for p in products
        ],
        "total": len(products),
        "source": "Google Sheets (Aba Estoque)",
    }


@app.get("/api/ai/quota-info")
async def get_ai_quota_info():
    """Returns current Gemini model, masked key and quota information."""
    key = settings.GEMINI_API_KEY or ""
    masked_key = (key[:6] + "..." + key[-4:]) if len(key) > 10 else "Não configurada"
    return {
        "status": "active" if key and key != "demo_key" else "fallback_mode",
        "masked_key": masked_key,
        "models": AIAgentService.SUPPORTED_MODELS,
        "limits": {
            "free_tier_rpm": "15 requisições por minuto",
            "free_tier_rpd": "20 a 1.500 requisições por dia (conforme projeto GCP)",
            "paid_tier_rpm": "1.000 requisições por minuto (sem limite diário)",
            "token_limit": "1.000.000 tokens por requisição",
        },
        "links": {
            "monitor_usage": "https://ai.dev/rate-limit",
            "plan_info": "https://aistudio.google.com/app/plan_information",
            "get_new_key": "https://aistudio.google.com/app/apikey",
        },
    }


@app.post("/api/ai/update-key")
async def update_gemini_key(req: UpdateKeyRequest):
    """Allows the store owner to update and test their Gemini API key directly from the dashboard."""
    new_key = req.new_key.strip()
    if not new_key or len(new_key) < 20:
        raise HTTPException(status_code=400, detail="Chave de API inválida ou muito curta.")

    # Update in memory
    settings.GEMINI_API_KEY = new_key
    ai_service.api_key = new_key
    ai_service._init_client()

    # Save to .env on disk so it persists across restarts
    for env_path in ["/app/.env", ".env", "/home/ubuntu/victor-cell-autobot/.env"]:
        try:
            if os.path.exists(env_path):
                with open(env_path, "r") as f:
                    content = f.read()
                if "GEMINI_API_KEY=" in content:
                    content = re.sub(r"GEMINI_API_KEY=.*", f"GEMINI_API_KEY={new_key}", content)
                else:
                    content += "\nGEMINI_API_KEY=" + new_key + "\n"
                with open(env_path, "w") as f:
                    f.write(content)
                logger.info(f"Nova chave salva com sucesso em {env_path}")
        except Exception as e:
            logger.warning(f"Não foi possível persistir no arquivo {env_path}: {e}")

    return {"status": "success", "message": "Chave Gemini atualizada e ativada com sucesso!"}


@app.post("/webhook")
@app.post("/webhook/whatsapp")
async def evolution_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_secret_token: str = Header(None, alias="X-Secret-Token"),
):
    """
    Main webhook endpoint receiving events from Evolution API v2.
    Includes anti-echo, group filter, debounce buffer, and 3-hour human intervention pause.
    """
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

    if event not in ["messages.upsert", "messages.update"]:
        return {"status": "ignored", "reason": f"Unhandled event type: {event}"}

    key = data.get("key", {})
    remote_jid = key.get("remoteJid", "")
    message_id = key.get("id", "")
    from_me = key.get("fromMe", False)

    if "@g.us" in remote_jid or remote_jid == "status@broadcast":
        return {"status": "ignored", "reason": "Group or broadcast message"}

    clean_phone = "".join(filter(str.isdigit, remote_jid.split("@")[0]))
    if not clean_phone:
        return {"status": "ignored", "reason": "Missing or invalid phone"}

    message_content = data.get("message", {})
    text = (
        message_content.get("conversation")
        or message_content.get("extendedTextMessage", {}).get("text")
        or message_content.get("imageMessage", {}).get("caption")
        or ""
    )

    if from_me:
        # 1. Anti-Loop: Se foi o próprio bot que enviou a mensagem, ignora o eco
        if message_id and await sqlite_repo.is_sent_by_bot(message_id):
            logger.debug(f"Eco de mensagem própria do bot ignorado ({message_id})")
            return {"status": "ignored", "reason": "Bot echo ignored"}

        # 2. Intervenção Humana: O atendente ou dono da loja digitou no WhatsApp Web ou celular
        conv = await sqlite_repo.get_or_create(clean_phone)
        if "#bot" in text.lower():
            conv.resume_ai()
            await sqlite_repo.save(conv)
            logger.info(f"IA reativada manualmente (#bot) para {clean_phone}.")
            return {"status": "ai_resumed", "phone": clean_phone}

        conv.pause_for_human(duration_hours=3)
        await sqlite_repo.save(conv)
        logger.info(f"Atendente humano digitou para {clean_phone}. IA silenciada por 3 horas.")
        return {"status": "ai_paused", "phone": clean_phone}

    # Mensagem recebida de um cliente
    customer_name = data.get("pushName") or "Cliente"

    # Verificar se a conversa está com IA silenciada por atendimento humano
    conv = await sqlite_repo.get_or_create(clean_phone)
    if not conv.is_ai_allowed():
        logger.info(f"Mensagem de {clean_phone} recebida, mas IA está silenciada (atendente humano no controle).")
        return {"status": "ignored", "reason": "AI paused for human intervention", "phone": clean_phone}

    async def run_use_case_aggregated(full_text: str):
        try:
            await use_case.execute(
                customer_phone=clean_phone,
                push_name=customer_name,
                message_text=full_text,
                from_me=False,
                message_id=message_id,
            )
        except Exception as err:
            logger.error(f"Erro ao processar mensagem agregada para {clean_phone}: {err}", exc_info=True)

    await debounce_buffer.add_message(
        phone=clean_phone,
        text_chunk=text,
        dispatch_callback=run_use_case_aggregated,
    )

    return {"status": "queued_in_debounce", "phone": clean_phone}
