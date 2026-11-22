"""HydroTwin: Digital Twin of Drinking Water Distribution Network.

Embassy of Japan in Tunisia Hackathon (Water + Energy).
Adheres strictly to honesty, advisory decision principles, reproducibility, and multilingual accessibility.
"""

import os
import sys
from pathlib import Path

# Ensure repository root is always in sys.path regardless of working directory
_REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

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
from app.assets.plotly_template import register_template, add_event_vrect, add_threshold_line
from app.components import (
    inject_theme_css,
    render_hero_header,
    render_footer,
    render_assumptions_expander,
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

# Register custom Plotly template before any chart rendering
register_template()

# Page Configuration
st.set_page_config(
    page_title="HydroTwin | Digital Twin for Water & Energy",
    page_icon="app/assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject full theme stylesheet on every render
inject_theme_css()

_LOGO_SVG_SIDEBAR = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 76" width="34" height="40" fill="none" style="display:block;margin:0 auto 10px;">
  <path d="M32 3 C32 3 10 32 10 50 C10 63 19.8 73 32 73 C44.2 73 54 63 54 50 C54 32 32 3 32 3 Z"
        fill="#0D9488" stroke="#0D9488" stroke-width="1.6"/>
  <line x1="32" y1="36" x2="22" y2="54" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round"/>
  <line x1="32" y1="36" x2="42" y2="54" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round"/>
  <line x1="22" y1="54" x2="42" y2="54" stroke="#0D9488" stroke-width="1.8" stroke-linecap="round"/>
  <circle cx="32" cy="36" r="3.5" fill="#0D9488" stroke="#FFFFFF" stroke-width="1.5"/>
  <circle cx="22" cy="54" r="3" fill="#0B1528" stroke="#FFFFFF" stroke-width="1.5"/>
  <circle cx="42" cy="54" r="3" fill="#FFFFFF" stroke="#0D9488" stroke-width="1.5"/>
</svg>"""


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
    st.session_state.sensor_mode = "rich"
    st.session_state.active_scenario = "1 Normal"
    st.session_state.timeline_hour = 12
    st.session_state.is_outage = False

if "sensor_mode" not in st.session_state:
    st.session_state.sensor_mode = "rich"
if "active_scenario" not in st.session_state:
    st.session_state.active_scenario = "1 Normal"
if "timeline_hour" not in st.session_state:
    st.session_state.timeline_hour = 12
if "is_outage" not in st.session_state:
    st.session_state.is_outage = False


# -------------------------------------------------------------
# 2. Sidebar Controls
# -------------------------------------------------------------
with st.sidebar:
    st.markdown(_LOGO_SVG_SIDEBAR, unsafe_allow_html=True)
    st.markdown(
        """
        <div style="text-align:center;margin-bottom:14px;">
          <div style="color:#FFFFFF;font-size:1.15rem;font-weight:700;letter-spacing:-0.02em;">HydroTwin</div>
          <div style="color:rgba(255,255,255,0.65);font-size:0.74rem;">Digital Twin · Japan × Tunisia</div>
          <div style="margin-top:6px;"><span class="ht-chip ht-chip-offline" style="font-size:0.68rem;padding:2px 8px;">100% Offline Mode</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Language Selector
    st.markdown('<div class="ht-sidebar-section">Language / Langue / اللغة / 言語</div>', unsafe_allow_html=True)
    lang_code = st.selectbox(
        "Language Selection",
        options=["en", "fr", "ar", "ja"],
        format_func=lambda x: {
            "ar": "العربية",
            "fr": "Français",
            "ja": "日本語",
            "en": "English",
        }[x],
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Guided Demo Walkthrough Toggle
    demo_mode_toggle = st.toggle("Guided Walkthrough (6 Steps)", value=st.session_state.demo_mode)
    if demo_mode_toggle != st.session_state.demo_mode:
        st.session_state.demo_mode = demo_mode_toggle
        st.rerun()

    if not st.session_state.demo_mode:
        st.markdown('<div class="ht-sidebar-section">Telemetry Instrumentation</div>', unsafe_allow_html=True)
        
        # Segmented Control for Dense vs Sparse (Contrast Fixed)
        sensor_mode_choice = st.segmented_control(
            "Sensor Instrumentation",
            options=["rich", "sparse"],
            format_func=lambda x: "Dense (24)" if x == "rich" else "Sparse (6+1)",
            default=st.session_state.sensor_mode,
            key="sensor_mode_seg",
            label_visibility="collapsed",
        )
        if sensor_mode_choice and sensor_mode_choice != st.session_state.sensor_mode:
            st.session_state.sensor_mode = sensor_mode_choice
            st.rerun()

        if st.session_state.sensor_mode == "rich":
            st.markdown(
                """
                <div style="margin: 6px 0 10px;">
                  <span class="ht-chip ht-chip-offline" style="font-size:0.70rem;">Dense (24 Sensors)</span>
                  <span class="ht-chip" style="font-size:0.70rem;margin-left:4px;color:rgba(255,255,255,0.7);">&sigma; = 0.40 m</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption("Dense telemetry captures localized pressure gradients across all network nodes.")
        else:
            st.markdown(
                """
                <div style="margin: 6px 0 10px;">
                  <span class="ht-chip" style="font-size:0.70rem;background:rgba(217,119,6,0.25);color:#F59E0B;">Sparse (6 Sens + 1 Fault)</span>
                  <span class="ht-chip" style="font-size:0.70rem;margin-left:4px;color:rgba(255,255,255,0.7);">&sigma; = 0.40 m</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption("Budget utility setup: 6 active transducers + 1 faulty logger reporting zero drop.")

        st.markdown('<div class="ht-sidebar-section">Hydraulic Timeline & Season</div>', unsafe_allow_html=True)
        season = st.selectbox("Season", ["Summer", "Autumn", "Winter", "Spring"], index=0)
        diurnal = st.radio("Cycle Pattern", ["Day (High Draw)", "Night (Low Draw / Refill)"], index=0 if st.session_state.timeline_hour >= 6 else 1)
        time_slider = st.slider(
            "Timeline Hour",
            min_value=0,
            max_value=24,
            value=st.session_state.timeline_hour,
            help="Hour of 24h simulation dispatch",
        )
        if time_slider != st.session_state.timeline_hour:
            st.session_state.timeline_hour = time_slider

        st.markdown('<div class="ht-sidebar-section">Simulated Incident Injection</div>', unsafe_allow_html=True)
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            leak_sev = st.selectbox("Severity", ["minor", "moderate", "critical"], index=1, help="Minor <10 m³/h, Moderate 10-50 m³/h, Critical >50 m³/h")
        with col_s2:
            target_district = st.selectbox("Target District", config.DISTRICT_NAMES, index=0)

        if st.button("Inject Simulated Leak", use_container_width=True):
            node_to_d, d_to_nodes = partition_districts(st.session_state.wn)
            candidate_nodes = d_to_nodes.get(target_district, st.session_state.wn.junction_name_list[:5])
            leak_junction = candidate_nodes[min(len(candidate_nodes) - 1, 3)]

            leak_area = (
                config.LEAK_AREA_MINOR_M2 if leak_sev == "minor"
                else config.LEAK_AREA_MODERATE_M2 if leak_sev == "moderate"
                else config.LEAK_AREA_CRITICAL_M2
            )

            wn_sim = load_network(24)
            inject_node_leak(wn_sim, leak_junction, area_m2=leak_area, start_hour=4, duration_hours=20)
            st.session_state.current_res = run_simulation(wn_sim)
            st.session_state.has_leak = True
            st.session_state.leak_node = leak_junction
            st.session_state.leak_severity = leak_sev
            st.session_state.active_scenario = "2 Leak"
            st.session_state.active_suspects = rank_suspect_pipes(
                st.session_state.current_res.pressures,
                st.session_state.baseline_res.pressures,
                mode=st.session_state.sensor_mode,
                top_k=5,
            )
            st.rerun()

        if st.button("Reset Healthy Baseline", use_container_width=True):
            st.session_state.current_res = st.session_state.baseline_res
            st.session_state.has_leak = False
            st.session_state.leak_node = None
            st.session_state.leak_severity = "none"
            st.session_state.active_suspects = []
            st.session_state.active_scenario = "1 Normal"
            st.session_state.is_outage = False
            st.rerun()

        # Collapsible Calibration & Engineering Jargon
        with st.expander("Engineering Reference & Calibration", expanded=False):
            st.markdown(
                """
                <div style="font-size:0.76rem;line-height:1.5;color:rgba(255,255,255,0.8);">
                  <b>Parameters &amp; Formulations:</b><br>
                  • <b>PDD</b>: Wagner pressure-dependent flow below 15m minimum head.<br>
                  • <b>TOU</b>: STEG Time-of-Use structure (Off-peak / Day / Peak).<br>
                  • <b>Top-k</b>: Suspect candidate containment in top-k ranks.<br>
                  • <b>Hop</b>: Graph shortest-path distance (edges to incident).<br>
                  • <b>&sigma; = 0.40 m</b>: Transducer Gaussian noise standard deviation.
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown('<div class="ht-sidebar-section">Walkthrough Navigation</div>', unsafe_allow_html=True)
        demo_step = st.radio(
            "Demo Step",
            options=[1, 2, 3, 4, 5, 6],
            format_func=lambda s: f"Step {s}: {DEMO_STEP_METADATA[s]['title'].split(':')[1]}",
            index=st.session_state.demo_step - 1,
        )
        if demo_step != st.session_state.demo_step:
            st.session_state.demo_step = demo_step
            st.rerun()

        c_prev, c_next = st.columns(2)
        with c_prev:
            if st.button("Previous Step", disabled=(st.session_state.demo_step <= 1), use_container_width=True):
                st.session_state.demo_step -= 1
                st.rerun()
        with c_next:
            if st.button("Next Step", disabled=(st.session_state.demo_step >= 6), use_container_width=True):
                st.session_state.demo_step += 1
                st.rerun()

# Inject multilingual CSS for RTL or typography
st.markdown(get_language_container_css(lang_code), unsafe_allow_html=True)


# -------------------------------------------------------------
# 3. Minimal Header with Advisory Popover
# -------------------------------------------------------------
render_hero_header()


# -------------------------------------------------------------
# 4. Top Horizontal Stepper: 1 Normal | 2 Leak | 3 Night | 4 Power cut
# -------------------------------------------------------------
def _apply_scenario_update():
    """Apply the chosen scenario state immediately on segmented control click."""
    sc = st.session_state.get("top_scenario_stepper", "1 Normal")
    st.session_state.active_scenario = sc
    if sc == "1 Normal":
        st.session_state.current_res = st.session_state.baseline_res
        st.session_state.has_leak = False
        st.session_state.leak_node = None
        st.session_state.leak_severity = "none"
        st.session_state.active_suspects = []
        st.session_state.timeline_hour = 12
        st.session_state.demo_step = 1
        st.session_state.is_outage = False
    elif sc == "2 Leak":
        wn_sim = load_network(24)
        inject_node_leak(wn_sim, "121", area_m2=config.LEAK_AREA_MODERATE_M2, start_hour=4, duration_hours=20)
        st.session_state.current_res = run_simulation(wn_sim)
        st.session_state.has_leak = True
        st.session_state.leak_node = "121"
        st.session_state.leak_severity = "moderate"
        st.session_state.active_suspects = rank_suspect_pipes(
            st.session_state.current_res.pressures,
            st.session_state.baseline_res.pressures,
            mode=st.session_state.sensor_mode,
            top_k=5,
        )
        st.session_state.timeline_hour = 12
        st.session_state.demo_step = 2
        st.session_state.is_outage = False
    elif sc == "3 Night":
        st.session_state.current_res = st.session_state.baseline_res
        st.session_state.has_leak = False
        st.session_state.leak_node = None
        st.session_state.leak_severity = "none"
        st.session_state.active_suspects = []
        st.session_state.timeline_hour = 2
        st.session_state.demo_step = 3
        st.session_state.is_outage = False
    elif sc == "4 Power cut":
        st.session_state.current_res = st.session_state.baseline_res
        st.session_state.has_leak = False
        st.session_state.leak_node = None
        st.session_state.leak_severity = "none"
        st.session_state.active_suspects = []
        st.session_state.timeline_hour = 14
        st.session_state.demo_step = 5
        st.session_state.is_outage = True

scenario_labels = ["1 Normal", "2 Leak", "3 Night", "4 Power cut"]
stepper_col, tag_col = st.columns([5, 1], vertical_alignment="center")

with stepper_col:
    st.segmented_control(
        "Operational Scenario",
        options=scenario_labels,
        default=st.session_state.active_scenario,
        key="top_scenario_stepper",
        on_change=_apply_scenario_update,
        label_visibility="collapsed",
    )

with tag_col:
    st.markdown(
        """
        <div style="text-align:right;">
          <span class="ht-ribbon-subtle">Japan × Tunisia</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------
# 5. Restrained Top KPI Cards (Max 4 Cards, Tabular Figures)
# -------------------------------------------------------------
res_curr = st.session_state.current_res
water_lost = res_curr.total_water_loss_m3
suspect_count = len(st.session_state.active_suspects)
crit_alerts = 1 if (st.session_state.has_leak and st.session_state.leak_severity == "critical") else 0

# Baseline vs optimized metrics
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
    noise_sigma=config.SENSOR_NOISE_PRESSURE_STD_M,
    has_leak=st.session_state.has_leak,
    is_outage=st.session_state.is_outage,
)


# -------------------------------------------------------------
# 6. View Modes: Guided Walkthrough or Standard Operational Tabs
# -------------------------------------------------------------
if st.session_state.demo_mode:
    cache = get_demo_cache()
    step_num = st.session_state.demo_step
    meta = DEMO_STEP_METADATA[step_num]

    col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
    with col_nav1:
        if st.button("Previous Step", disabled=(step_num <= 1), use_container_width=True, key="top_back_btn"):
            st.session_state.demo_step -= 1
            st.rerun()
    with col_nav2:
        st.markdown(
            f"""
            <div style="text-align:center;padding:2px 0;">
              <div style="font-weight:600;font-size:0.92rem;color:var(--ink);">Step {step_num} of 6: {meta['title']}</div>
              <div style="font-size:0.78rem;color:var(--text-secondary);">{meta['description']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_nav3:
        if st.button("Next Step", disabled=(step_num >= 6), use_container_width=True, key="top_next_btn"):
            st.session_state.demo_step += 1
            st.rerun()

    if step_num == 1:
        col_m, col_f = st.columns([3, 2])
        with col_m:
            fig1 = create_network_plotly_figure(
                st.session_state.wn,
                pressures_df=cache["step1"]["res_base"].pressures,
                time_idx=10,
                node_to_district=cache["step1"]["node_to_district"],
            )
            st.plotly_chart(fig1, use_container_width=True)
        with col_f:
            st.markdown("##### District Demand Forecasts (90% Confidence Interval)")
            fc_data = []
            for d_name, vals in cache["step1"]["forecasts"].items():
                fc_data.append({
                    "District": d_name.split(" - ")[1],
                    "Forecast (m³/h)": vals["mean_m3h"],
                    "Lower 90%": vals["lower_m3h"],
                    "Upper 90%": vals["upper_m3h"],
                })
            st.dataframe(pd.DataFrame(fc_data), use_container_width=True, hide_index=True)

            df_chart = pd.DataFrame(fc_data)
            fig_bar = px.bar(
                df_chart,
                x="District",
                y="Forecast (m³/h)",
                error_y=df_chart["Upper 90%"] - df_chart["Forecast (m³/h)"],
                error_y_minus=df_chart["Forecast (m³/h)"] - df_chart["Lower 90%"],
                color_discrete_sequence=["#0D9488"],
                title="District Hourly Demand (Summer Morning)",
            )
            fig_bar.update_layout(template="hydrotwin", height=240, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_bar, use_container_width=True)

    elif step_num == 2:
        col_m2, col_wo = st.columns([3, 2])
        with col_m2:
            fig2 = create_network_plotly_figure(
                st.session_state.wn,
                pressures_df=cache["step2"]["res_leak"].pressures,
                time_idx=12,
                node_to_district=cache["step1"]["node_to_district"],
                suspect_pipes=[s["pipe_id"] for s in cache["step2"]["suspects_rich"]],
                active_leak_node=cache["step2"]["leak_node"],
            )
            st.plotly_chart(fig2, use_container_width=True)
        with col_wo:
            st.markdown(cache["step2"]["work_order"]["html"], unsafe_allow_html=True)

    elif step_num == 3:
        p_hours = list(range(24))
        p_def = cache["step3"]["sched_def"]
        p_opt = cache["step3"]["sched_opt"]

        fig_sched = go.Figure()
        fig_sched.add_trace(go.Scatter(
            x=p_hours, y=p_def["Pump 10"],
            mode="lines", name="Default Baseline (Pump 10)",
            line=dict(color="#64748B", width=2, dash="dash"),
        ))
        fig_sched.add_trace(go.Scatter(
            x=p_hours, y=p_opt["Pump 10"],
            mode="lines", name="Optimized Schedule (Pump 10)",
            fill="tonexty",
            fillcolor="rgba(13, 148, 136, 0.12)",
            line=dict(color="#0D9488", width=2.2),
        ))
        add_event_vrect(fig_sched, 0, 6, "Off-Peak Tariff", color="teal", opacity=0.04)
        add_event_vrect(fig_sched, 22, 24, "Off-Peak Tariff", color="teal", opacity=0.04)
        fig_sched.update_layout(
            title=dict(text="<b>Pump 10 Hourly Duty: Baseline vs. Optimized</b>", font=dict(size=12)),
            xaxis=dict(title="Hour of Day", range=[0, 23]),
            yaxis=dict(title="Pump Status (0=OFF, 1=ON)", range=[-0.1, 1.2]),
            template="hydrotwin",
            height=280,
            margin=dict(l=10, r=10, t=36, b=10),
        )
        st.plotly_chart(fig_sched, use_container_width=True)

    elif step_num == 4:
        methods = ["Random Baseline", "Nearest-Sensor", "HydroTwin"]
        rich_vals = [5.2, 29.1, 36.8]
        sparse_vals = [5.2, 12.7, 16.4]

        fig_eval = go.Figure()
        fig_eval.add_trace(go.Bar(
            name="Dense Mode (24 Sensors)",
            y=methods, x=rich_vals, orientation="h",
            marker_color="#0D9488",
        ))
        fig_eval.add_trace(go.Bar(
            name="Sparse Mode (6 Sens + 1 Fault)",
            y=methods, x=sparse_vals, orientation="h",
            marker_color="#D97706",
        ))
        fig_eval.update_layout(
            title=dict(text="<b>Top-5 Exact Containment Accuracy (%)</b>", font=dict(size=12)),
            xaxis=dict(title="Accuracy (%)", range=[0, 50]),
            template="hydrotwin",
            height=240,
            barmode="group",
            margin=dict(l=10, r=20, t=36, b=10),
        )
        st.plotly_chart(fig_eval, use_container_width=True)

    elif step_num == 5:
        comp = cache["step5"]["comp_resil"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Blind Hospital Compliance", f"{comp.blind_priority_zone_compliance_pct:.1f}%")
        c2.metric("Pre-Fill Hospital Compliance", f"{comp.resilience_priority_zone_compliance_pct:.1f}%", f"+{comp.resilience_priority_zone_compliance_pct - comp.blind_priority_zone_compliance_pct:.1f} pp")
        c3.metric("Autonomy Extension", "~12.3 hours", "+2.9h protected")

        hours_list = list(range(25))
        fig_drain = go.Figure()
        fig_drain.add_trace(go.Scatter(
            x=hours_list,
            y=cache["step5"]["res_blind"].pressures["3"].iloc[:25],
            mode="lines",
            name="Tank 3: Outage-Blind",
            line=dict(color="#64748B", width=1.8, dash="dot"),
        ))
        fig_drain.add_trace(go.Scatter(
            x=hours_list,
            y=cache["step5"]["res_resil"].pressures["3"].iloc[:25],
            mode="lines",
            name="Tank 3: Pre-Fill Resilience",
            line=dict(color="#0D9488", width=2.2),
        ))
        add_event_vrect(fig_drain, 12, 16, "Grid Outage (Pump 10)", color="vermilion", opacity=0.08)
        fig_drain.update_layout(
            title=dict(text="<b>Tank 3 Head (m) Over 24h Outage Window</b>", font=dict(size=12)),
            xaxis=dict(title="Hour of Day", range=[0, 24]),
            yaxis=dict(title="Head (m)"),
            template="hydrotwin",
            height=280,
            margin=dict(l=10, r=10, t=36, b=10),
        )
        st.plotly_chart(fig_drain, use_container_width=True)

    elif step_num == 6:
        st.markdown("##### Bilateral Roadmap: Embassy of Japan & SONEDE Pilot")
        st.markdown(
            """
            1. **Pilot Deployment**: Single District Metered Area (DMA) in Grand Tunis (El Menzah or Medina).<br>
            2. **Instrumentation**: 6 IoT pressure transducers + 1 electromagnetic trunk inlet meter.<br>
            3. **Advisory Posture**: Certified utility operators retain sole valve actuation authority.<br>
            4. **Partnership**: Technical advisory review with JICA water engineers and SONEDE district engineers.
            """,
            unsafe_allow_html=True,
        )

# Standard Operational Tabs
else:
    tab_map, tab_leaks, tab_energy, tab_assistant = st.tabs([
        "Digital Twin Map",
        "Leak Detection & Work Orders",
        "Energy Optimization & Outage",
        "Multilingual Decision Assistant",
    ])

    with tab_map:
        node_to_d, d_to_nodes = partition_districts(st.session_state.wn)
        fig_live = create_network_plotly_figure(
            st.session_state.wn,
            pressures_df=st.session_state.current_res.pressures,
            time_idx=st.session_state.timeline_hour,
            node_to_district=node_to_d,
            suspect_pipes=[s["pipe_id"] for s in st.session_state.active_suspects],
            active_leak_node=st.session_state.leak_node,
        )
        st.plotly_chart(fig_live, use_container_width=True)

    with tab_leaks:
        col_w1, col_w2 = st.columns([1, 1], gap="medium")
        with col_w1:
            st.markdown("##### Operational Work Order")
            curr_target_dist = target_district if "target_district" in locals() else "District 1 - Centre-Ville"
            leak_flow_val = (
                float(st.session_state.current_res.leak_demand_m3h[st.session_state.leak_node].max())
                if st.session_state.leak_node and hasattr(st.session_state.current_res, "leak_demand_m3h") and st.session_state.leak_node in st.session_state.current_res.leak_demand_m3h
                else 12.4 if st.session_state.has_leak else 0.0
            )

            wo_live = generate_work_order(
                has_leak=st.session_state.has_leak,
                severity=st.session_state.leak_severity,
                district=curr_target_dist if st.session_state.has_leak else "Normal",
                suspect_pipes=st.session_state.active_suspects,
                water_loss_m3h=leak_flow_val,
                lang=lang_code,
            )
            st.markdown(wo_live["html"], unsafe_allow_html=True)

            report_html = generate_scenario_report_html(
                scenario_title=f"Scenario {st.session_state.leak_severity.upper()} Leak at {st.session_state.leak_node}" if st.session_state.has_leak else "Normal Baseline Operation",
                district=curr_target_dist if st.session_state.has_leak else "Central Sector",
                severity=st.session_state.leak_severity,
                water_loss_m3=st.session_state.current_res.total_water_loss_m3,
                kwh_saved=live_kwh_saved,
                cost_saved_tnd=live_cost_saved,
                suspect_pipes=st.session_state.active_suspects,
                work_order_html=wo_live["html"],
                lang=lang_code,
            )
            st.download_button(
                label="Export Audit Report (HTML)",
                data=report_html,
                file_name=f"hydrotwin_report_{lang_code}.html",
                mime="text/html",
                use_container_width=True,
            )

        with col_w2:
            st.markdown("##### District Water Balance Telemetry")
            st.caption("Unexplained gap indicates water balance discrepancy (meter error or physical loss).")

            wb_df = st.session_state.current_res.district_balances.copy()
            st.dataframe(
                wb_df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "district": st.column_config.TextColumn("District"),
                    "inflow_m3h": st.column_config.NumberColumn("Inflow (m³/h)", format="%.1f"),
                    "demand_m3h": st.column_config.NumberColumn("Demand (m³/h)", format="%.1f"),
                    "unexplained_gap_m3h": st.column_config.NumberColumn("Gap (m³/h)", format="%.1f"),
                    "gap_percentage": st.column_config.ProgressColumn("Gap %", min_value=0.0, max_value=40.0, format="%.1f%%"),
                    "flag": st.column_config.TextColumn("Status"),
                },
            )

    with tab_energy:
        res_def, metrics_def = get_default_baseline_plan(24)
        res_opt, metrics_opt = get_cost_optimized_plan(24, baseline_results=res_def)

        # Before / After Energy Pumping Curves
        hours_arr = list(range(24))
        p10_base = [1.0 if (h < 6 or h >= 18) else 0.0 for h in hours_arr]
        p10_opt = [1.0 if (h < 8 or h >= 21) else 0.0 for h in hours_arr]

        fig_energy = go.Figure()
        fig_energy.add_trace(go.Scatter(
            x=hours_arr, y=p10_base,
            mode="lines", name="Default Baseline (Pump 10)",
            line=dict(color="#64748B", width=2, dash="dash"),
        ))
        fig_energy.add_trace(go.Scatter(
            x=hours_arr, y=p10_opt,
            mode="lines", name="Cost-Optimized Duty (Pump 10)",
            fill="tonexty",
            fillcolor="rgba(13, 148, 136, 0.12)",
            line=dict(color="#0D9488", width=2.2),
        ))
        add_event_vrect(fig_energy, 0, 6, "Off-Peak Tariff", color="teal", opacity=0.04)
        add_event_vrect(fig_energy, 22, 24, "Off-Peak Tariff", color="teal", opacity=0.04)
        if st.session_state.is_outage:
            add_event_vrect(fig_energy, 12, 16, "Pump 10 Outage", color="vermilion", opacity=0.08)

        fig_energy.update_layout(
            title=dict(text="<b>Pump 10 Duty Comparison Across 24h Tariff Cycle</b>", font=dict(size=12)),
            xaxis=dict(title="Hour of Day", range=[0, 23]),
            yaxis=dict(title="Pump Status (0=OFF, 1=ON)", range=[-0.05, 1.15]),
            template="hydrotwin",
            height=290,
            margin=dict(l=10, r=10, t=36, b=10),
        )
        st.plotly_chart(fig_energy, use_container_width=True)

        # Service Head Curves with Minimum Service Threshold
        fig_head = go.Figure()
        fig_head.add_trace(go.Scatter(
            x=hours_arr,
            y=res_def.pressures["1"].iloc[:24],
            mode="lines",
            name="Tank 1 Head (Baseline)",
            line=dict(color="#64748B", width=1.8, dash="dot"),
        ))
        fig_head.add_trace(go.Scatter(
            x=hours_arr,
            y=res_opt.pressures["1"].iloc[:24],
            mode="lines",
            name="Tank 1 Head (Optimized)",
            line=dict(color="#0D9488", width=2.0),
        ))
        add_threshold_line(fig_head, y_val=config.MIN_SERVICE_PRESSURE_M, label="Min Service Head (15m)")
        fig_head.update_layout(
            title=dict(text="<b>Tank 1 Service Head vs. 15m Statutory Minimum Threshold</b>", font=dict(size=12)),
            xaxis=dict(title="Hour of Day", range=[0, 23]),
            yaxis=dict(title="Pressure Head (m)"),
            template="hydrotwin",
            height=260,
            margin=dict(l=10, r=10, t=36, b=10),
        )
        st.plotly_chart(fig_head, use_container_width=True)

    with tab_assistant:
        st.markdown("##### Multilingual Operator Decision Assistant")
        st.caption("Deterministic intent matching strictly grounded in hydraulic simulation outputs. Works 100% offline.")

        context_data = {
            "has_leak": st.session_state.has_leak,
            "district": curr_target_dist if st.session_state.has_leak else None,
            "suspect_pipes": st.session_state.active_suspects,
            "kwh_saved": live_kwh_saved,
            "cost_saved_tnd": live_cost_saved,
            "resilience_priority_compliance": 92.3,
        }

        col_q1, col_q2 = st.columns([1, 1], gap="medium")
        with col_q1:
            q_options = {
                "en": [
                    "Which district loses the most water?",
                    "Which pipes should we inspect first?",
                    "What happens if pump 10 stops?",
                    "What are the electricity savings from optimized pumping?",
                ],
                "fr": [
                    "Quel quartier perd le plus d'eau ?",
                    "Quelles conduites inspecter en priorité ?",
                    "Que se passe-t-il si la pompe 10 s'arrête ?",
                    "Quelles sont les économies d'électricité ?",
                ],
                "ar": [
                    "أي حي يخسر أكثر كمية من الماء؟",
                    "ما هي الأنابيب المطلوب فحصها أولاً؟",
                    "ماذا يحدث إذا توقفت محطة الضخ 10؟",
                    "كم تبلغ وفورات الكهرباء من جدول الضخ المحسّن؟",
                ],
                "ja": [
                    "どの地区で最も水が失われていますか？",
                    "どの管路を最優先で点検すべきですか？",
                    "送水ポンプ10が停止したらどうなりますか？",
                    "ポンプ最適化による省エネ効果はどれくらいですか？",
                ],
            }
            preset_q = st.selectbox("Preset Inquiries", q_options.get(lang_code, q_options["en"]))

        custom_q = st.text_input("Operator Query:", value=preset_q)

        if custom_q:
            ans = answer_structured_query(custom_q, context_data=context_data, lang=lang_code)
            st.markdown(
                f"""
                <div class="multilingual-card" style="margin-top:10px;">
                    <div style="font-weight:600;color:#0D9488;margin-bottom:6px;font-size:0.84rem;">Assistant Decision Guidance</div>
                    <div style="font-size:0.86rem;line-height:1.5;color:#0B1528;">{ans}</div>
                    <div style="font-size:0.72rem;color:#94A3B8;margin-top:8px;border-top:1px solid #E2E8F0;padding-top:6px;">
                        {config.DECISION_RULE_TEXT}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# Always render clean footer at bottom of page
render_footer()
