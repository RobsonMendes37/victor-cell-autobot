"""
Google Sheets Product Repository using gspread and Service Account.
Implements ProductRepositoryInterface with in-memory caching to respect Google API quotas.

Expected Google Sheets Layout:
- Row 1: Project Title
- Row 2: Headers (SKU, Produto, Modelos Compatíveis, Categoria, Qualidade, Com Aro, Preço, Estoque, Garantia, Última Alteração)
- Row 3+: Product Data
"""

import logging
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

import gspread
import pytz

from domain.entities import Product, QualityTier, ReservationOrder
from domain.repositories import ProductRepositoryInterface
from infrastructure.config import settings

logger = logging.getLogger("GoogleSheetsRepository")


class GoogleSheetsRepository(ProductRepositoryInterface):
    def __init__(
        self,
        sheet_id: Optional[str] = None,
        credentials_file: str = "credentials.json",
        cache_ttl_seconds: int = 120,
    ):
        self.sheet_id = sheet_id
        self.credentials_file = credentials_file
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cached_products: Dict[str, Product] = {}
        self._last_cache_update: Optional[datetime] = None
        self._client: Optional[gspread.Client] = None

    def _get_client(self) -> Optional[gspread.Client]:
        if self._client:
            return self._client
        if os.path.exists(self.credentials_file):
            try:
                self._client = gspread.service_account(filename=self.credentials_file)
                logger.info(f"Conexão com Google Sheets autenticada via {self.credentials_file}")
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

        client = self._get_client()
        if client and self.sheet_id:
            try:
                sheet = client.open_by_key(self.sheet_id)
                worksheet = sheet.worksheet("Estoque_Catalogo")
                all_values = worksheet.get_all_values()

                # Linha 1 = Título, Linha 2 = Cabeçalhos, Linha 3+ = Dados
                if len(all_values) >= 3:
                    products = {}
                    for row in all_values[2:]:  # Inicia na linha 3 (índice 2)
                        if not row or not row[0].strip():
                            continue
                        try:
                            sku = row[0].strip()
                            name = row[1].strip()
                            models = [m.strip() for m in row[2].split(",") if m.strip()]
                            category = row[3].strip() if len(row) > 3 else "Geral"
                            quality_str = row[4].strip() if len(row) > 4 else "ORIGINAL_NACIONAL"
                            has_frame = (row[5].strip().upper() == "SIM") if len(row) > 5 else False
                            price = (
                                float(row[6].replace("R$", "").replace(",", ".").strip())
                                if len(row) > 6
                                else 0.0
                            )
                            stock = int(row[7].strip()) if len(row) > 7 else 0
                            warranty = int(row[8].strip()) if len(row) > 8 else 90

                            quality_enum = (
                                QualityTier.PARALELA_CHINA
                                if "PARALELA" in quality_str.upper()
                                or "CHINA" in quality_str.upper()
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
                            logger.warning(
                                f"Erro ao processar linha da planilha {row}: {parse_err}"
                            )

                    self._cached_products = products
                    self._last_cache_update = now
                    logger.info(
                        f"Cache de produtos atualizado do Google Sheets ({len(products)} itens carregados)."
                    )
                    return list(self._cached_products.values())
            except Exception as e:
                logger.error(f"Erro ao buscar catálogo do Google Sheets: {e}. Usando cache local.")

        return list(self._cached_products.values())

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
        """Appends a new order row to the 'Logs_Expedicao_PowerBI' tab in Google Sheets."""
        client = self._get_client()
        if client and self.sheet_id:
            try:
                sheet = client.open_by_key(self.sheet_id)
                worksheet = sheet.worksheet("Logs_Expedicao_PowerBI")
                fortaleza_tz = pytz.timezone(settings.STORE_TIMEZONE)
                created_str = order.created_at.astimezone(fortaleza_tz).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
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
                logger.info(
                    f"Pedido #{order.id} registrado com sucesso na aba Logs_Expedicao_PowerBI."
                )
                return True
            except Exception as e:
                logger.error(f"Erro ao gravar log no Google Sheets: {e}")
        return False
