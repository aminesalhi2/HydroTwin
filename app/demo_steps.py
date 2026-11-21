"""Precomputed demo scenarios cache for the 3-minute jury presentation.

Guarantees instant response (<0.5s) on stage with zero risk of simulation hangs.
Covers the 6 guided demo steps in all 4 languages.
"""

from pathlib import Path
from typing import Dict, Any
import joblib

import config
from network.loader import load_network, partition_districts
from sim.simulator import run_simulation
from sim.leak_injector import inject_node_leak, classify_leak_severity
from ml.demand_forecasting import predict_district_demand
from ml.leak_detector import detect_anomaly
from ml.leak_localizer import rank_suspect_pipes
from planner.pump_optimizer import get_default_baseline_plan, get_cost_optimized_plan
from planner.resilience import run_resilience_simulation
from app.multilingual import generate_work_order, answer_structured_query

DEMO_CACHE_PATH = config.DATA_DIR / "demo_cache.joblib"

DEMO_STEP_METADATA = {
    1: {
        "title": "Step 1: Dense Digital Twin & District Demand Forecast",
        "description": "Visualize the baseline network with 24 dense sensors. Inspect 24-hour demand forecasts with 90% prediction intervals across all 5 municipal districts.",
        "badge": "🇯🇵 Bilateral Reference Twin"
    },
    2: {
        "title": "Step 2: Physical Leak Injection & Ranked Work Order",
        "description": "A simulated pipe burst occurs. Dual-track detection flags the anomaly. Topological graph smoothing identifies the Top-5 ranked suspect pipes, and an actionable multilingual work order is generated.",
        "badge": "🚨 Rapid Localization"
    },
    3: {
        "title": "Step 3: Diurnal Day ➔ Night Transition & Pressure Reduction",
        "description": "Shift pumping to off-peak night hours (22h-06h). Throttling midday excess pressure reduces background physical leakage under Torricelli's law while saving 0 to 583 kWh/day across seasonal profiles under hypothetical tariffs.",
        "badge": "⚡ Energy + Water Nexus"
    },
    4: {
        "title": "Step 4: Transition to Sparse Telemetry (Honest Degradation)",
        "description": "Switch instrumentation from 24 sensors to 6 sensors with 1 simulated failed sensor. Transparently report the honest accuracy drop and expanded field search radius.",
        "badge": "🇹🇳 Low-Cost Adaptation"
    },
    5: {
        "title": "Step 5: Grid Power Crisis & Emergency Resilience Mode",
        "description": "Primary intake Pump 10 experiences a 4-hour blackout (14h-18h). The AI assistant proposes pre-filled storage and gravity routing to protect the Hospital District above 18m head.",
        "badge": "🛡️ Priority Zone Protection"
    },
    6: {
        "title": "Step 6: Operational Advisory Sign-Off & JICA Pilot Roadmap",
        "description": "Executive review of live counters: m³ of water and kWh saved. Roadmap for a 1-district sandbox pilot with an operator and JICA in advisory mode.",
        "badge": "🤝 JICA Bilateral Roadmap"
    }
}

def precompute_demo_cache() -> Dict[str, Any]:
    """Simulate and cache all 6 demo steps so live presentations are 100% instant and offline."""
    print("[Demo Cache] Precomputing Step 1: Baseline & Forecasts...")
    wn_base = load_network(24)
    res_base = run_simulation(wn_base)
    node_to_d, d_to_nodes = partition_districts(wn_base)
    
    # Precompute district forecasts
    forecasts = {}
    for d in config.DISTRICT_NAMES:
        pred, low, upp = predict_district_demand(d, season="Summer", time_of_day="morning", hour=10)
        forecasts[d] = {"mean_m3h": round(pred, 1), "lower_m3h": round(low, 1), "upper_m3h": round(upp, 1)}

    print("[Demo Cache] Precomputing Step 2: Simulated Leak Scenario...")
    leak_node = wn_base.junction_name_list[25] # Node in Centre-Ville
    wn_leak = load_network(24)
    inject_node_leak(wn_leak, leak_node, area_m2=config.LEAK_AREA_CRITICAL_M2, start_hour=6, duration_hours=18)
    res_leak = run_simulation(wn_leak)
    anomaly_result = detect_anomaly(res_leak.pressures, res_base.pressures, res_leak.district_balances)
    suspects_rich = rank_suspect_pipes(res_leak.pressures, res_base.pressures, mode="rich", top_k=5)
    suspects_sparse = rank_suspect_pipes(res_leak.pressures, res_base.pressures, mode="sparse", top_k=5)
    
    # Precompute work orders for all 4 languages
    work_orders = {}
    for lang in ["en", "fr", "ar", "ja"]:
        work_orders[lang] = generate_work_order(
            has_leak=True,
            severity="critical",
            district=node_to_d.get(leak_node, "District 1 - Centre-Ville"),
            suspect_pipes=suspects_rich,
            water_loss_m3h=float(res_leak.leak_demand_m3h[leak_node].max()),
            lang=lang
        )

    print("[Demo Cache] Precomputing Step 3: TOU Pumping Optimization...")
    res_def, metrics_def = get_default_baseline_plan(24)
    res_opt, metrics_opt = get_cost_optimized_plan(24, baseline_results=res_def)

    print("[Demo Cache] Precomputing Step 5: Resilience Outage Simulation...")
    res_blind, res_resil, comp_resil = run_resilience_simulation(
        pump_outage_id="10",
        outage_start_hour=14,
        outage_duration_hours=4
    )

    demo_payload = {
        "step1": {
            "res_base": res_base,
            "forecasts": forecasts,
            "node_to_district": node_to_d,
            "district_to_nodes": d_to_nodes,
        },
        "step2": {
            "res_leak": res_leak,
            "leak_node": leak_node,
            "anomaly_result": anomaly_result,
            "suspects_rich": suspects_rich,
            "suspects_sparse": suspects_sparse,
            "work_orders": work_orders,
        },
        "step3": {
            "metrics_def": metrics_def,
            "metrics_opt": metrics_opt,
            "res_opt": res_opt,
        },
        "step4": {
            "suspects_rich": suspects_rich,
            "suspects_sparse": suspects_sparse,
        },
        "step5": {
            "comp_resil": comp_resil,
            "res_blind": res_blind,
            "res_resil": res_resil,
        },
        "step6": {
            "total_water_loss_detected": res_leak.total_water_loss_m3,
            "kwh_saved": metrics_opt.kwh_saved_vs_baseline,
            "cost_saved_tnd": metrics_opt.cost_saved_vs_baseline_tnd,
        }
    }
    
    joblib.dump(demo_payload, DEMO_CACHE_PATH)
    print(f"[Demo Cache] Successfully saved to {DEMO_CACHE_PATH}")
    return demo_payload

def get_demo_cache() -> Dict[str, Any]:
    """Retrieve or generate demo cache."""
    if not DEMO_CACHE_PATH.exists():
        precompute_demo_cache()
    return joblib.load(DEMO_CACHE_PATH)
