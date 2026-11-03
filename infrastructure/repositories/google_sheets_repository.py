"""
Google Sheets Product Repository.
Supports BOTH:
1. Google Sheets API Key (via direct REST API v4 HTTP requests) for reading catalog.
2. Google Service Account (via credentials.json & gspread) for reading catalog + appending order logs.
Includes in-memory cache to respect Google API quotas, auto-tab detection, and flexible header parsing.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

import gspread
import httpx
import pytz

from domain.entities import Product, QualityTier, ReservationOrder
from domain.repositories import ProductRepositoryInterface
from infrastructure.config import settings

logger = logging.getLogger("GoogleSheetsRepository")


class GoogleSheetsRepository(ProductRepositoryInterface):
    def __init__(
        self,
        sheet_id: Optional[str] = None,
        api_key: Optional[str] = None,
        credentials_file: str = "credentials.json",
        cache_ttl_seconds: int = 120,
    ):
        self.sheet_id = sheet_id or getattr(settings, "GOOGLE_SHEET_ID", None)
        self.api_key = api_key or getattr(settings, "GOOGLE_SHEETS_API_KEY", None)
        self.credentials_file = credentials_file
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cached_products: Dict[str, Product] = {}
        self._last_cache_update: Optional[datetime] = None
        self._client: Optional[gspread.Client] = None
        self._seed_default_catalog()

    def _seed_default_catalog(self) -> None:
        """Seed default products so bot works immediately even if sheet is empty or being edited."""
        sample_items = [
            Product(
                sku="TEL-SAM-A15-ORIG",
                name="Tela Frontal Samsung Galaxy A15",
                category="Tela Frontal",
                compatible_models=["Galaxy A15", "A15 4G", "A15 5G", "SM-A155F", "SM-A156B"],
                quality=QualityTier.ORIGINAL_NACIONAL,
                has_frame=True,
                price=190.00,
                stock_quantity=4,
                warranty_days=90,
            ),
            Product(
                sku="TEL-SAM-A15-CHIN",
                name="Tela Frontal Samsung Galaxy A15",
                category="Tela Frontal",
                compatible_models=["Galaxy A15", "A15 4G", "A15 5G", "SM-A155F", "SM-A156B"],
                quality=QualityTier.PARALELA_CHINA,
                has_frame=False,
                price=95.00,
                stock_quantity=12,
                warranty_days=30,
            ),
            Product(
                sku="CON-MOT-G22",
                name="Conector de Carga Placa Sub Motorola Moto G22",
                category="Conector de Carga",
                compatible_models=["Moto G22", "XT2231"],
                quality=QualityTier.ORIGINAL_NACIONAL,
                has_frame=False,
                price=35.00,
                stock_quantity=8,
                warranty_days=90,
            ),
            Product(
                sku="BAT-IPH-11",
                name="Bateria Apple iPhone 11 Foxconn Saúde 100%",
                category="Bateria",
                compatible_models=["iPhone 11", "A2111", "A2223"],
                quality=QualityTier.PRIMEIRA_LINHA,
                has_frame=False,
                price=130.00,
                stock_quantity=5,
                warranty_days=90,
            ),
        ]
        for item in sample_items:
            self._cached_products[item.sku] = item

    def _get_service_client(self) -> Optional[gspread.Client]:
        if self._client:
            return self._client
        if os.path.exists(self.credentials_file):
            try:
                self._client = gspread.service_account(filename=self.credentials_file)
                logger.info(f"Conexão com Google Sheets autenticada via Service Account ({self.credentials_file})")
                return self._client
            except Exception as e:
                logger.error(f"Erro ao autenticar service account do Google Sheets: {e}")
        return None

    async def list_all(self) -> List[Product]:
        """Lists products, refreshing cache from Google Sheets if TTL expired."""
        now = datetime.now(timezone.utc)
        if (
            self._cached_products
            and self._last_cache_update
            and (now - self._last_cache_update).total_seconds() < self.cache_ttl_seconds
        ):
            return list(self._cached_products.values())

        if not self.sheet_id:
            return list(self._cached_products.values())

        # Método 1: Leitura via Chave de API direta (Google Sheets REST API v4)
        if self.api_key:
            products = await self._fetch_via_api_key()
            if products:
                self._cached_products = products
                self._last_cache_update = now
                return list(self._cached_products.values())

        # Método 2: Leitura via Service Account (gspread)
        client = self._get_service_client()
        if client:
            products = await self._fetch_via_service_account(client)
            if products:
                self._cached_products = products
                self._last_cache_update = now
                return list(self._cached_products.values())

        return list(self._cached_products.values())

    async def _fetch_via_api_key(self) -> Dict[str, Product]:
        """Fetches catalog using Google Sheets API Key (REST API v4)."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 1. Descobrir o nome da aba automaticamente
                meta_url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.sheet_id}?key={self.api_key}"
                meta_res = await client.get(meta_url)
                if meta_res.status_code != 200:
                    logger.warning(f"Google Sheets metadata status {meta_res.status_code}: {meta_res.text}")
                    return {}

                meta_data = meta_res.json()
                sheets = meta_data.get("sheets", [])
                tab_names = [s.get("properties", {}).get("title") for s in sheets if s.get("properties")]
                if not tab_names:
                    return {}

                target_tab = "Estoque_Catalogo" if "Estoque_Catalogo" in tab_names else tab_names[0]

                # 2. Buscar valores da aba identificada
                url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.sheet_id}/values/{target_tab}!A1:N?key={self.api_key}"
                res = await client.get(url)
                if res.status_code == 200:
                    data = res.json()
                    rows = data.get("values", [])
                    products = self._parse_rows(rows)
                    if products:
                        logger.info(f"Catálogo lido com sucesso da aba '{target_tab}' ({len(products)} itens).")
                        return products
                    else:
                        logger.info(f"Aba '{target_tab}' está vazia ou sem produtos válidos ainda.")
                else:
                    logger.warning(f"Google Sheets API retornou status {res.status_code}: {res.text}")
        except Exception as e:
            logger.error(f"Erro ao consultar Google Sheets via API Key: {e}")
        return {}

    async def _fetch_via_service_account(self, client: gspread.Client) -> Dict[str, Product]:
        """Fetches catalog using gspread and Service Account."""
        try:
            sheet = client.open_by_key(str(self.sheet_id or ""))
            worksheet = None
            try:
                worksheet = sheet.worksheet("Estoque_Catalogo")
            except Exception:
                worksheet = sheet.get_worksheet(0)

            if worksheet:
                all_values = worksheet.get_all_values()
                return self._parse_rows(all_values)
        except Exception as e:
            logger.error(f"Erro ao consultar Google Sheets via gspread: {e}")
        return {}

    def _parse_rows(self, rows: List[List[str]]) -> Dict[str, Product]:
        products = {}
        for row in rows:
            if not row or not row[0].strip():
                continue
            first_cell = row[0].strip().lower()

            # Pular linhas de título ou de cabeçalho
            if first_cell in ["sku", "código", "codigo", "item", "id"] or any("produto" in c.lower() for c in row):
                continue
            if len(row) < 3 or first_cell.startswith("catálogo") or first_cell.startswith("estoque"):
                continue

            try:
                sku = row[0].strip()
                name = row[1].strip()
                models = [m.strip() for m in row[2].split(",") if m.strip()]
                category = row[3].strip() if len(row) > 3 else "Geral"
                quality_str = row[4].strip() if len(row) > 4 else "ORIGINAL_NACIONAL"
                has_frame = (row[5].strip().upper() in ["SIM", "TRUE", "S", "1"]) if len(row) > 5 else False
                price = float(row[6].replace("R$", "").replace(",", ".").strip()) if len(row) > 6 else 0.0

                # Suporte inteligente a Booleano de Estoque (Checkbox TRUE/FALSE, SIM/NÃO, ou Contagem numérica)
                stock_raw = row[7].strip() if len(row) > 7 else "SIM"
                s_upper = stock_raw.upper()
                if s_upper in ["TRUE", "SIM", "S", "TEM", "DISPONIVEL", "DISPONÍVEL", "1", "V"]:
                    has_stock = True
                    stock = 1
                elif s_upper in ["FALSE", "NAO", "NÃO", "N", "ESGOTADO", "SEM ESTOQUE", "0", "ACABOU", ""]:
                    has_stock = False
                    stock = 0
                else:
                    try:
                        num = int(float(stock_raw.replace(",", ".")))
                        has_stock = (num > 0)
                        stock = max(num, 0)
                    except ValueError:
                        has_stock = True
                        stock = 1

                warranty = int(row[8].strip()) if len(row) > 8 and row[8].strip().isdigit() else 90
                location = row[10].strip() if len(row) > 10 and row[10].strip() else None

                q_upper = quality_str.upper()
                if "ORIGINAL_CHINA" in q_upper or "ORIGINAL CHINA" in q_upper:
                    quality_enum = QualityTier.ORIGINAL_CHINA
                elif "PARALELA" in q_upper or "CHINA" in q_upper:
                    quality_enum = QualityTier.PARALELA_CHINA
                elif "PRIMEIRA" in q_upper or "1" in q_upper:
                    quality_enum = QualityTier.PRIMEIRA_LINHA
                else:
                    quality_enum = QualityTier.ORIGINAL_NACIONAL

                prod = Product(
                    sku=sku,
                    name=name,
                    category=category,
                    compatible_models=models,
                    quality=quality_enum,
                    has_frame=has_frame,
                    price=price,
                    stock_quantity=stock,
                    warranty_days=warranty,
                    has_stock=has_stock,
                    location=location,
                )
                products[sku] = prod
            except Exception as parse_err:
                logger.warning(f"Erro ao processar linha da planilha {row}: {parse_err}")
        return products

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        products = await self.list_all()
        for p in products:
            if p.sku == sku:
                return p
        return None

    async def search(
        self,
        query: str,
        quality: Optional[QualityTier] = None,
        has_frame: Optional[bool] = None,
    ) -> List[Product]:
        products = await self.list_all()
        q = query.lower().strip()
        matches = []
        for p in products:
            if q in p.name.lower() or any(q in m.lower() for m in p.compatible_models):
                if quality and p.quality != quality:
                    continue
                if has_frame is not None and p.has_frame != has_frame:
                    continue
                matches.append(p)
        return matches

    async def update_stock(self, sku: str, new_quantity: int) -> bool:
        if sku in self._cached_products:
            self._cached_products[sku].stock_quantity = new_quantity
            return True
        return False

    async def decrement_stock(self, sku: str, quantity: int = 1) -> bool:
        if sku in self._cached_products:
            current = self._cached_products[sku].stock_quantity
            if current >= quantity:
                self._cached_products[sku].stock_quantity = current - quantity
                return True
        return False

    async def increment_stock(self, sku: str, quantity: int = 1) -> bool:
        if sku in self._cached_products:
            self._cached_products[sku].stock_quantity += quantity
            return True
        return False

    async def append_order_log(self, order: ReservationOrder) -> bool:
        """Appends a new order row to the 'Logs_Expedicao_PowerBI' tab via Service Account."""
        client = self._get_service_client()
        if client and self.sheet_id:
            try:
                sheet = client.open_by_key(str(self.sheet_id or ""))
                worksheet = sheet.worksheet("Logs_Expedicao_PowerBI")
                fortaleza_tz = pytz.timezone(settings.STORE_TIMEZONE)
                created_str = order.created_at.astimezone(fortaleza_tz).strftime("%Y-%m-%d %H:%M:%S")
                expires_str = order.expires_at.astimezone(fortaleza_tz).strftime("%H:%M")

                row_data = [
                    order.id,
                    created_str,
                    order.customer_name,
                    order.customer_phone,
                    order.product_sku,
                    order.quantity,
                    f"{order.product_price:.2f}",
                    order.destination_address,
                    "UBER_FLASH",
                    order.status.value,
                    expires_str,
                ]
                worksheet.append_row([str(x) for x in row_data])
                logger.info(f"Pedido #{order.id} registrado com sucesso no Google Sheets.")
                return True
            except Exception as e:
                logger.error(f"Erro ao gravar log no Google Sheets via service account: {e}")
        return False

    async def append_product(self, product: Product) -> bool:
        """Appends a single product to the 'Estoque_Catalogo' tab via Service Account."""
        client = self._get_service_client()
        self._cached_products[product.sku] = product
        if client and self.sheet_id:
            try:
                sheet = client.open_by_key(str(self.sheet_id or ""))
                try:
                    worksheet = sheet.worksheet("Estoque_Catalogo")
                except Exception:
                    worksheet = sheet.get_worksheet(0)

                qual_val = product.quality.value if hasattr(product.quality, "value") else str(product.quality)
                row_data = [
                    product.sku,
                    product.name,
                    ", ".join(product.compatible_models) if product.compatible_models else product.name,
                    product.category,
                    qual_val,
                    "SIM" if product.has_frame else "NÃO",
                    f"{product.price:.2f}",
                    str(product.stock_quantity),
                    str(product.warranty_days),
                    f"{product.cost_price:.2f}" if product.cost_price else "0.00",
                    product.location or "GAVETA-A1",
                ]
                worksheet.append_row(row_data)
                logger.info(f"Peça {product.sku} ({product.name}) gravada no Google Sheets.")
                return True
            except Exception as e:
                logger.error(f"Erro ao inserir peça no Google Sheets: {e}")
        return True

    async def append_products_batch(self, products: List[Product]) -> int:
        """Appends a batch of products to the Google Sheets spreadsheet."""
        client = self._get_service_client()
        count = 0
        rows_to_append = []
        for product in products:
            self._cached_products[product.sku] = product
            qual_val = product.quality.value if hasattr(product.quality, "value") else str(product.quality)
            row_data = [
                product.sku,
                product.name,
                ", ".join(product.compatible_models) if product.compatible_models else product.name,
                product.category,
                qual_val,
                "SIM" if product.has_frame else "NÃO",
                f"{product.price:.2f}",
                str(product.stock_quantity),
                str(product.warranty_days),
                f"{product.cost_price:.2f}" if product.cost_price else "0.00",
                product.location or "GAVETA-A1",
            ]
            rows_to_append.append(row_data)
            count += 1

        if client and self.sheet_id and rows_to_append:
            try:
                sheet = client.open_by_key(str(self.sheet_id or ""))
                try:
                    worksheet = sheet.worksheet("Estoque_Catalogo")
                except Exception:
                    worksheet = sheet.get_worksheet(0)
                worksheet.append_rows(rows_to_append)
                logger.info(f"{len(rows_to_append)} peças adicionadas em lote no Google Sheets.")
            except Exception as e:
                logger.error(f"Erro ao inserir lote no Google Sheets: {e}")
        return count

