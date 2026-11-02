"""
Test Suite for CatalogSearchService and Fuzzy Model Resolution.
Validates typo tolerance, alias expansion (T220, T295, NB304, etc.),
and part discrimination (display vs touch vs battery).
"""

from application.use_cases.catalog_search_service import (
    CatalogSearchService,
    levenshtein_distance,
    remove_accents,
    string_similarity,
)
from domain.entities import Product, QualityTier


def test_remove_accents_and_levenshtein():
    assert remove_accents("não é possível módulo") == "nao e possivel modulo"
    assert levenshtein_distance("samsung", "samsung") == 0
    assert levenshtein_distance("samsung", "sansung") == 1
    assert string_similarity("samsung", "sansung") > 0.85


def test_detect_model_alias_exact_and_fuzzy():
    # Modelos Samsung Tablet
    assert CatalogSearchService.detect_model_alias("quanto tá a tela do a7 lite?") == "Tab A7 Lite"
    assert CatalogSearchService.detect_model_alias("tem a tela do t220?") == "Tab A7 Lite"
    assert CatalogSearchService.detect_model_alias("preciso pro sm-t225") == "Tab A7 Lite"
    assert CatalogSearchService.detect_model_alias("tem display do t295") == "Tab A 8.0 (2019)"
    assert CatalogSearchService.detect_model_alias("tela tab a8 x200") == "Tab A8"
    assert CatalogSearchService.detect_model_alias("tela t500") == "Tab A7"

    # Modelos Multilaser
    assert CatalogSearchService.detect_model_alias("touch do multilaser m10a") == "Multilaser M10A"
    assert CatalogSearchService.detect_model_alias("tem vidro pro nb304") == "Multilaser M10A"
    assert CatalogSearchService.detect_model_alias("touch m7s") == "Multilaser M7s"
    assert CatalogSearchService.detect_model_alias("bateria do m7 3g") == "Multilaser M7s"


def test_detect_part_type():
    assert CatalogSearchService.detect_part_type("quanto tá o display?") == "display"
    assert CatalogSearchService.detect_part_type("tem a tela frontar?") == "display"
    assert CatalogSearchService.detect_part_type("só o touch dele") == "touch"
    assert CatalogSearchService.detect_part_type("vidro touch com cabo") == "touch"
    assert CatalogSearchService.detect_part_type("bateria inchou") == "bateria"
    assert CatalogSearchService.detect_part_type("conector de carga quebrou") == "conector"


def test_detect_quality_and_frame():
    q, frame = CatalogSearchService.detect_quality_and_frame("quero a tela original nacional com aro")
    assert q == QualityTier.ORIGINAL_NACIONAL
    assert frame is True

    q2, frame2 = CatalogSearchService.detect_quality_and_frame("paralela china sem carcaça")
    assert q2 == QualityTier.PARALELA_CHINA
    assert frame2 is False


def test_search_best_matches_ranking():
    catalog = [
        Product(
            sku="DISP-SAM-T220-ORIG",
            name="Display Tela Samsung Galaxy Tab A7 Lite T220 T225",
            category="Tablet",
            compatible_models=["T220", "T225"],
            price=140.0,
            stock_quantity=5,
            quality=QualityTier.ORIGINAL_NACIONAL,
            has_frame=True,
        ),
        Product(
            sku="TOUCH-SAM-T295-PAR",
            name="Touch Vidro Samsung Galaxy Tab A 8.0 T290 T295",
            category="Tablet",
            compatible_models=["T290", "T295"],
            price=55.0,
            stock_quantity=10,
            quality=QualityTier.PARALELA_CHINA,
            has_frame=False,
        ),
        Product(
            sku="TOUCH-ML-M10A-PAR",
            name="Touchscreen Multilaser M10A 3G 4G NB304 NB305",
            category="Tablet",
            compatible_models=["M10A", "NB304", "NB305"],
            price=45.0,
            stock_quantity=8,
            quality=QualityTier.PARALELA_CHINA,
            has_frame=False,
        ),
    ]

    # Busca com erro de digitação e gíria de balcão: 'tela t220'
    results = CatalogSearchService.search_best_matches(catalog, "quanto custa a tela do t220?")
    assert len(results) >= 1
    best_product, score = results[0]
    assert best_product.sku == "DISP-SAM-T220-ORIG"
    assert score >= 0.70

    # Busca por codinome Multilaser: 'nb304 touch'
    results_ml = CatalogSearchService.search_best_matches(catalog, "tem o touch pro nb304?")
    assert len(results_ml) >= 1
    best_ml, score_ml = results_ml[0]
    assert best_ml.sku == "TOUCH-ML-M10A-PAR"
