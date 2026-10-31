"""
Google Sheets Product Repository.
Supports BOTH:
1. Google Sheets API Key (via direct REST API v4 HTTP requests) for reading catalog.
2. Google Service Account (via credentials.json & gspread) for reading catalog + appending order logs.
Includes in-memory cache to respect Google API quotas.
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
        self.sheet_id = sheet_id
        self.api_key = api_key or getattr(settings, "GOOGLE_SHEETS_API_KEY", None)
        self.credentials_file = credentials_file
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cached_products: Dict[str, Product] = {}
        self._last_cache_update: Optional[datetime] = None
        self._client: Optional[gspread.Client] = None

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
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.sheet_id}/values/Estoque_Catalogo!A3:J?key={self.api_key}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    data = res.json()
                    rows = data.get("values", [])
                    products = self._parse_rows(rows)
                    logger.info(f"Catálogo lido com sucesso via Chave de API ({len(products)} itens).")
                    return products
                else:
                    logger.warning(f"Google Sheets API retornou status {res.status_code}: {res.text}")
        except Exception as e:
            logger.error(f"Erro ao consultar Google Sheets via API Key: {e}")
        return {}

    async def _fetch_via_service_account(self, client: gspread.Client) -> Dict[str, Product]:
        """Fetches catalog using gspread and Service Account."""
        try:
            sheet = client.open_by_key(self.sheet_id)
            worksheet = sheet.worksheet("Estoque_Catalogo")
            all_values = worksheet.get_all_values()
            if len(all_values) >= 3:
                return self._parse_rows(all_values[2:])
        except Exception as e:
            logger.error(f"Erro ao consultar Google Sheets via gspread: {e}")
        return {}

    def _parse_rows(self, rows: List[List[str]]) -> Dict[str, Product]:
        products = {}
        for row in rows:
            if not row or not row[0].strip():
                continue
            try:
                sku = row[0].strip()
                name = row[1].strip()
                models = [m.strip() for m in row[2].split(",") if m.strip()]
                category = row[3].strip() if len(row) > 3 else "Geral"
                quality_str = row[4].strip() if len(row) > 4 else "ORIGINAL_NACIONAL"
                has_frame = (row[5].strip().upper() == "SIM") if len(row) > 5 else False
                price = float(row[6].replace("R$", "").replace(",", ".").strip()) if len(row) > 6 else 0.0
                stock = int(row[7].strip()) if len(row) > 7 else 0
                warranty = int(row[8].strip()) if len(row) > 8 else 90

                quality_enum = (
                    QualityTier.PARALELA_CHINA
                    if "PARALELA" in quality_str.upper() or "CHINA" in quality_str.upper()
                    else (
                        QualityTier.PRIMEIRA_LINHA
                        if "PRIMEIRA" in quality_str.upper() or "1" in quality_str
                        else QualityTier.ORIGINAL_NACIONAL
                    )
                )

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
                sheet = client.open_by_key(self.sheet_id)
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
                worksheet.append_row(row_data)
                logger.info(f"Pedido #{order.id} registrado com sucesso no Google Sheets.")
                return True
            except Exception as e:
                logger.error(f"Erro ao gravar log no Google Sheets via service account: {e}")
        return False
