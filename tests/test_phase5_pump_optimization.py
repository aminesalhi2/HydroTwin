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

def test_outage_proof_forced_shutoff_24h():
    """Verify that a 24h total pump blackout strictly shuts off pumps, exhausts tanks, and collapses compliance."""
    import wntr
    from network.loader import load_network, partition_districts
    from sim.simulator import run_simulation
    
    wn = load_network(24)
    p10 = wn.get_link("10")
    p335 = wn.get_link("335")
    
    # Remove all controls that could turn either pump back on
    controls_to_remove = [c for c in wn.control_name_list if "PUMP 10" in str(wn.get_control(c)) or "PUMP 335" in str(wn.get_control(c))]
    for c_name in controls_to_remove:
        wn.remove_control(c_name)
        
    p10.initial_status = wntr.network.elements.LinkStatus.Closed
    p335.initial_status = wntr.network.elements.LinkStatus.Closed
    
    res = run_simulation(wn)
    
    # 1. Assert pump flow = 0 for all 24 hours
    flow_10_max = res.flowrates["10"].abs().max()
    flow_335_max = res.flowrates["335"].abs().max()
    assert flow_10_max == 0.0, f"Expected 0 flow on Pump 10, got {flow_10_max}"
    assert flow_335_max == 0.0, f"Expected 0 flow on Pump 335, got {flow_335_max}"
    
    # 2. Track hourly tank levels and hours when tanks hit minimum level
    t1_min = wn.get_node("1").min_level
    t2_min = wn.get_node("2").min_level
    t3_min = wn.get_node("3").min_level
    
    t1_exhausted_hour = None
    t2_exhausted_hour = None
    t3_exhausted_hour = None
    
    _, d2n = partition_districts(wn)
    d3_nodes = d2n["District 3 - Medina & Hospital"]
    
    print("\n--- 24h Outage Proof: Hourly Tank Levels and Pressure Compliance ---")
    print("Hour | Tank 1 (min=0.03m) | Tank 2 (min=1.98m) | Tank 3 (min=1.22m) | Net >= 15m | D3 >= 18m")
    
    hourly_net_comp = []
    hourly_d3_comp = []
    
    for h in range(25):
        t1_val = res.pressures.loc[h * 3600, "1"]
        t2_val = res.pressures.loc[h * 3600, "2"]
        t3_val = res.pressures.loc[h * 3600, "3"]
        
        if t1_exhausted_hour is None and t1_val <= t1_min + 0.01:
            t1_exhausted_hour = h
        if t2_exhausted_hour is None and t2_val <= t2_min + 0.01:
            t2_exhausted_hour = h
        if t3_exhausted_hour is None and t3_val <= t3_min + 0.01:
            t3_exhausted_hour = h
            
        net_comp = (res.pressures.loc[h * 3600, wn.junction_name_list] >= 15.0).mean() * 100.0
        d3_comp = (res.pressures.loc[h * 3600, d3_nodes] >= 18.0).mean() * 100.0
        hourly_net_comp.append(net_comp)
        hourly_d3_comp.append(d3_comp)
        
        print(f"{h:02d}:00 | T1={t1_val:.2f}m | T2={t2_val:.2f}m | T3={t3_val:.2f}m | Net: {net_comp:.1f}% | D3: {d3_comp:.1f}%")
        
    print(f"Tank 1 reached minimum level at Hour: {t1_exhausted_hour}")
    print(f"Tank 2 reached minimum level at Hour: {t2_exhausted_hour}")
    print(f"Tank 3 reached minimum level at Hour: {t3_exhausted_hour}")
    
    # Tanks 1 and 2 hit minimum level at hour 4
    assert t1_exhausted_hour == 4, f"Expected T1 min at h=4, got {t1_exhausted_hour}"
    assert t2_exhausted_hour == 4, f"Expected T2 min at h=4, got {t2_exhausted_hour}"
    # Tank 3 (massive elevated tank) hits minimum level at hour 8
    assert t3_exhausted_hour == 8, f"Expected T3 min at h=8, got {t3_exhausted_hour}"
    
    # 3. Assert that once storage is exhausted at hour 8, compliance collapses
    assert hourly_net_comp[7] > 90.0, "Storage should buffer network through hour 7"
    assert hourly_net_comp[8] < 5.0, f"Expected network compliance collapse at hour 8, got {hourly_net_comp[8]}%"
    assert hourly_d3_comp[8] == 0.0, f"Expected District 3 compliance collapse at hour 8, got {hourly_d3_comp[8]}%"

