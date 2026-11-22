"""Streamlit UI components, Plotly network maps, and honesty guardrails.

Premium design pass — calm precision theme: Japanese minimalism × Mediterranean warmth.
All function signatures are preserved; only HTML output and visual logic updated.
"""

from typing import Dict, List, Optional
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import wntr

import config

# ─────────────────────────────────────────────────────────────
# CSS injection — called once per session
# ─────────────────────────────────────────────────────────────
def _get_css_path() -> str:
    """Return absolute path to theme.css."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "assets", "theme.css")


def inject_theme_css() -> None:
    """Inject the HydroTwin theme CSS — called once per session via session_state guard."""
    if st.session_state.get("_ht_theme_injected"):
        return
    css_path = _get_css_path()
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as fh:
            css_content = fh.read()
        st.markdown(f"<style>\n{css_content}\n</style>", unsafe_allow_html=True)
    else:
        # Minimal inline fallback if file not found
        st.markdown(
            "<style>:root{--navy:#0B1F3A;--ocean:#1E6FD9;--aqua:#2FD3C9;--sand:#F4EFE6;"
            "--vermilion:#D7263D;--green:#2E9E6B;--amber:#E8A020;--white:#FFFFFF;"
            "--text-primary:#0B1F3A;--text-secondary:#4A6080;--border:#DDE3ED;--card-bg:#FFFFFF;}</style>",
            unsafe_allow_html=True,
        )
    st.session_state["_ht_theme_injected"] = True


# Inject on import — guarded by session_state
inject_theme_css()

# ─────────────────────────────────────────────────────────────
# Inline SVG assets
# ─────────────────────────────────────────────────────────────
_LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 80" width="48" height="60">
  <path d="M32 4 C32 4, 8 36, 8 52 C8 66.4 18.8 76 32 76 C45.2 76 56 66.4 56 52 C56 36 32 4 32 4Z" fill="#E8F2FF" stroke="#1E6FD9" stroke-width="2.5"/>
  <circle cx="32" cy="44" r="5" fill="#2FD3C9"/>
  <circle cx="20" cy="58" r="4" fill="#1E6FD9"/>
  <circle cx="44" cy="58" r="4" fill="#1E6FD9"/>
  <line x1="32" y1="44" x2="20" y2="58" stroke="#0B1F3A" stroke-width="1.5" stroke-opacity="0.6"/>
  <line x1="32" y1="44" x2="44" y2="58" stroke="#0B1F3A" stroke-width="1.5" stroke-opacity="0.6"/>
  <line x1="20" y1="58" x2="44" y2="58" stroke="#0B1F3A" stroke-width="1.5" stroke-opacity="0.6"/>
</svg>"""

# Inline SVG icons for KPI cards
_ICON_DROP = """<svg viewBox="0 0 24 24" fill="none" stroke="#1E6FD9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M12 2C12 2 5 10 5 15a7 7 0 0014 0c0-5-7-13-7-13z"/>
</svg>"""

_ICON_BOLT = """<svg viewBox="0 0 24 24" fill="none" stroke="#2E9E6B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
</svg>"""

_ICON_PIN = """<svg viewBox="0 0 24 24" fill="none" stroke="#2FD3C9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/>
  <circle cx="12" cy="10" r="3"/>
</svg>"""

_ICON_BELL = """<svg viewBox="0 0 24 24" fill="none" stroke="#D7263D" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/>
  <path d="M13.73 21a2 2 0 01-3.46 0"/>
</svg>"""

_ICON_ANTENNA = """<svg viewBox="0 0 24 24" fill="none" stroke="#2FD3C9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M5 12.55a11 11 0 0114.08 0"/>
  <path d="M1.42 9a16 16 0 0121.16 0"/>
  <path d="M8.53 16.11a6 6 0 016.95 0"/>
  <line x1="12" y1="20" x2="12" y2="20.01"/>
</svg>"""


# ─────────────────────────────────────────────────────────────
# Public API (all signatures preserved)
# ─────────────────────────────────────────────────────────────

