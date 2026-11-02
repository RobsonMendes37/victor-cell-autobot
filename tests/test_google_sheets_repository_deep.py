"""
Deep Tests for GoogleSheetsRepository row parsing, stock logic, and order appending.
"""


import pytest

from domain.entities import QualityTier
from infrastructure.repositories.google_sheets_repository import GoogleSheetsRepository


def test_parse_rows_all_variations():
    repo = GoogleSheetsRepository(sheet_id="mock_sheet")

    sample_rows = [
        # Headers to skip
        ["SKU", "Nome", "Modelos", "Categoria", "Qualidade", "Aro", "Preco", "Estoque", "Garantia", "Obs", "Gaveta"],
        ["Estoque Catálogo Victor Cell"],
        [],
        # Row 1: Original Nacional com Aro e Estoque Numérico
        ["TAB-X200-ORIG", "Tela Tab A8 X200", "X200, X205", "Samsung", "ORIGINAL_NACIONAL", "SIM", "R$ 150,00", "15", "90", "", "Gaveta A1"],
        # Row 2: Original China Sem Aro e Checkbox TRUE
        ["TAB-T295-CHINA", "Tela Tab A 8.0", "T290, T295", "Samsung", "ORIGINAL CHINA", "NAO", "R$ 90,00", "TRUE", "90", "", "Gaveta B1"],
        # Row 3: Primeira Linha e Checkbox SIM
        ["TAB-M7-1LINHA", "Touch M7 3G", "M7, T2040", "Multilaser", "PRIMEIRA LINHA", "N", "45.00", "SIM", "90", "", ""],
        # Row 4: Paralela China Esgotada (FALSE / ESGOTADO)
        ["TAB-M8-CHIN", "Touch M8 4G", "M8", "Multilaser", "PARALELA", "0", "35", "ESGOTADO", "90", "", ""],
        # Row 5: Fallback de estoque inválido
        ["TAB-FALLBACK", "Peça Fallback", "M10", "Outros", "OUTRA", "", "10", "INV", "", "", ""],
    ]

    products = repo._parse_rows(sample_rows)
    assert len(products) == 5

    p1 = products["TAB-X200-ORIG"]
    assert p1.quality == QualityTier.ORIGINAL_NACIONAL
    assert p1.has_frame is True
    assert p1.stock_quantity == 15
    assert p1.has_stock is True
    assert p1.location == "Gaveta A1"

    p2 = products["TAB-T295-CHINA"]
    assert p2.quality == QualityTier.ORIGINAL_CHINA
    assert p2.has_frame is False
    assert p2.stock_quantity == 1
    assert p2.has_stock is True

    p3 = products["TAB-M7-1LINHA"]
    assert p3.quality == QualityTier.PRIMEIRA_LINHA
    assert p3.price == 45.0

    p4 = products["TAB-M8-CHIN"]
    assert p4.quality == QualityTier.PARALELA_CHINA
    assert p4.has_stock is False
    assert p4.stock_quantity == 0

    p5 = products["TAB-FALLBACK"]
    assert p5.quality == QualityTier.ORIGINAL_NACIONAL
    assert p5.has_stock is True


@pytest.mark.asyncio
async def test_sheets_crud_methods():
    repo = GoogleSheetsRepository(sheet_id="mock_sheet")
    # Seed
    repo._cached_products = repo._parse_rows([
        ["SKU-TEST", "Touch Teste", "T290", "Samsung", "ORIGINAL", "N", "50", "10"],
    ])

    # get_by_sku
    item = await repo.get_by_sku("SKU-TEST")
    assert item is not None
    assert item.price == 50.0

    # search
    found = await repo.search("T290")
    assert len(found) == 1

    # decrement and increment
    ok_dec = await repo.decrement_stock("SKU-TEST", 3)
    assert ok_dec is True
    assert (await repo.get_by_sku("SKU-TEST")).stock_quantity == 7

    ok_inc = await repo.increment_stock("SKU-TEST", 3)
    assert ok_inc is True
    assert (await repo.get_by_sku("SKU-TEST")).stock_quantity == 10

    # update_stock
    await repo.update_stock("SKU-TEST", 25)
    assert (await repo.get_by_sku("SKU-TEST")).stock_quantity == 25
