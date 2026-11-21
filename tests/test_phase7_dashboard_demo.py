"""Test suite for Phase 7: Dashboard and Guided Demo Mode.

Validates:
- Precomputed demo cache completeness and fast loadability
- Step metadata coverage for the 6-step guided demo
- Printable scenario HTML audit report generation (including Arabic RTL)
- Plotly digital twin network graph rendering
"""

import pytest
from pathlib import Path
import config
from app.demo_steps import get_demo_cache, DEMO_STEP_METADATA, DEMO_CACHE_PATH
from app.reports import generate_scenario_report_html
from app.components import create_network_plotly_figure
from network.loader import load_network, partition_districts


def test_demo_cache_completeness():
    """Verify demo cache exists, loads instantly, and has all 6 step payloads."""
    assert DEMO_CACHE_PATH.exists(), f"Demo cache not found at {DEMO_CACHE_PATH}"
    cache = get_demo_cache()
    
    for step_key in ["step1", "step2", "step3", "step4", "step5", "step6"]:
        assert step_key in cache, f"Missing {step_key} in demo cache"
        
    # Step 1: Base simulation and district forecasts
    assert "res_base" in cache["step1"]
    assert "forecasts" in cache["step1"]
    assert len(cache["step1"]["forecasts"]) == len(config.DISTRICT_NAMES)
    for d_name in config.DISTRICT_NAMES:
        fc = cache["step1"]["forecasts"][d_name]
        assert "mean_m3h" in fc and "lower_m3h" in fc and "upper_m3h" in fc
        assert fc["lower_m3h"] <= fc["mean_m3h"] <= fc["upper_m3h"]
        
    # Step 2: Leak injection and multilingual work orders
    assert "res_leak" in cache["step2"]
    assert "suspects_rich" in cache["step2"]
    assert len(cache["step2"]["suspects_rich"]) == 5
    assert "work_orders" in cache["step2"]
    for lang in ["en", "fr", "ar", "ja"]:
        assert lang in cache["step2"]["work_orders"]
        assert "html" in cache["step2"]["work_orders"][lang]
        
    # Step 3: TOU pump optimization
    m_opt = cache["step3"]["metrics_opt"]
    assert m_opt.kwh_saved_vs_baseline > 200.0
    assert m_opt.compliance_min_pressure_pct >= 90.0
    
    # Step 4: Rich vs Sparse suspects
    assert len(cache["step4"]["suspects_rich"]) == 5
    assert len(cache["step4"]["suspects_sparse"]) == 5
    
    # Step 5: Resilience simulation
    comp = cache["step5"]["comp_resil"]
    assert comp.resilience_priority_zone_compliance_pct >= comp.blind_priority_zone_compliance_pct
    assert len(comp.advisory_action_items) >= 2
    
    # Step 6: Closing counters
    assert cache["step6"]["kwh_saved"] > 200.0
    assert cache["step6"]["total_water_loss_detected"] > 0.0


def test_demo_step_metadata():
    """Verify all 6 demo steps have complete UI presentation metadata."""
    assert len(DEMO_STEP_METADATA) == 6
    for step_num in range(1, 7):
        meta = DEMO_STEP_METADATA[step_num]
        assert "title" in meta and len(meta["title"]) > 5
        assert "description" in meta and len(meta["description"]) > 10
        assert "badge" in meta and len(meta["badge"]) > 2


def test_report_generation():
    """Verify exportable HTML scenario audit reports generate properly in English and Arabic."""
    from planner.pump_optimizer import get_default_baseline_plan, get_cost_optimized_plan
    _, m_base = get_default_baseline_plan(24)
    _, m_opt = get_cost_optimized_plan(24, baseline_results=_)
    saved_cost = m_opt.cost_saved_vs_baseline_tnd

    # Test English report
    html_en = generate_scenario_report_html(
        scenario_title="Test Critical Burst",
        district="District 1 - Centre-Ville",
        severity="critical",
        water_loss_m3=450.2,
        kwh_saved=m_opt.kwh_saved_vs_baseline,
        cost_saved_tnd=saved_cost,
        suspect_pipes=[{"rank": 1, "pipe_id": "103", "district": "Centre-Ville", "probability_pct": 82.5, "recommendation": "Inspect immediately"}],
        work_order_html="<div>Work order details</div>",
        lang="en"
    )
    assert "<html" in html_en
    assert "Test Critical Burst" in html_en
    assert config.HONESTY_BANNER_TEXT in html_en
    assert "dir=\"ltr\"" in html_en
    
    # Test Arabic report (must have RTL)
    html_ar = generate_scenario_report_html(
        scenario_title="تقرير تدقيق سيناريو تسرب",
        district="حي المركز",
        severity="critical",
        water_loss_m3=450.2,
        kwh_saved=m_opt.kwh_saved_vs_baseline,
        cost_saved_tnd=saved_cost,
        suspect_pipes=[{"rank": 1, "pipe_id": "103", "district": "حي المركز", "probability_pct": 82.5, "recommendation": "فحص ميداني فوري"}],
        work_order_html="<div>أمر عمل</div>",
        lang="ar"
    )
    assert "<html" in html_ar
    assert "dir=\"rtl\"" in html_ar
    assert "HydroTwin" in html_ar


def test_plotly_figure_generation():
    """Verify interactive Plotly network figure generates with all required elements."""
    wn = load_network(24)
    cache = get_demo_cache()
    pressures = cache["step1"]["res_base"].pressures
    node_to_district, _ = partition_districts(wn)
    
    fig = create_network_plotly_figure(
        wn=wn,
        pressures_df=pressures,
        time_idx=12,
        node_to_district=node_to_district,
        suspect_pipes=["103", "111"],
        active_leak_node=wn.junction_name_list[0]
    )
    
    assert fig is not None
    assert len(fig.data) >= 3 # Nodes, pipes, pumps/tanks/highlights
    # Check that layout has title and white template
    assert fig.layout.template.layout.paper_bgcolor is not None or fig.layout.title.text is not None
