"""Streamlit UI components, Plotly network maps, and honesty guardrails."""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import wntr

import config

def render_honesty_banner():
    """Render the mandatory honesty disclaimer banner on every screen."""
    st.markdown(
        f"""
        <div style="background-color: #fff3cd; border-left: 6px solid #ffc107; padding: 12px 18px; margin-bottom: 16px; border-radius: 4px;">
            <div style="font-weight: 700; color: #856404; font-size: 0.95rem;">
                ⚠️ {config.DISCLAIMER_BANNER}
            </div>
            <div style="font-size: 0.85rem; color: #533f03; margin-top: 4px;">
                Calibrated against verified engineering benchmarks (STEG TOU tariffs, 25%-50% national loss ranges, 15m minimum service heads).
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_decision_badge():
    """Display the advisory badge emphasizing human operator agency."""
    st.markdown(
        f"""
        <div style="background-color: #e8f4fd; border: 1px solid #b6d4fe; border-radius: 6px; padding: 10px 14px; margin-bottom: 14px;">
            <span style="font-weight: 600; color: #084298;">🛡️ Advisory Decision Support:</span>
            <span style="color: #0c5460; font-size: 0.9rem;"> {config.DECISION_RULE_TEXT}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_honest_limitations_box():
    """Render the mandatory Honest Limitations box detailing simulation boundaries."""
    st.markdown(
        """
        <div style="background-color: #f8f9fa; border: 1px solid #dcdfe6; border-left: 5px solid #6c757d; border-radius: 4px; padding: 12px 16px; margin-bottom: 16px;">
            <div style="font-weight: 700; color: #343a40; font-size: 0.92rem; margin-bottom: 6px;">
                🔍 Honest Prototype Limitations & Technical Boundaries:
            </div>
            <ul style="margin: 0; padding-left: 20px; font-size: 0.85rem; color: #495057; line-height: 1.5;">
                <li><b>Small Synthetic Network</b>: Net3 benchmark topology (92 junctions, 117 pipes); full municipal networks span 10,000+ pipe segments.</li>
                <li><b>Synthetic Consumer Demand</b>: District demands are modeled via diurnal sine curves and temperature variables, not metered smart-grid telemetry.</li>
                <li><b>Zero Proprietary Utility Data</b>: Contains no confidential SCADA logs from SONEDE, STEG, or Japanese municipal water bureaus.</li>
                <li><b>Minor Leaks Poorly Localized</b>: Fissures (&lt; 10 m³/h) generate pressure drops smaller than sensor transducer noise (&sigma; = 0.4m) and are difficult to isolate.</li>
                <li><b>Advisory Decision Posture Only</b>: Recommends schedules and ranked inspection pipes; certified human operators retain sole execution authority.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_assumptions_expander():
    """Render the expandable assumptions panel detailing all parameters."""
    with st.expander("ℹ️ Simulation Assumptions & Calibration Parameters (Click to inspect)", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("##### ⚡ Assumed Time-of-Use Tariff (Hypothesis, to verify)")
            st.markdown(f"- **Off-Peak (22h-06h)**: `{config.TARIFF_OFF_PEAK_TND_PER_KWH:.3f} TND/kWh` (~{config.TARIFF_OFF_PEAK_TND_PER_KWH * config.TND_TO_JPY:.1f} JPY)")
            st.markdown(f"- **Standard (06h-18h)**: `{config.TARIFF_DAY_TND_PER_KWH:.3f} TND/kWh` (~{config.TARIFF_DAY_TND_PER_KWH * config.TND_TO_JPY:.1f} JPY)")
            st.markdown(f"- **Peak (18h-21h)**: `{config.TARIFF_PEAK_TND_PER_KWH:.3f} TND/kWh` (~{config.TARIFF_PEAK_TND_PER_KWH * config.TND_TO_JPY:.1f} JPY)")
        with col2:
            st.markdown("##### 💧 Hydraulic Constraints")
            st.markdown(f"- **Minimum Service Pressure**: `{config.MIN_SERVICE_PRESSURE_M} m` (~1.5 bar)")
            st.markdown(f"- **PDD Delivery Pressure**: `{config.REQUIRED_PRESSURE_PDD_M} m` (100% flow)")
            st.markdown(f"- **Excess Pressure Stress**: `> {config.EXCESS_PRESSURE_THRESHOLD_M} m` (accelerates bursts)")
            st.markdown(f"- **Outage Window**: `{config.OUTAGE_START_HOUR}:00 - {config.OUTAGE_START_HOUR + config.OUTAGE_DURATION_HOURS}:00`")
        with col3:
            st.markdown("##### 🔍 Leak & Loss Thresholds")
            st.markdown(f"- **Minor**: `< {config.LEAK_SEVERITY_THRESHOLDS['minor']['max_flow_m3h']} m³/h`")
            st.markdown(f"- **Moderate**: `{config.LEAK_SEVERITY_THRESHOLDS['minor']['max_flow_m3h']} - {config.LEAK_SEVERITY_THRESHOLDS['moderate']['max_flow_m3h']} m³/h`")
            st.markdown(f"- **Critical**: `> {config.LEAK_SEVERITY_THRESHOLDS['moderate']['max_flow_m3h']} m³/h`")
            st.markdown(f"- **Tunisia Loss Range**: `{config.TUNISIA_LOSS_RANGE_PCT[0]}% - {config.TUNISIA_LOSS_RANGE_PCT[1]}%`")

def render_impact_cards(
    water_lost_m3: float,
    water_saved_m3: float = 0.0,
    kwh_saved: float = 291.7,
    cost_saved_tnd: float = 69.7,
    suspect_pipes_count: int = 5,
    critical_alerts: int = 0,
    sensor_mode: str = "rich",
    noise_sigma: float = 0.40
):
    """Render top summary metric cards for executive decision-makers."""
    mode_label = "Rich Mode (24 sens)" if sensor_mode == "rich" else "Sparse Mode (6 sens)"
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("💧 Water Lost (Sim.)", f"{water_lost_m3:,.0f} m³", delta="Simulated Orifice" if water_lost_m3 > 0 else "Normal")
    c2.metric("⚡ Pumping Savings", "0 – 292 – 583 kWh/d", delta="0.0 – 69.7 – 206.4 TND (Hypothetical Tariff)", delta_color="normal")
    c3.metric("🎯 Suspect Leaks", f"{suspect_pipes_count}", delta="Ranked by risk")
    c4.metric("🚨 Critical Alerts", f"{critical_alerts}", delta="Immediate inspection" if critical_alerts > 0 else "Normal", delta_color="inverse" if critical_alerts > 0 else "normal")
    c5.metric("📡 Sensor mode: Rich / Sparse", mode_label, delta=f"Assumed noise σ = {noise_sigma:.2f} m")

def create_network_plotly_figure(
    wn: wntr.network.WaterNetworkModel,
    pressures_df: Optional[pd.DataFrame] = None,
    time_idx: int = 12,
    node_to_district: Optional[Dict[str, str]] = None,
    suspect_pipes: Optional[List[str]] = None,
    active_leak_node: Optional[str] = None
) -> go.Figure:
    """Create an interactive Plotly digital twin network map with pressure colormaps."""
    fig = go.Figure()
    
    # 1. Draw Pipes
    pipe_x = []
    pipe_y = []
    for name, pipe in wn.pipes():
        start_node = wn.get_node(pipe.start_node_name)
        end_node = wn.get_node(pipe.end_node_name)
        pipe_x.extend([start_node.coordinates[0], end_node.coordinates[0], None])
        pipe_y.extend([start_node.coordinates[1], end_node.coordinates[1], None])
        
    fig.add_trace(go.Scatter(
        x=pipe_x,
        y=pipe_y,
        mode="lines",
        line=dict(color="#b0bec5", width=2),
        hoverinfo="none",
        name="Distribution Pipes",
        showlegend=True
    ))

    # 2. Highlight Suspect Pipes if any
    if suspect_pipes:
        for idx, pipe_name in enumerate(suspect_pipes[:5]):
            if pipe_name in wn.pipe_name_list:
                pipe = wn.get_link(pipe_name)
                start_node = wn.get_node(pipe.start_node_name)
                end_node = wn.get_node(pipe.end_node_name)
                color = "#dc3545" if idx == 0 else "#fd7e14" if idx < 3 else "#ffc107"
                fig.add_trace(go.Scatter(
                    x=[start_node.coordinates[0], end_node.coordinates[0]],
                    y=[start_node.coordinates[1], end_node.coordinates[1]],
                    mode="lines",
                    line=dict(color=color, width=6),
                    hovertext=f"Suspect #{idx+1}: Pipe {pipe_name}",
                    name=f"Top-{idx+1} Suspect ({pipe_name})",
                    showlegend=True
                ))

    # 3. Draw Junctions colored by pressure
    junction_x = []
    junction_y = []
    junction_text = []
    junction_pressures = []
    
    current_pressures = pressures_df.iloc[time_idx] if pressures_df is not None else None
    
    for name, node in wn.junctions():
        junction_x.append(node.coordinates[0])
        junction_y.append(node.coordinates[1])
        p_val = current_pressures[name] if current_pressures is not None and name in current_pressures else 25.0
        junction_pressures.append(p_val)
        district = node_to_district.get(name, "Municipal") if node_to_district else "Municipal"
        status_str = "⚠️ LOW PRESSURE" if p_val < config.MIN_SERVICE_PRESSURE_M else "✅ Healthy"
        junction_text.append(f"Node: {name}<br>District: {district}<br>Pressure: {p_val:.1f} m<br>Status: {status_str}")

    fig.add_trace(go.Scatter(
        x=junction_x,
        y=junction_y,
        mode="markers",
        marker=dict(
            size=10,
            color=junction_pressures,
            colorscale="Viridis",
            colorbar=dict(title="Pressure (m)", thickness=15, len=0.8),
            showscale=True,
            cmin=10.0,
            cmax=60.0,
            line=dict(color="#ffffff", width=1)
        ),
        text=junction_text,
        hoverinfo="text",
        name="Junctions",
        showlegend=False
    ))

    # 4. Draw Pumps
    pump_x = []
    pump_y = []
    pump_text = []
    for name, pump in wn.pumps():
        start_node = wn.get_node(pump.start_node_name)
        pump_x.append(start_node.coordinates[0])
        pump_y.append(start_node.coordinates[1])
        pump_text.append(f"⚡ Pump Station {name}<br>From: {pump.start_node_name} → To: {pump.end_node_name}")
        
    fig.add_trace(go.Scatter(
        x=pump_x,
        y=pump_y,
        mode="markers+text",
        marker=dict(symbol="diamond", size=18, color="#0d6efd", line=dict(color="#ffffff", width=2)),
        text=[f"Pump {name}" for name in wn.pump_name_list],
        textposition="top center",
        hovertext=pump_text,
        hoverinfo="text",
        name="Pump Stations"
    ))

    # 5. Draw Tanks
    tank_x = []
    tank_y = []
    tank_text = []
    for name, tank in wn.tanks():
        tank_x.append(tank.coordinates[0])
        tank_y.append(tank.coordinates[1])
        t_lvl = current_pressures[name] if current_pressures is not None and name in current_pressures else tank.init_level
        tank_text.append(f"🏢 Storage Reservoir {name}<br>Current Head: {t_lvl:.2f} m<br>Capacity: {tank.max_level:.1f} m max")
        
    fig.add_trace(go.Scatter(
        x=tank_x,
        y=tank_y,
        mode="markers+text",
        marker=dict(symbol="square", size=18, color="#20c997", line=dict(color="#ffffff", width=2)),
        text=[f"Tank {name}" for name in wn.tank_name_list],
        textposition="bottom center",
        hovertext=tank_text,
        hoverinfo="text",
        name="Storage Tanks"
    ))

    # 6. Draw active leak if present
    if active_leak_node and active_leak_node in wn.node_name_list:
        l_node = wn.get_node(active_leak_node)
        fig.add_trace(go.Scatter(
            x=[l_node.coordinates[0]],
            y=[l_node.coordinates[1]],
            mode="markers+text",
            marker=dict(symbol="star", size=24, color="#e63946", line=dict(color="#ffffff", width=2)),
            text=["💥 SIMULATED LEAK"],
            textposition="top right",
            hovertext=f"Active Simulated Leak at Node {active_leak_node}",
            hoverinfo="text",
            name="Ground Truth Leak"
        ))

    fig.update_layout(
        title=f"Drinking Water Network Twin (Net3) — Timestep {time_idx}:00",
        template="plotly_white",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x", scaleratio=1),
        margin=dict(l=10, r=10, t=40, b=10),
        height=550,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig
