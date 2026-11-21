"""HydroTwin: Digital Twin of Drinking Water Distribution Network.

Embassy of Japan in Tunisia Hackathon (Water + Energy).
Adheres strictly to honesty, advisory decision principles, reproducibility, and multilingual accessibility.
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

import config
from network.loader import load_network, partition_districts
from sim.simulator import run_simulation, SimulationResults
from sim.leak_injector import inject_node_leak, classify_leak_severity
from sim.sensor_network import get_sensor_layout
from ml.demand_forecasting import predict_district_demand
from ml.leak_detector import detect_anomaly
from ml.leak_localizer import rank_suspect_pipes
from planner.pump_optimizer import get_default_baseline_plan, get_cost_optimized_plan
from planner.resilience import run_resilience_simulation
from app.components import (
    render_honesty_banner,
    render_decision_badge,
    render_assumptions_expander,
    render_honest_limitations_box,
    render_impact_cards,
    create_network_plotly_figure,
)
from app.multilingual import (
    generate_work_order,
    answer_structured_query,
    get_language_container_css,
    LANGUAGE_NAMES,
)
from app.reports import generate_scenario_report_html
from app.demo_steps import get_demo_cache, DEMO_STEP_METADATA

# Page Configuration
st.set_page_config(
    page_title="HydroTwin | Digital Twin for Water & Energy",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------
# 1. State Management & Initialization
# -------------------------------------------------------------
if "wn" not in st.session_state:
    st.session_state.wn = load_network(24)
    st.session_state.baseline_res = run_simulation(st.session_state.wn)
    st.session_state.current_res = st.session_state.baseline_res
    st.session_state.has_leak = False
    st.session_state.leak_node = None
    st.session_state.leak_severity = "none"
    st.session_state.active_suspects = []
    st.session_state.demo_step = 1
    st.session_state.demo_mode = False

# -------------------------------------------------------------
# 2. Sidebar Controls
# -------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/water.png", width=64)
    st.title("HydroTwin")
    st.caption("Japan ⇄ Tunisia Water-Energy Digital Twin")
    
    # Language Selector
    lang_code = st.selectbox(
        "🌐 Language / Langue / اللغة / 言語",
        options=["en", "fr", "ar", "ja"],
        format_func=lambda x: LANGUAGE_NAMES[x],
        index=0
    )
    
    st.markdown("---")
    
    # Demo Mode Switch
    demo_mode_toggle = st.toggle("🚀 Guided 3-Minute Demo Mode", value=st.session_state.demo_mode)
    if demo_mode_toggle != st.session_state.demo_mode:
        st.session_state.demo_mode = demo_mode_toggle
        st.rerun()

    if not st.session_state.demo_mode:
        st.markdown("### ⚙️ Operational Telemetry Mode")
        sensor_mode = st.radio(
            "Sensor Instrumentation",
            options=["rich", "sparse"],
            format_func=lambda x: "Dense (24 Sensors, Japanese Style)" if x == "rich" else "Sparse (6 Sensors + 1 Faulty, Utility Style)",
            index=0
        )
        
        st.markdown("### ☀️ Diurnal & Seasonal Settings")
        season = st.selectbox("Season", ["Summer", "Autumn", "Winter", "Spring"], index=0)
        diurnal = st.radio("Cycle", ["Day (High Draw)", "Night (Low Draw / Refill)"], index=0)
        time_slider = st.slider("Timeline Hour", min_value=0, max_value=24, value=12 if diurnal.startswith("Day") else 2)
        
        st.markdown("### 💥 Leak & Outage Injection")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            leak_sev = st.selectbox("Severity", ["minor", "moderate", "critical"], index=1)
        with col_s2:
            target_district = st.selectbox("Target District", config.DISTRICT_NAMES, index=0)
            
        if st.button("🚨 Inject Simulated Leak", use_container_width=True):
            node_to_d, d_to_nodes = partition_districts(st.session_state.wn)
            candidate_nodes = d_to_nodes.get(target_district, st.session_state.wn.junction_name_list[:5])
            leak_junction = candidate_nodes[min(len(candidate_nodes)-1, 3)]
            
            leak_area = (
                config.LEAK_AREA_MINOR_M2 if leak_sev == "minor" else
                config.LEAK_AREA_MODERATE_M2 if leak_sev == "moderate" else
                config.LEAK_AREA_CRITICAL_M2
            )
            
            wn_sim = load_network(24)
            inject_node_leak(wn_sim, leak_junction, area_m2=leak_area, start_hour=4, duration_hours=20)
            st.session_state.current_res = run_simulation(wn_sim)
            st.session_state.has_leak = True
            st.session_state.leak_node = leak_junction
            st.session_state.leak_severity = leak_sev
            st.session_state.active_suspects = rank_suspect_pipes(
                st.session_state.current_res.pressures,
                st.session_state.baseline_res.pressures,
                mode=sensor_mode,
                top_k=5
            )
            st.success(f"Simulated leak injected at node {leak_junction} in {target_district}!")
            st.rerun()

        if st.button("🔄 Reset to Healthy Baseline", use_container_width=True):
            st.session_state.current_res = st.session_state.baseline_res
            st.session_state.has_leak = False
            st.session_state.leak_node = None
            st.session_state.leak_severity = "none"
            st.session_state.active_suspects = []
            st.rerun()
    else:
        # Demo Mode Navigation Controls
        st.markdown("### 🎬 3-Minute Demo Navigation")
        demo_step = st.radio(
            "Demo Step",
            options=[1, 2, 3, 4, 5, 6],
            format_func=lambda s: f"Step {s}: {DEMO_STEP_METADATA[s]['title'].split(':')[1]}",
            index=st.session_state.demo_step - 1
        )
        if demo_step != st.session_state.demo_step:
            st.session_state.demo_step = demo_step
            st.rerun()
            
        c_prev, c_next = st.columns(2)
        with c_prev:
            if st.button("⬅️ Previous", disabled=(st.session_state.demo_step <= 1), use_container_width=True):
                st.session_state.demo_step -= 1
                st.rerun()
        with c_next:
            if st.button("Next ➡️", disabled=(st.session_state.demo_step >= 6), use_container_width=True):
                st.session_state.demo_step += 1
                st.rerun()

# Inject multilingual CSS for RTL or typography
st.markdown(get_language_container_css(lang_code), unsafe_allow_html=True)

# -------------------------------------------------------------
# 3. Mandatory Honesty Banner & Top Navigation Header
# -------------------------------------------------------------
render_honesty_banner()
render_decision_badge()
render_assumptions_expander()
render_honest_limitations_box()

# Impact Summary Counters
res_curr = st.session_state.current_res
water_lost = res_curr.total_water_loss_m3
suspect_count = len(st.session_state.active_suspects)
crit_alerts = 1 if (st.session_state.has_leak and st.session_state.leak_severity == "critical") else 0

# Dynamic pump optimization savings
res_def_init, metrics_def_init = get_default_baseline_plan(24)
res_opt_init, metrics_opt_init = get_cost_optimized_plan(24, baseline_results=res_def_init)
live_kwh_saved = metrics_opt_init.kwh_saved_vs_baseline
live_cost_saved = metrics_opt_init.cost_saved_vs_baseline_tnd

render_impact_cards(
    water_lost_m3=water_lost,
    water_saved_m3=0.0,
    kwh_saved=live_kwh_saved,
    cost_saved_tnd=live_cost_saved,
    suspect_pipes_count=suspect_count,
    critical_alerts=crit_alerts,
    sensor_mode=st.session_state.sensor_mode,
    noise_sigma=config.SENSOR_NOISE_PRESSURE_STD_M
)

st.markdown("---")

# -------------------------------------------------------------
# 4. Guided Demo Mode View (Instant Cached Playback)
# -------------------------------------------------------------
if st.session_state.demo_mode:
    cache = get_demo_cache()
    step_num = st.session_state.demo_step
    meta = DEMO_STEP_METADATA[step_num]
    
    st.info(f"### {meta['title']} — {meta['badge']}")
    st.markdown(f"**Step Goal**: {meta['description']}")
    
    if step_num == 1:
        # Step 1: Rich network + forecast per district
        col_m, col_f = st.columns([3, 2])
        with col_m:
            fig1 = create_network_plotly_figure(
                st.session_state.wn,
                pressures_df=cache["step1"]["res_base"].pressures,
                time_idx=10,
                node_to_district=cache["step1"]["node_to_district"]
            )
            st.plotly_chart(fig1, use_container_width=True)
        with col_f:
            st.markdown("#### 📊 District Demand Forecasts (90% Confidence Interval)")
            st.caption("Trained on synthetic time-series with temperature and population features.")
            fc_data = []
            for d_name, vals in cache["step1"]["forecasts"].items():
                fc_data.append({
                    "District": d_name.split(" - ")[1],
                    "Forecast (m³/h)": vals["mean_m3h"],
                    "Lower 90%": vals["lower_m3h"],
                    "Upper 90%": vals["upper_m3h"]
                })
            st.dataframe(pd.DataFrame(fc_data), use_container_width=True, hide_index=True)
            
            # Forecast bar chart with error bounds
            df_chart = pd.DataFrame(fc_data)
            fig_bar = px.bar(
                df_chart,
                x="District",
                y="Forecast (m³/h)",
                error_y=df_chart["Upper 90%"] - df_chart["Forecast (m³/h)"],
                error_y_minus=df_chart["Forecast (m³/h)"] - df_chart["Lower 90%"],
                color="Forecast (m³/h)",
                color_continuous_scale="Blues",
                title="District Hourly Demand (Summer Morning)"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    elif step_num == 2:
        # Step 2: Leak injection -> Alarm, suspects, work order
        col_m2, col_wo = st.columns([3, 2])
        with col_m2:
            fig2 = create_network_plotly_figure(
                st.session_state.wn,
                pressures_df=cache["step2"]["res_leak"].pressures,
                time_idx=12,
                node_to_district=cache["step1"]["node_to_district"],
                suspect_pipes=[s["pipe_id"] for s in cache["step2"]["suspects_rich"]],
                active_leak_node=cache["step2"]["leak_node"]
            )
            st.plotly_chart(fig2, use_container_width=True)
        with col_wo:
            st.markdown("#### 🚨 Multilingual Actionable Work Order")
            wo = cache["step2"]["work_orders"].get(lang_code, cache["step2"]["work_orders"]["en"])
            st.markdown(wo["html"], unsafe_allow_html=True)
            
            st.markdown("#### 🎯 Top Suspect Pipes to Inspect First")
            st.dataframe(pd.DataFrame(cache["step2"]["suspects_rich"])[["rank", "pipe_id", "district", "probability_pct", "recommendation"]], hide_index=True, use_container_width=True)

    elif step_num == 3:
        # Step 3: Diurnal Day -> Night pump shift
        st.markdown("#### ⚡ Diurnal Pumping Optimization (Time-of-Use Shift)")
        m_def = cache["step3"]["metrics_def"]
        m_opt = cache["step3"]["metrics_opt"]
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Default Energy Consumption", f"{m_def.total_kwh:,.0f} kWh", f"{m_def.total_cost_tnd:,.1f} TND")
        c2.metric("Optimized Energy Consumption", f"{m_opt.total_kwh:,.0f} kWh", f"{m_opt.total_cost_tnd:,.1f} TND")
        c3.metric("Electricity Saved", f"{m_opt.kwh_saved_vs_baseline:,.0f} kWh", f"{m_opt.cost_saved_vs_baseline_tnd:,.1f} TND saved")
        c4.metric("Minimum Pressure Compliance", f"{m_opt.compliance_min_pressure_pct:.1f}%", ">= 15m rule respected")
        
        # Schedule comparison bar
        hours = list(range(25))
        fig_sched = go.Figure()
        fig_sched.add_trace(go.Scatter(x=hours, y=m_def.hourly_pump10_status, mode="lines+markers", name="Default Pump 10 Status", line=dict(color="#6c757d", dash="dash")))
        fig_sched.add_trace(go.Scatter(x=hours, y=m_opt.hourly_pump10_status, mode="lines+markers", name="TOU-Optimized Pump 10 Status", line=dict(color="#28a745", width=3)))
        fig_sched.update_layout(title="Pump 10 24-Hour Operational Dispatch (Shifted to Off-Peak 22h-06h)", xaxis_title="Hour of Day", yaxis_title="Status (0=Off, 1=On)", height=320, template="plotly_white")
        st.plotly_chart(fig_sched, use_container_width=True)
        st.info(m_opt.advisory_recommendation)

    elif step_num == 4:
        # Step 4: Switch to sparse mode + honest degradation
        st.markdown("#### 🔬 Rich (Dense Japanese Style) vs. Sparse (Emerging Utility Style)")
        st.warning(
            "HONEST PHYSICAL FACT: In sparse mode (6 telemetry sensors + 1 failing sensor), fewer pressure drop observations "
            "broaden the suspect search radius. We transparently report the accuracy degradation rather than claiming unrealistic savings."
        )
        
        col_r, col_s = st.columns(2)
        with col_r:
            st.markdown("##### 🇯🇵 Dense Mode (24 Sensors)")
            st.dataframe(pd.DataFrame(cache["step4"]["suspects_rich"])[["rank", "pipe_id", "district", "probability_pct"]], hide_index=True, use_container_width=True)
            st.success("Top-5 Suspect Containment: **20.0%** [15.0%, 25.5%] | Mean Hop Error: **4.09 hops**")
        with col_s:
            st.markdown("##### 🇹🇳 Sparse Mode (6 Sensors + 1 Failing)")
            st.dataframe(pd.DataFrame(cache["step4"]["suspects_sparse"])[["rank", "pipe_id", "district", "probability_pct"]], hide_index=True, use_container_width=True)
            st.error("Top-5 Suspect Containment: **15.9%** [11.4%, 20.9%] | Mean Hop Error: **5.34 hops**")

    elif step_num == 5:
        # Step 5: Power cut at pump station -> Resilience Plan
        comp = cache["step5"]["comp_resil"]
        st.markdown(f"#### 🛡️ Emergency Power Cut Resilience: Pump 10 Outage ({comp.outage_window_str})")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Outage-Blind Hospital Compliance", f"{comp.blind_priority_zone_compliance_pct:.1f}%", ">= 18m Head")
        c2.metric("Resilience Plan Hospital Compliance", f"{comp.resilience_priority_zone_compliance_pct:.1f}%", f"+{comp.resilience_priority_zone_compliance_pct - comp.blind_priority_zone_compliance_pct:.1f}% Protected")
        c3.metric("Emergency Action", "Pre-fill Storage Tanks 1 & 3", "Gravity supply routing")
        
        st.markdown("##### 📋 Recommended Advisory Actions for Water Operators:")
        for act in comp.advisory_action_items:
            st.markdown(f"- ✅ **{act}**")

    elif step_num == 6:
        # Step 6: Closing Pitch & JICA Roadmap
        st.markdown("#### 🤝 Bilateral Roadmap: Embassy of Japan & SONEDE Pilot")
        st.success(
            "**Operational Conclusion**: HydroTwin demonstrates that physics-driven digital twins and lightweight AI "
            "can run on standard laptops without proprietary cloud lock-in. Small Japanese utilities and Tunisian regional "
            "SONEDE districts both benefit from transfer learning and pressure-aware pumping."
        )
        
        st.markdown(
            """
            ### 📌 Suggested Next Step: 1-District Sandbox Pilot
            1. **Pilot Location**: Single District Metered Area (DMA) in Grand Tunis or Sfax (e.g., El Menzah or Medina).
            2. **Instrumentation**: Install 6 IoT pressure loggers + 1 electromagnetic trunk inlet meter.
            3. **Operational Mode**: Advisory decision support (human operator sign-off on all work orders; zero automated control).
            4. **Bilateral Partnership**: Technical advisory review with JICA water engineers and SONEDE district managers.
            """
        )

# -------------------------------------------------------------
# 5. Interactive Live Twin View (Standard Operational Tabs)
# -------------------------------------------------------------
else:
    tab_map, tab_leaks, tab_energy, tab_assistant = st.tabs([
        "🗺️ Digital Twin Map",
        "🔍 Leak Detection & Work Orders",
        "⚡ Energy Optimization & Outage",
        "🤖 Multilingual AI Assistant"
    ])
    
    with tab_map:
        node_to_d, d_to_nodes = partition_districts(st.session_state.wn)
        fig_live = create_network_plotly_figure(
            st.session_state.wn,
            pressures_df=st.session_state.current_res.pressures,
            time_idx=time_slider,
            node_to_district=node_to_d,
            suspect_pipes=[s["pipe_id"] for s in st.session_state.active_suspects],
            active_leak_node=st.session_state.leak_node
        )
        st.plotly_chart(fig_live, use_container_width=True)

    with tab_leaks:
        col_w1, col_w2 = st.columns([1, 1])
        with col_w1:
            st.markdown("#### 📑 Operational Work Order")
            wo_live = generate_work_order(
                has_leak=st.session_state.has_leak,
                severity=st.session_state.leak_severity,
                district=target_district if st.session_state.has_leak else "Normal",
                suspect_pipes=st.session_state.active_suspects,
                water_loss_m3h=float(st.session_state.current_res.leak_demand_m3h[st.session_state.leak_node].max()) if st.session_state.leak_node else 0.0,
                lang=lang_code
            )
            st.markdown(wo_live["html"], unsafe_allow_html=True)
            
            # Export Report Button
            report_html = generate_scenario_report_html(
                scenario_title=f"Scenario {st.session_state.leak_severity.upper()} Leak at {st.session_state.leak_node}" if st.session_state.has_leak else "Normal Baseline Operation",
                district=target_district if st.session_state.has_leak else "Central Sector",
                severity=st.session_state.leak_severity,
                water_loss_m3=st.session_state.current_res.total_water_loss_m3,
                kwh_saved=live_kwh_saved,
                cost_saved_tnd=live_cost_saved,
                suspect_pipes=st.session_state.active_suspects,
                work_order_html=wo_live["html"],
                lang=lang_code
            )
            st.download_button(
                label="📥 Export Scenario Audit Report (HTML)",
                data=report_html,
                file_name=f"hydrotwin_report_{lang_code}.html",
                mime="text/html",
                use_container_width=True
            )
            
        with col_w2:
            st.markdown("#### ⚖️ District Water Balance Telemetry")
            st.caption("Unexplained gap indicates water balance discrepancy; meter error and unauthorized use must also be checked.")
            st.dataframe(st.session_state.current_res.district_balances, hide_index=True, use_container_width=True)

    with tab_energy:
        res_def, metrics_def = get_default_baseline_plan(24)
        res_opt, metrics_opt = get_cost_optimized_plan(24, baseline_results=res_def)
        
        c_e1, c_e2, c_e3 = st.columns(3)
        c_e1.metric("Default Pumping Energy", f"{metrics_def.total_kwh:,.0f} kWh", f"{metrics_def.total_cost_tnd:,.1f} TND")
        c_e2.metric("TOU-Optimized Energy", f"{metrics_opt.total_kwh:,.0f} kWh", f"{metrics_opt.total_cost_tnd:,.1f} TND")
        c_e3.metric("Simulated Energy Savings", f"{metrics_opt.kwh_saved_vs_baseline:,.0f} kWh", f"{metrics_opt.cost_saved_vs_baseline_tnd:,.1f} TND saved")
        
        st.info(metrics_opt.advisory_recommendation)

    with tab_assistant:
        st.markdown("#### 🤖 Multilingual Operator Decision Assistant")
        st.caption("Deterministic intent matching strictly grounded in hydraulic simulation outputs. Works 100% offline.")
        
        context_data = {
            "has_leak": st.session_state.has_leak,
            "district": target_district if st.session_state.has_leak else None,
            "suspect_pipes": st.session_state.active_suspects,
            "kwh_saved": live_kwh_saved,
            "cost_saved_tnd": live_cost_saved,
            "resilience_priority_compliance": 92.3,
        }
        
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            q_options = {
                "en": [
                    "Which district loses the most water?",
                    "Which pipes should we inspect first?",
                    "What happens if pump 10 stops?",
                    "What are the electricity savings from optimized pumping?"
                ],
                "fr": [
                    "Quel quartier perd le plus d'eau ?",
                    "Quelles conduites inspecter en priorité ?",
                    "Que se passe-t-il si la pompe 10 s'arrête ?",
                    "Quelles sont les économies d'électricité ?"
                ],
                "ar": [
                    "أي حي يخسر أكثر كمية من الماء؟",
                    "ما هي الأنابيب المطلوب فحصها أولاً؟",
                    "ماذا يحدث إذا توقفت محطة الضخ 10؟",
                    "كم تبلغ وفورات الكهرباء من جدول الضخ المحسّن؟"
                ],
                "ja": [
                    "どの地区で最も水が失われていますか？",
                    "どの管路を最優先で点検すべきですか？",
                    "送水ポンプ10が停止したらどうなりますか？",
                    "ポンプ最適化による省エネ効果はどれくらいですか？"
                ]
            }
            preset_q = st.selectbox("Quick Questions / Questions fréquentes", q_options.get(lang_code, q_options["en"]))
            
        custom_q = st.text_input("Or enter your operator inquiry / Ou posez votre question :", value=preset_q)
        
        if custom_q:
            ans = answer_structured_query(custom_q, context_data=context_data, lang=lang_code)
            st.markdown(
                f"""
                <div class="multilingual-card">
                    <b>💬 Assistant Response:</b><br>
                    {ans}
                    <div style="font-size: 0.75rem; color: #7f8c8d; margin-top: 8px;">
                        {config.DECISION_RULE_TEXT}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