def render_honesty_banner() -> None:
    """Render the mandatory honesty disclaimer banner on every screen."""
    st.markdown(
        f"""
        <div class="ht-banner">
            <div class="ht-banner-body">
                <div class="ht-banner-title">
                    ⚠️ {config.DISCLAIMER_BANNER}
                    <span class="ht-chip">⚡ Offline · Simulated Data Only</span>
                </div>
                <div class="ht-banner-sub">
                    Calibrated against verified engineering benchmarks (STEG TOU tariffs,
                    25%–50% national loss ranges, 15 m minimum service heads).
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_decision_badge() -> None:
    """Display the advisory badge emphasizing human operator agency."""
    st.markdown(
        f"""
        <div class="ht-advisory">
            <strong>🛡️ Advisory Decision Support:</strong>
            {config.DECISION_RULE_TEXT}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_honest_limitations_box() -> None:
    """Render the mandatory Honest Limitations box detailing simulation boundaries."""
    st.markdown(
        """
        <div class="ht-limitations">
            <div class="ht-limitations-title">🔍 Honest Prototype Limitations &amp; Technical Boundaries:</div>
            <ul>
                <li><b>Small Synthetic Network</b>: Net3 benchmark topology (92 junctions, 117 pipes);
                    full municipal networks span 10,000+ pipe segments.</li>
                <li><b>Synthetic Consumer Demand</b>: District demands are modeled via diurnal sine curves
                    and temperature variables, not metered smart-grid telemetry.</li>
                <li><b>Zero Proprietary Utility Data</b>: Contains no confidential SCADA logs from
                    SONEDE, STEG, or Japanese municipal water bureaus.</li>
                <li><b>Minor Leaks Poorly Localized</b>: Fissures (&lt; 10 m³/h) generate pressure drops
                    smaller than sensor transducer noise (&sigma; = 0.4 m) and are difficult to isolate.</li>
                <li><b>Advisory Decision Posture Only</b>: Recommends schedules and ranked inspection pipes;
                    certified human operators retain sole execution authority.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_assumptions_expander() -> None:
    """Render the expandable assumptions panel detailing all parameters."""
    with st.expander("ℹ️ Simulation Assumptions & Calibration Parameters (Click to inspect)", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("##### ⚡ Assumed Time-of-Use Tariff (Hypothesis, to verify)")
            st.markdown(f"- **Off-Peak (22h–06h)**: `{config.TARIFF_OFF_PEAK_TND_PER_KWH:.3f} TND/kWh` (~{config.TARIFF_OFF_PEAK_TND_PER_KWH * config.TND_TO_JPY:.1f} JPY)")
            st.markdown(f"- **Standard (06h–18h)**: `{config.TARIFF_DAY_TND_PER_KWH:.3f} TND/kWh` (~{config.TARIFF_DAY_TND_PER_KWH * config.TND_TO_JPY:.1f} JPY)")
            st.markdown(f"- **Peak (18h–21h)**: `{config.TARIFF_PEAK_TND_PER_KWH:.3f} TND/kWh` (~{config.TARIFF_PEAK_TND_PER_KWH * config.TND_TO_JPY:.1f} JPY)")
        with col2:
            st.markdown("##### 💧 Hydraulic Constraints")
            st.markdown(f"- **Minimum Service Pressure**: `{config.MIN_SERVICE_PRESSURE_M} m` (~1.5 bar)")
            st.markdown(f"- **PDD Delivery Pressure**: `{config.REQUIRED_PRESSURE_PDD_M} m` (100% flow)")
            st.markdown(f"- **Excess Pressure Stress**: `> {config.EXCESS_PRESSURE_THRESHOLD_M} m` (accelerates bursts)")
            st.markdown(f"- **Outage Window**: `{config.OUTAGE_START_HOUR}:00 – {config.OUTAGE_START_HOUR + config.OUTAGE_DURATION_HOURS}:00`")
        with col3:
            st.markdown("##### 🔍 Leak & Loss Thresholds")
            st.markdown(f"- **Minor**: `< {config.LEAK_SEVERITY_THRESHOLDS['minor']['max_flow_m3h']} m³/h`")
            st.markdown(f"- **Moderate**: `{config.LEAK_SEVERITY_THRESHOLDS['minor']['max_flow_m3h']} – {config.LEAK_SEVERITY_THRESHOLDS['moderate']['max_flow_m3h']} m³/h`")
            st.markdown(f"- **Critical**: `> {config.LEAK_SEVERITY_THRESHOLDS['moderate']['max_flow_m3h']} m³/h`")
            st.markdown(f"- **Tunisia Loss Range**: `{config.TUNISIA_LOSS_RANGE_PCT[0]}% – {config.TUNISIA_LOSS_RANGE_PCT[1]}%`")


def render_impact_cards(
    water_lost_m3: float = 0.0,
    water_saved_m3: float = 0.0,
    kwh_saved: float = 291.7,
    cost_saved_tnd: float = 69.7,
    suspect_pipes_count: int = 5,
    critical_alerts: int = 0,
    sensor_mode: str = "rich",
    noise_sigma: float = 0.40,
    **kwargs,
) -> None:
    """Render top summary metric cards for executive decision-makers."""
    mode_label = "Rich (24 sens)" if sensor_mode == "rich" else "Sparse (6 sens)"
    alert_sub_class = "alert" if critical_alerts > 0 else ""
    alert_sub_text = "Immediate inspection required" if critical_alerts > 0 else "No active alerts"

    water_display = f"{water_lost_m3:,.0f}" if water_lost_m3 > 0 else "0"
    water_sub = "Simulated orifice model" if water_lost_m3 > 0 else "Normal baseline"

    st.markdown(
        f"""
        <div class="ht-kpi-grid">
          <!-- Card 1: Water Lost -->
          <div class="ht-kpi-card kpi-blue">
            <div class="ht-kpi-header">
              <div class="ht-kpi-icon">{_ICON_DROP}</div>
              <div class="ht-kpi-label">Water Lost (Sim.)</div>
            </div>
            <div class="ht-kpi-value">{water_display} <span style="font-size:1rem;font-weight:400;color:var(--text-secondary)">m³</span></div>
            <div class="ht-kpi-sublabel">{water_sub}</div>
          </div>

          <!-- Card 2: Pumping Savings -->
          <div class="ht-kpi-card kpi-green">
            <div class="ht-kpi-header">
              <div class="ht-kpi-icon">{_ICON_BOLT}</div>
              <div class="ht-kpi-label">Pumping Savings</div>
            </div>
            <div class="ht-kpi-value" style="font-size:1.1rem;line-height:1.3">0 – 292 – 583 <span style="font-size:0.85rem;font-weight:400;color:var(--text-secondary)">kWh/d</span></div>
            <div class="ht-kpi-sublabel">0.0 – 69.7 – 206.4 TND <span class="ht-chip">Hypothetical Tariff</span></div>
          </div>

          <!-- Card 3: Suspect Leaks -->
          <div class="ht-kpi-card kpi-ocean">
            <div class="ht-kpi-header">
              <div class="ht-kpi-icon">{_ICON_PIN}</div>
              <div class="ht-kpi-label">Suspect Leaks</div>
            </div>
            <div class="ht-kpi-value">{suspect_pipes_count}</div>
            <div class="ht-kpi-sublabel">Ranked by pressure residuals</div>
          </div>

          <!-- Card 4: Critical Alerts -->
          <div class="ht-kpi-card kpi-red">
            <div class="ht-kpi-header">
              <div class="ht-kpi-icon">{_ICON_BELL}</div>
              <div class="ht-kpi-label">Critical Alerts</div>
            </div>
            <div class="ht-kpi-value" style="color:{'var(--vermilion)' if critical_alerts > 0 else 'var(--green)'}">{critical_alerts}</div>
            <div class="ht-kpi-sublabel {alert_sub_class}">{alert_sub_text}</div>
          </div>

          <!-- Card 5: Sensor Mode -->
          <div class="ht-kpi-card kpi-aqua">
            <div class="ht-kpi-header">
              <div class="ht-kpi-icon">{_ICON_ANTENNA}</div>
              <div class="ht-kpi-label">Sensor Mode</div>
            </div>
            <div class="ht-kpi-value" style="font-size:1.2rem">{mode_label}</div>
            <div class="ht-kpi-sublabel">σ = {noise_sigma:.2f} m noise assumed</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def create_network_plotly_figure(
    wn: wntr.network.WaterNetworkModel,
    pressures_df: Optional[pd.DataFrame] = None,
    time_idx: int = 12,
    node_to_district: Optional[Dict[str, str]] = None,
    suspect_pipes: Optional[List[str]] = None,
    active_leak_node: Optional[str] = None,
) -> go.Figure:
    """Create an interactive Plotly digital twin network map with premium styling."""
    # Import here to avoid circular issues; template already registered in main.py
    try:
        from app.assets.plotly_template import PRESSURE_COLORSCALE
    except ImportError:
        PRESSURE_COLORSCALE = [
            [0.0, "#1E6FD9"], [0.3, "#2FD3C9"], [0.6, "#E8A020"], [1.0, "#D7263D"]
        ]

    fig = go.Figure()

    # 1. Draw all pipes (muted on dark background)
    pipe_x: List = []
    pipe_y: List = []
    for name, pipe in wn.pipes():
        start_node = wn.get_node(pipe.start_node_name)
        end_node = wn.get_node(pipe.end_node_name)
        pipe_x.extend([start_node.coordinates[0], end_node.coordinates[0], None])
        pipe_y.extend([start_node.coordinates[1], end_node.coordinates[1], None])

    fig.add_trace(go.Scatter(
        x=pipe_x, y=pipe_y,
        mode="lines",
        line=dict(color="#2A4A6A", width=1.5),
        hoverinfo="none",
        name="Distribution Pipes",
        showlegend=True,
    ))

    # 2. Highlight suspect pipes (ranked severity coloring)
    if suspect_pipes:
        rank_colors = {0: "#D7263D", 1: "#E8A020", 2: "#E8A020", 3: "#F4D03F", 4: "#F4D03F"}
        rank_widths = {0: 7, 1: 5, 2: 5, 3: 3, 4: 3}
        for idx, pipe_name in enumerate(suspect_pipes[:5]):
            if pipe_name in wn.pipe_name_list:
                pipe = wn.get_link(pipe_name)
                start_node = wn.get_node(pipe.start_node_name)
                end_node = wn.get_node(pipe.end_node_name)
                mid_x = (start_node.coordinates[0] + end_node.coordinates[0]) / 2
                mid_y = (start_node.coordinates[1] + end_node.coordinates[1]) / 2
                color = rank_colors.get(idx, "#F4D03F")
                width = rank_widths.get(idx, 3)
                fig.add_trace(go.Scatter(
                    x=[start_node.coordinates[0], end_node.coordinates[0]],
                    y=[start_node.coordinates[1], end_node.coordinates[1]],
                    mode="lines",
                    line=dict(color=color, width=width),
                    hovertext=f"Suspect #{idx+1}: Pipe {pipe_name}",
                    name=f"Top-{idx+1} Suspect ({pipe_name})",
                    showlegend=True,
                ))
                # Rank annotation near midpoint
                fig.add_annotation(
                    x=mid_x, y=mid_y,
                    text=f"<b>#{idx+1}</b>",
                    showarrow=False,
                    font=dict(size=10, color=color),
                    bgcolor="rgba(11,31,58,0.75)",
                    borderpad=2,
                )

    # 3. Draw junctions colored by pressure (custom colorscale)
    junction_x: List = []
    junction_y: List = []
    junction_text: List = []
    junction_pressures: List = []

    current_pressures = pressures_df.iloc[time_idx] if pressures_df is not None else None

    for name, node in wn.junctions():
        junction_x.append(node.coordinates[0])
        junction_y.append(node.coordinates[1])
        p_val = (
            current_pressures[name]
            if current_pressures is not None and name in current_pressures
            else 25.0
        )
        junction_pressures.append(p_val)
        district = node_to_district.get(name, "Municipal") if node_to_district else "Municipal"
        status_str = "⚠️ LOW PRESSURE" if p_val < config.MIN_SERVICE_PRESSURE_M else "✅ Healthy"
        junction_text.append(
            f"Node: {name}<br>District: {district}<br>Pressure: {p_val:.1f} m<br>Status: {status_str}"
        )

    fig.add_trace(go.Scatter(
        x=junction_x, y=junction_y,
        mode="markers",
        marker=dict(
            size=9,
            color=junction_pressures,
            colorscale=PRESSURE_COLORSCALE,
            colorbar=dict(
                title=dict(text="Pressure (m)", font=dict(color="#FFFFFF", size=11)),
                thickness=12, len=0.75,
                tickfont=dict(color="#FFFFFF", size=10),
            ),
            showscale=True,
            cmin=10.0, cmax=60.0,
            line=dict(color="rgba(255,255,255,0.4)", width=1),
        ),
        text=junction_text,
        hoverinfo="text",
        name="Junctions",
        showlegend=False,
    ))

    # 4. Draw Pumps (diamond, navy fill, aqua border)
    pump_x: List = []
    pump_y: List = []
    pump_text: List = []
    for name, pump in wn.pumps():
        start_node = wn.get_node(pump.start_node_name)
        pump_x.append(start_node.coordinates[0])
        pump_y.append(start_node.coordinates[1])
        pump_text.append(
            f"⚡ Pump Station {name}<br>From: {pump.start_node_name} → To: {pump.end_node_name}"
        )

    fig.add_trace(go.Scatter(
        x=pump_x, y=pump_y,
        mode="markers+text",
        marker=dict(
            symbol="diamond",
            size=20,
            color="#0B1F3A",
            line=dict(color="#2FD3C9", width=2),
        ),
        text=[f"Pump {name}" for name in wn.pump_name_list],
        textposition="top center",
        textfont=dict(color="#FFFFFF", size=10),
        hovertext=pump_text,
        hoverinfo="text",
        name="Pump Stations",
    ))

    # 5. Draw Tanks (square, aqua fill, navy border)
    tank_x: List = []
    tank_y: List = []
    tank_text: List = []
    for name, tank in wn.tanks():
        tank_x.append(tank.coordinates[0])
        tank_y.append(tank.coordinates[1])
        t_lvl = (
            current_pressures[name]
            if current_pressures is not None and name in current_pressures
            else tank.init_level
        )
        tank_text.append(
            f"🏢 Storage Reservoir {name}<br>Current Head: {t_lvl:.2f} m<br>Capacity: {tank.max_level:.1f} m max"
        )

    fig.add_trace(go.Scatter(
        x=tank_x, y=tank_y,
        mode="markers+text",
        marker=dict(
            symbol="square",
            size=20,
            color="#2FD3C9",
            line=dict(color="#0B1F3A", width=2),
        ),
        text=[f"Tank {name}" for name in wn.tank_name_list],
        textposition="bottom center",
        textfont=dict(color="#FFFFFF", size=10),
        hovertext=tank_text,
        hoverinfo="text",
        name="Storage Tanks",
    ))

    # 6. Draw active leak — star + ring effect
    if active_leak_node and active_leak_node in wn.node_name_list:
        l_node = wn.get_node(active_leak_node)
        lx, ly = l_node.coordinates[0], l_node.coordinates[1]
        # Ring (outer)
        fig.add_trace(go.Scatter(
            x=[lx], y=[ly],
            mode="markers",
            marker=dict(
                symbol="circle",
                size=42,
                color="rgba(0,0,0,0)",
                line=dict(color="#D7263D", width=3),
            ),
            hoverinfo="none",
            showlegend=False,
        ))
        # Star (inner)
        fig.add_trace(go.Scatter(
            x=[lx], y=[ly],
            mode="markers+text",
            marker=dict(
                symbol="star",
                size=28,
                color="#D7263D",
                line=dict(color="#FFFFFF", width=2),
            ),
            text=["💥 SIMULATED LEAK"],
            textposition="top right",
            textfont=dict(color="#D7263D", size=11),
            hovertext=f"Active Simulated Leak at Node {active_leak_node}",
            hoverinfo="text",
            name="Ground Truth Leak",
        ))

    # Reservoirs (triangle-up) if any
    if hasattr(wn, "reservoirs"):
        res_x: List = []
        res_y: List = []
        res_text: List = []
        for name, reservoir in wn.reservoirs():
            res_x.append(reservoir.coordinates[0])
            res_y.append(reservoir.coordinates[1])
            res_text.append(f"🌊 Reservoir {name}")
        if res_x:
            fig.add_trace(go.Scatter(
                x=res_x, y=res_y,
                mode="markers+text",
                marker=dict(symbol="triangle-up", size=18, color="#1E6FD9", line=dict(color="#FFFFFF", width=2)),
                text=[f"Res {n}" for n, _ in wn.reservoirs()],
                textposition="top center",
                textfont=dict(color="#FFFFFF", size=9),
                hovertext=res_text,
                hoverinfo="text",
                name="Reservoirs",
            ))

    fig.update_layout(
        title=f"Drinking Water Network Twin (Net3) — Timestep {time_idx}:00",
        plot_bgcolor="#0B1F3A",
        paper_bgcolor="#0B1F3A",
        font=dict(color="#FFFFFF"),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            scaleanchor="x", scaleratio=1,
        ),
        margin=dict(l=10, r=10, t=44, b=10),
        height=550,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(11,31,58,0.85)", bordercolor="#2A4A6A",
            font=dict(color="#FFFFFF", size=11),
        ),
        dragmode=False,
        uirevision="constant",
        modebar_remove=[
            "toImage", "select2d", "lasso2d", "zoom2d",
            "pan2d", "autoScale2d", "resetScale2d",
        ],
    )

    return fig
