"""Tests for Phase 5: Pump schedule optimization and resilience planning."""

import pytest
import config
from planner.pump_optimizer import get_default_baseline_plan, get_cost_optimized_plan
from planner.resilience import run_resilience_simulation

def test_default_baseline_plan():
    res_def, metrics_def = get_default_baseline_plan(24)
    assert metrics_def.total_kwh > 4000
    assert metrics_def.total_cost_tnd > 1000
    assert metrics_def.avg_tariff_tnd_per_kwh > 0.20
    assert metrics_def.compliance_min_pressure_pct > 90.0
    assert metrics_def.tank_levels_preserved is True
    
    # Assert end-of-day stored volume >= start volume (volume m3 compared per requirement)
    assert metrics_def.total_storage_end_m3 >= metrics_def.total_storage_start_m3 - 10.0
    t_start = res_def.pressures.index[0]
    t_end = res_def.pressures.index[-1]
    for t_name in ["1", "2", "3"]:
        assert res_def.pressures.loc[t_end, t_name] >= res_def.pressures.loc[t_start, t_name] - 0.25
    assert "ADVISES" in config.DECISION_RULE_TEXT

def test_cost_optimized_plan_savings_and_constraints():
    res_def, metrics_def = get_default_baseline_plan(24)
    res_opt, metrics_opt = get_cost_optimized_plan(24, baseline_results=res_def)
    
    # Optimized plan saves energy and money vs default
    assert metrics_opt.kwh_saved_vs_baseline > 0, f"Expected kWh savings, got: {metrics_opt.kwh_saved_vs_baseline}"
    assert metrics_opt.cost_saved_vs_baseline_tnd > 0, f"Expected TND savings, got: {metrics_opt.cost_saved_vs_baseline_tnd}"
    assert metrics_opt.total_kwh < metrics_def.total_kwh
    assert metrics_opt.avg_tariff_tnd_per_kwh > 0.20
    
    # Assert end-of-day stored volume >= start volume for optimized plan
    assert metrics_opt.tank_levels_preserved is True
    assert metrics_opt.total_storage_end_m3 >= metrics_opt.total_storage_start_m3 - 10.0
    t_start = res_opt.pressures.index[0]
    t_end = res_opt.pressures.index[-1]
    for t_name in ["1", "2", "3"]:
        assert res_opt.pressures.loc[t_end, t_name] >= res_opt.pressures.loc[t_start, t_name] - 0.25
    
    # Service pressure rule must be respected (> 90% compliance)
    assert metrics_opt.compliance_min_pressure_pct >= 90.0
    assert "ADVISORY" in metrics_opt.advisory_recommendation

def test_resilience_outage_simulation():
    res_blind, res_resil, comp = run_resilience_simulation(
        pump_outage_id="10",
        outage_start_hour=14,
        outage_duration_hours=4
    )
    assert comp.target_pump == "10"
    assert "14:00" in comp.outage_window_str
    assert comp.resilience_priority_zone_compliance_pct >= 90.0
    assert len(comp.advisory_action_items) >= 3
    assert "Pre-fill" in comp.advisory_action_items[0]
