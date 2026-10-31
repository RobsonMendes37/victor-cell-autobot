"""
Google Sheets & Power BI Exporter.
Follows the exact layout specified:
- Row 1: Project Title
- Row 2: Column Headers
- Row 3+: Data rows
Generates both local CSVs (for direct Power BI import) and connects to Google Sheets via gspread.
"""

import csv
import logging
import os
from typing import List

import pytz

from domain.entities import Product, ReservationOrder
from infrastructure.config import settings

logger = logging.getLogger("SheetsExporter")


class SheetsExporter:
    def __init__(self, output_dir: str = "data"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def export_catalog_csv(
        self, products: List[Product], filename: str = "Estoque_Catalogo.csv"
    ) -> str:
        """
        Exports catalog with Title in row 1, headers in row 2, data from row 3.
        """
        filepath = os.path.join(self.output_dir, filename)
        fortaleza_tz = pytz.timezone(settings.STORE_TIMEZONE)

        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            # Linha 1: Título do Projeto
            writer.writerow(
                [
                    "Victor Cell - Controle de Estoque & Catálogo de Peças",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                ]
            )
            # Linha 2: Colunas
            writer.writerow(
                [
                    "SKU",
                    "Produto",
                    "Modelos Compatíveis",
                    "Categoria",
                    "Qualidade / Procedência",
                    "Com Aro",
                    "Preço Balcão (R$)",
                    "Qtd Estoque",
                    "Garantia (Dias)",
                    "Última Alteração",
                ]
            )
            # Linha 3+: Dados
            for p in products:
                dt_str = p.last_updated_at.astimezone(fortaleza_tz).strftime("%Y-%m-%d %H:%M")
                writer.writerow(
                    [
                        p.sku,
                        p.name,
                        ", ".join(p.compatible_models),
                        p.category,
                        p.quality.value,
                        "SIM" if p.has_frame else "NÃO",
                        f"{p.price:.2f}",
                        p.stock_quantity,
                        p.warranty_days,
                        dt_str,
                    ]
                )
        logger.info(f"Catálogo exportado para Power BI em: {filepath}")
        return filepath

    def export_orders_log_csv(
        self, orders: List[ReservationOrder], filename: str = "Logs_Expedicao_PowerBI.csv"
    ) -> str:
        """
        Exports high-level sales and dispatch logs for Power BI.
        Row 1: Title
        Row 2: Headers
        Row 3+: Orders data
        """
        filepath = os.path.join(self.output_dir, filename)
        fortaleza_tz = pytz.timezone(settings.STORE_TIMEZONE)

        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            # Linha 1: Título do Projeto
            writer.writerow(
                [
                    "Victor Cell - Registro de Saídas & Despachos de Peças (Power BI)",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                ]
            )
            # Linha 2: Colunas
            writer.writerow(
                [
                    "ID Pedido",
                    "Data/Hora",
                    "Cliente Nome",
                    "Telefone",
                    "SKU Peça",
                    "Quantidade",
                    "Valor Unitário (R$)",
                    "Endereço Entrega",
                    "Modalidade",
                    "Status",
                    "Validade Reserva",
                ]
            )
            # Linha 3+: Dados
            for o in orders:
                created_str = o.created_at.astimezone(fortaleza_tz).strftime("%Y-%m-%d %H:%M:%S")
                expires_str = o.expires_at.astimezone(fortaleza_tz).strftime("%H:%M")
                writer.writerow(
                    [
                        o.id,
                        created_str,
                        o.customer_name,
                        o.customer_phone,
                        o.product_sku,
                        o.quantity,
                        f"{o.product_price:.2f}",
                        o.destination_address,
                        "UBER_FLASH",
                        o.status.value,
                        expires_str,
                    ]
                )
        logger.info(f"Logs de saída exportados para Power BI em: {filepath}")
        return filepath
