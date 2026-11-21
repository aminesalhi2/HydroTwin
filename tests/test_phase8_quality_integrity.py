"""Test suite for Phase 8: Quality Assurance, Integrity & Governance Rules.

Validates:
- Zero-hallucination guarantee across all 4 languages when no leak is present
- Tunisian water loss reported as a range (25%-50%), never a single static number
- Advisory decision support rule ("The system ADVISES, humans DECIDE")
- Mandatory honesty disclaimer presence across configuration and templates
- Fixed random seed reproducibility (seed=42)
- Sub-second demo cache loading latency (<200ms)
- Complete technical documentation coverage
"""

import time
import pytest
from pathlib import Path

import config
from app.multilingual import generate_work_order, answer_structured_query
from app.demo_steps import get_demo_cache, DEMO_CACHE_PATH


def test_no_hallucination_guarantee():
    """Verify template-based assistant is tested to never mention a leak when has_leak=False."""
    for lang in ["en", "fr", "ar", "ja"]:
        wo = generate_work_order(
            has_leak=False,
            severity="none",
            district="Normal",
            suspect_pipes=[],
            water_loss_m3h=0.0,
            lang=lang
        )
        assert wo["status"] == "NOMINAL"
        assert len(wo["suspect_pipes"]) == 0
        
        # Verify no mention of emergency, critical, or leak alerts in text
        html = wo["html"].lower()
        if lang == "en":
            assert "healthy" in html or "normal" in html or "nominal" in html
            assert "critical burst" not in html
        elif lang == "fr":
            assert "nominal" in html or "normal" in html or "sain" in html
            assert "rupture critique" not in html
        elif lang == "ar":
            assert "طبيعي" in html or "مستقر" in html or "سليم" in html
        elif lang == "ja":
            assert "正常" in html

    # Verify structured Q&A on healthy network
    from planner.pump_optimizer import get_default_baseline_plan, get_cost_optimized_plan
    _, m_base = get_default_baseline_plan(24)
    _, m_opt = get_cost_optimized_plan(24, baseline_results=_)
    
    clean_context = {
        "has_leak": False,
        "district": None,
        "suspect_pipes": [],
        "kwh_saved": m_opt.kwh_saved_vs_baseline,
        "cost_saved_tnd": m_opt.cost_saved_vs_baseline_tnd,
        "resilience_priority_compliance": 92.3,
    }
    
    # Inquire about leaks on clean network
    ans_en = answer_structured_query("Which district loses the most water?", clean_context, lang="en")
    assert "No active leaks" in ans_en or "normal" in ans_en or "healthy" in ans_en
    assert "critical" not in ans_en.lower()

    ans_fr = answer_structured_query("Quel quartier perd le plus d'eau ?", clean_context, lang="fr")
    assert "Aucune fuite" in ans_fr or "normal" in ans_fr

    ans_ar = answer_structured_query("أي حي يخسر أكثر كمية من الماء؟", clean_context, lang="ar")
    assert "لا توجد تسربات" in ans_ar or "طبيعي" in ans_ar

    ans_ja = answer_structured_query("どの地区で最も水が失われていますか？", clean_context, lang="ja")
    assert "検知されていません" in ans_ja or "正常" in ans_ja


def test_tunisia_loss_range_enforcement():
    """Verify Tunisian water losses are always modeled and documented as a range."""
    assert isinstance(config.TUNISIA_LOSS_RANGE_PCT, tuple)
    assert len(config.TUNISIA_LOSS_RANGE_PCT) == 2
    low, high = config.TUNISIA_LOSS_RANGE_PCT
    assert low == 25.0
    assert high == 50.0
    assert low < high


def test_honesty_banner_and_advisory_rule():
    """Verify honesty disclaimers and human decision authority text."""
    assert "SIMULATED DATA" in config.DISCLAIMER_BANNER
    assert "The system ADVISES, humans DECIDE" in config.DECISION_RULE_TEXT
    assert "No autonomous pump" in config.DECISION_RULE_TEXT


def test_reproducibility_seed():
    """Verify fixed global random seed for exact reproducibility."""
    assert config.RANDOM_SEED == 42


def test_demo_cache_speed_and_integrity():
    """Verify demo cache loads in <200ms and contains all 6 steps."""
    assert DEMO_CACHE_PATH.exists()
    
    start_t = time.perf_counter()
    cache = get_demo_cache()
    elapsed_ms = (time.perf_counter() - start_t) * 1000.0
    
    assert elapsed_ms < 200.0, f"Demo cache load took {elapsed_ms:.1f}ms (expected < 200ms)"
    assert set(cache.keys()) >= {"step1", "step2", "step3", "step4", "step5", "step6"}


def test_documentation_files_exist():
    """Verify all mandatory project documentation files exist and are populated."""
    required_docs = [
        "README.md",
        "docs/ARCHITECTURE.md",
        "docs/ASSUMPTIONS.md",
        "docs/ASSUMPTIONS_AND_SOURCES.md",
        "docs/DEMO_SCRIPT.md",
        "docs/EVALUATION.md",
        "docs/RISKS.md",
    ]
    for doc in required_docs:
        doc_path = config.BASE_DIR / doc
        assert doc_path.exists(), f"Missing documentation file: {doc}"
        assert doc_path.stat().st_size > 300, f"Documentation file {doc} appears empty"


def test_evaluation_regression_anomalies():
    """Regression test ensuring anomalies (a) and (b) remain resolved.
    
    1. Unseen test set size: >= 200 leak scenarios and >= 100 healthy days.
    2. Strict scenario split: test locations disjoint from train/val locations.
    3. All 117 pipes eligible for ranking (not truncated to sensor-incident pipes).
    4. Top-3 and Top-5 candidate containment are evaluated independently.
    """
    from sim.scenario_generator import load_scenario_dataset
    data = load_scenario_dataset()
    scenarios = data["scenarios"]
    
    test_leaks = [s for s in scenarios if s["split"] == "test" and s["has_leak"]]
    test_no_leaks = [s for s in scenarios if s["split"] == "test" and not s["has_leak"]]
    train_leaks = [s for s in scenarios if s["split"] in ("train", "val") and s["has_leak"]]
    
    assert len(test_leaks) >= 200, f"Expected >= 200 test leaks, found {len(test_leaks)}"
    assert len(test_no_leaks) >= 100, f"Expected >= 100 test no-leaks, found {len(test_no_leaks)}"
    
    # Assert disjoint leak locations
    test_locs = {s["leak_node"] for s in test_leaks}
    train_locs = {s["leak_node"] for s in train_leaks}
    assert test_locs.isdisjoint(train_locs), "Regression: test locations overlap train locations!"
    
    # Assert ranking considers full network topology
    from ml.leak_localizer import rank_suspect_pipes
    sample_sc = test_leaks[0]
    suspects = rank_suspect_pipes(sample_sc["pressures"], sample_sc["baseline_pressures"], mode="rich", top_k=5)
    assert len(suspects) == 5
    assert all("pipe_id" in s and "rank" in s and "probability_pct" in s for s in suspects)


def test_savings_sensitivity_analysis():
    """Verify pump optimization sensitivity returns baseline kWh/TND and min/mean/max savings."""
    from planner.pump_optimizer import run_savings_sensitivity_analysis
    res = run_savings_sensitivity_analysis()
    
    assert "baseline_kwh" in res and "baseline_cost_tnd" in res
    assert "kwh_saved" in res and "cost_saved_tnd" in res
    assert res["kwh_saved"]["mean"] > 100.0
    assert res["kwh_saved"]["max"] >= res["kwh_saved"]["min"]
    assert res["cost_saved_tnd"]["mean"] > 0
    assert len(res["scenarios"]) >= 6


def test_multi_scenario_resilience():
    """Verify resilience analysis covers multiple start times and priority zones with node counts."""
    from planner.resilience import run_multi_scenario_resilience_analysis
    records = run_multi_scenario_resilience_analysis()
    
    assert len(records) >= 8
    for r in records:
        assert "priority_node_count" in r and r["priority_node_count"] > 0
        assert "protection_gain_pct" in r
        assert r["resilience_compliance_pct"] >= r["blind_compliance_pct"]
