"""Tests for Phase 3: Leak modeling, detection, localization, and severity."""

from pathlib import Path
import pytest
import config
from network.loader import load_network
from sim.leak_injector import inject_node_leak, inject_pipe_leak, classify_leak_severity
from sim.simulator import run_simulation
from ml.leak_detector import DistrictWaterBalanceDetector, detect_anomaly
from ml.leak_localizer import rank_suspect_pipes, evaluate_unseen_scenarios

def test_inject_node_leak():
    wn = load_network(24)
    target_node = wn.junction_name_list[10]
    inject_node_leak(wn, target_node, area_m2=config.LEAK_AREA_MODERATE_M2, start_hour=2, duration_hours=20)
    
    node = wn.get_node(target_node)
    assert node.leak_area == config.LEAK_AREA_MODERATE_M2
    
    res = run_simulation(wn)
    assert res.total_water_loss_m3 > 0
    assert res.leak_demand_m3h[target_node].max() > 0

def test_inject_pipe_leak_split():
    wn = load_network(24)
    target_pipe = wn.pipe_name_list[5]
    initial_links = wn.num_links
    initial_nodes = wn.num_nodes
    
    wn, leak_j = inject_pipe_leak(wn, target_pipe, area_m2=config.LEAK_AREA_CRITICAL_M2)
    assert wn.num_links == initial_links + 1
    assert wn.num_nodes == initial_nodes + 1
    assert leak_j in wn.node_name_list
    
    res = run_simulation(wn)
    assert res.total_water_loss_m3 > 0

def test_leak_severity_classification():
    sev_minor, label_minor = classify_leak_severity(5.0)
    sev_mod, label_mod = classify_leak_severity(20.0)
    sev_crit, label_crit = classify_leak_severity(55.0)
    
    assert sev_minor == "minor"
    assert sev_mod == "moderate"
    assert sev_crit == "critical"

def test_district_water_balance_detector():
    wb_detector = DistrictWaterBalanceDetector(gap_threshold_pct=12.0)
    wn = load_network(24)
    res = run_simulation(wn)
    
    flags = wb_detector.analyze_balances(res.district_balances)
    assert len(flags) == 5
    for f in flags:
        assert "gap_percentage" in f
        assert "disclaimer" in f

def test_rank_suspect_pipes_structure():
    wn = load_network(24)
    res_base = run_simulation(wn)
    
    # Run with leak
    wn_leak = load_network(24)
    inject_node_leak(wn_leak, wn.junction_name_list[15], area_m2=config.LEAK_AREA_CRITICAL_M2)
    res_leak = run_simulation(wn_leak)
    
    suspects = rank_suspect_pipes(res_leak.pressures, res_base.pressures, mode="rich", top_k=5)
    assert len(suspects) == 5
    probs = [s["probability"] for s in suspects]
    assert 0.99 <= sum(probs) <= 1.01
    assert suspects[0]["rank"] == 1
    assert "recommendation" in suspects[0]

def test_localization_ranking_invariants():
    """Verify that for every scenario, hit@1 <= hit@3 <= hit@5 strictly holds."""
    from sim.scenario_generator import load_scenario_dataset
    data = load_scenario_dataset()
    val_leaks = [s for s in data["scenarios"] if s["split"] == "val" and s["has_leak"]][:15]
    for sc in val_leaks:
        baseline_p = sc.get("baseline_pressures", data["baseline_pressures"])
        for mode in ["rich", "sparse"]:
            suspects = rank_suspect_pipes(sc["pressures"], baseline_p, mode=mode, top_k=5, seed=sc["sensor_noise_seed"])
            top5_ids = [s["pipe_id"] for s in suspects]
            true_pipes = sc["true_pipes"]
            prim_pipe = sc["leak_pipe"]
            
            # Exact pipe invariant
            e1 = int(prim_pipe in top5_ids[:1])
            e3 = int(prim_pipe in top5_ids[:3])
            e5 = int(prim_pipe in top5_ids[:5])
            assert e1 <= e3 <= e5, f"Exact invariant violated: {e1} <= {e3} <= {e5}"
            
            # Adjacent pipe invariant
            a1 = int(any(p in true_pipes for p in top5_ids[:1]))
            a3 = int(any(p in true_pipes for p in top5_ids[:3]))
            a5 = int(any(p in true_pipes for p in top5_ids[:5]))
            assert a1 <= a3 <= a5, f"Adjacent invariant violated: {a1} <= {a3} <= {a5}"

def test_evaluation_file_generation():
    metrics = evaluate_unseen_scenarios()
    assert "rich" in metrics
    assert "sparse" in metrics
    assert Path(config.DOCS_DIR / "EVALUATION.md").exists()
