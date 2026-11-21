"""Tests for Phase 6: Multilingual assistant and no-hallucination guardrails."""

import pytest
from app.multilingual import (
    generate_work_order,
    answer_structured_query,
    get_language_container_css,
    LANGUAGE_NAMES,
)

def test_language_css_rtl_and_fonts():
    css_ar = get_language_container_css("ar")
    assert "direction: rtl" in css_ar
    assert "text-align: right" in css_ar
    
    css_ja = get_language_container_css("ja")
    assert "Noto Sans JP" in css_ja
    assert "direction: ltr" in css_ja
    
    css_en = get_language_container_css("en")
    assert "direction: ltr" in css_en

def test_work_order_all_languages():
    suspects = [
        {"rank": 1, "pipe_id": "125", "district": "District 1 - Centre-Ville", "probability_pct": 52.3},
        {"rank": 2, "pipe_id": "131", "district": "District 1 - Centre-Ville", "probability_pct": 28.1},
    ]
    for lang in ["en", "fr", "ar", "ja"]:
        res = generate_work_order(
            has_leak=True,
            severity="critical",
            district="District 1 - Centre-Ville",
            suspect_pipes=suspects,
            water_loss_m3h=42.5,
            lang=lang
        )
        assert res["has_leak"] is True
        assert res["top_pipe_id"] == "125"
        assert res["lang"] == lang
        assert "multilingual-card" in res["html"]

def test_no_hallucination_when_no_leak_reported():
    """CRITICAL GUARDRAIL: When has_leak=False, the assistant MUST NOT mention or invent a leak."""
    context_healthy = {
        "has_leak": False,
        "suspect_pipes": [],
        "district": None,
        "kwh_saved": 292.1,
        "cost_saved_tnd": 33.6,
    }
    
    for lang in ["en", "fr", "ar", "ja"]:
        order = generate_work_order(has_leak=False, lang=lang)
        assert order["has_leak"] is False
        assert "Pipe 125" not in order["html"]
        assert "ALERT" not in order["title"] if lang == "en" else True
        
        # Test Q&A questions over healthy status
        ans_district = answer_structured_query("Which district loses water?", context_healthy, lang=lang)
        ans_pipes = answer_structured_query("Which pipes to inspect?", context_healthy, lang=lang)
        
        if lang == "en":
            assert "balanced" in ans_district.lower() or "normal" in ans_district.lower()
            assert "no pipe inspections are required" in ans_pipes.lower()
        elif lang == "fr":
            assert "normal" in ans_district.lower() or "équilibre" in ans_district.lower()
            assert "aucune inspection" in ans_pipes.lower()

def test_structured_qa_intents():
    context_leak = {
        "has_leak": True,
        "district": "District 2 - El Menzah",
        "suspect_pipes": [
            {"rank": 1, "pipe_id": "145", "probability_pct": 65.4},
            {"rank": 2, "pipe_id": "147", "probability_pct": 21.0},
        ],
        "kwh_saved": 292.1,
        "cost_saved_tnd": 33.6,
        "resilience_priority_compliance": 92.3,
    }
    
    # English queries
    assert "District 2 - El Menzah" in answer_structured_query("which district loses the most water", context_leak, "en")
    assert "Pipe 145" in answer_structured_query("which pipes to inspect first?", context_leak, "en")
    assert "92.3%" in answer_structured_query("what happens if pump 10 stops?", context_leak, "en")
    assert "292.1 kWh" in answer_structured_query("what are the energy savings?", context_leak, "en")
    
    # French query
    assert "District 2 - El Menzah" in answer_structured_query("quel quartier a une fuite ?", context_leak, "fr")
    
    # Arabic query
    assert "District 2 - El Menzah" in answer_structured_query("أي حي يخسر الماء ؟", context_leak, "ar")
    
    # Japanese query
    assert "District 2 - El Menzah" in answer_structured_query("どの地区で水が失われていますか？", context_leak, "ja")
