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
_LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 76" width="48" height="58" fill="none">
  <defs>
    <linearGradient id="dropGrad" x1="32" y1="2" x2="32" y2="74" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#2FD3C9" stop-opacity="0.9"/>
      <stop offset="45%" stop-color="#1E6FD9" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#0B1F3A" stop-opacity="0.98"/>
    </linearGradient>
    <linearGradient id="innerGlow" x1="16" y1="20" x2="48" y2="60" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <path d="M32 3 C32 3 10 32 10 50 C10 63 19.8 73 32 73 C44.2 73 54 63 54 50 C54 32 32 3 32 3 Z"
        fill="url(#dropGrad)" stroke="#2FD3C9" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M32 7 C32 7 14 34 14 50 C14 60.5 22 69 32 69 C42 69 50 60.5 50 50 C50 34 32 7 32 7 Z"
        fill="url(#innerGlow)" opacity="0.35"/>
  <line x1="32" y1="36" x2="22" y2="54" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-opacity="0.85"/>
  <line x1="32" y1="36" x2="42" y2="54" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-opacity="0.85"/>
  <line x1="22" y1="54" x2="42" y2="54" stroke="#2FD3C9" stroke-width="2" stroke-linecap="round" stroke-opacity="0.9"/>
  <circle cx="32" cy="36" r="4.5" fill="#2FD3C9" stroke="#FFFFFF" stroke-width="1.8"/>
  <circle cx="22" cy="54" r="4" fill="#1E6FD9" stroke="#FFFFFF" stroke-width="1.6"/>
  <circle cx="42" cy="54" r="4" fill="#FFFFFF" stroke="#2FD3C9" stroke-width="1.6"/>
</svg>"""

# Inline SVG icons for KPI cards
_ICON_DROP = """<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#1E6FD9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M12 2C12 2 5 10 5 15a7 7 0 0014 0c0-5-7-13-7-13z"/>
</svg>"""

_ICON_BOLT = """<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#2E9E6B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
</svg>"""

_ICON_PIN = """<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#1EBAB0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/>
  <circle cx="12" cy="10" r="3"/>
</svg>"""

_ICON_BELL = """<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#D7263D" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/>
  <path d="M13.73 21a2 2 0 01-3.46 0"/>
</svg>"""

_ICON_ANTENNA = """<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#1E6FD9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M5 12.55a11 11 0 0114.08 0"/>
  <path d="M1.42 9a16 16 0 0121.16 0"/>
  <path d="M8.53 16.11a6 6 0 016.95 0"/>
  <line x1="12" y1="20" x2="12" y2="20.01"/>
</svg>"""

_ICON_RIBBON_WAVE = """<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="#2FD3C9" stroke-width="1.8">
  <path d="M1 9c2-2 4-2 6 0s4 2 6 0s2-2 2-2"/>
  <path d="M1 5c2-2 4-2 6 0s4 2 6 0s2-2 2-2" opacity="0.6"/>
</svg>"""


# ─────────────────────────────────────────────────────────────
# Public API (all signatures preserved)
# ─────────────────────────────────────────────────────────────

def render_hero_header() -> None:
    """Render the full-width hero header with logo, title, tagline, and ribbon."""
    st.markdown(
        f"""
        <div class="ht-hero">
          <div class="ht-hero-left">
            <div class="ht-hero-logo">{_LOGO_SVG}</div>
            <div class="ht-hero-text">
              <h1 class="ht-hero-title">HydroTwin</h1>
              <div class="ht-hero-tagline">Digital twin &amp; AI for drinking-water networks</div>
            </div>
          </div>
          <div class="ht-hero-ribbon">
            <span class="ht-ribbon-badge">{_ICON_RIBBON_WAVE} Japan × Tunisia</span>
            <span class="ht-ribbon-sub">Water + Energy Track · Hackathon 2026</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    """Render professional footer with team placeholder, event credit, and simulated data notice."""
    st.markdown(
        """
        <div class="ht-footer">
          <div>
            <b>HydroTwin</b> · Digital Twin for Water &amp; Energy · Hackathon Embassy of Japan in Tunisia
          </div>
          <div>
            ⚠️ <i>Simulated engineering data · Calibrated for demonstration only</i>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
    mode_name = "Rich" if sensor_mode == "rich" else "Sparse"
    mode_chip = "24 Sensors" if sensor_mode == "rich" else "6 Sens + 1 Fault"
    mode_class = "ht-chip-offline" if sensor_mode == "rich" else "ht-chip"
    
    alert_sub_class = "alert" if critical_alerts > 0 else "nominal"
    alert_sub_text = "Immediate field inspection required" if critical_alerts > 0 else "All zones within normal head"
    alert_val_color = "var(--vermilion)" if critical_alerts > 0 else "var(--green)"

    water_display = f"{water_lost_m3:,.0f}" if water_lost_m3 > 0 else "0"
    water_sub = "Simulated orifice model" if water_lost_m3 > 0 else "Baseline nominal operation"

    st.markdown(
        f"""
        <div class="ht-kpi-grid">
          <!-- Card 1: Water Lost -->
          <div class="ht-kpi-card kpi-water">
            <div class="ht-kpi-header">
              <div class="ht-kpi-icon">{_ICON_DROP}</div>
              <div class="ht-kpi-label">Water Lost (Sim.)</div>
            </div>
            <div class="ht-kpi-value">{water_display} <span class="ht-kpi-unit">m³</span></div>
            <div class="ht-kpi-sublabel">{water_sub}</div>
          </div>

          <!-- Card 2: Pumping Savings -->
          <div class="ht-kpi-card kpi-energy">
            <div class="ht-kpi-header">
              <div class="ht-kpi-icon">{_ICON_BOLT}</div>
              <div class="ht-kpi-label">Pumping Savings</div>
            </div>
            <div class="ht-kpi-value-range">0 – 292 – 583 <span class="ht-kpi-unit">kWh/d</span></div>
            <div class="ht-kpi-sublabel">
              <span>0.0 – 69.7 – 206.4 TND</span>
              <span class="ht-chip ht-chip-tariff">Hypothetical Tariff</span>
            </div>
          </div>

          <!-- Card 3: Suspect Leaks -->
          <div class="ht-kpi-card kpi-suspect">
            <div class="ht-kpi-header">
              <div class="ht-kpi-icon">{_ICON_PIN}</div>
              <div class="ht-kpi-label">Suspect Leaks</div>
            </div>
            <div class="ht-kpi-value">{suspect_pipes_count} <span class="ht-kpi-unit">pipes</span></div>
            <div class="ht-kpi-sublabel">Ranked by pressure residuals</div>
          </div>

          <!-- Card 4: Critical Alerts -->
          <div class="ht-kpi-card kpi-alert">
            <div class="ht-kpi-header">
              <div class="ht-kpi-icon">{_ICON_BELL}</div>
              <div class="ht-kpi-label">Critical Alerts</div>
            </div>
            <div class="ht-kpi-value" style="color:{alert_val_color}">{critical_alerts}</div>
            <div class="ht-kpi-sublabel {alert_sub_class}">{alert_sub_text}</div>
          </div>

          <!-- Card 5: Sensor Mode -->
          <div class="ht-kpi-card kpi-sensor">
            <div class="ht-kpi-header">
              <div class="ht-kpi-icon">{_ICON_ANTENNA}</div>
              <div class="ht-kpi-label">Sensor Telemetry</div>
            </div>
            <div class="ht-kpi-value" style="font-size:1.4rem">
              {mode_name}
              <span class="ht-chip {mode_class}" style="vertical-align:middle;margin-left:6px">{mode_chip}</span>
            </div>
            <div class="ht-kpi-sublabel">Assumed sensor noise &sigma; = {noise_sigma:.2f} m</div>
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
    dark_mode: bool = True,
    **kwargs,
) -> go.Figure:
    """Create an interactive Plotly digital twin network map with calm precision styling.
    
    Features:
    - Perceptually uniform colorscale (blue -> aqua -> amber -> red) with clear m units
    - Soft translucent district boundary hulls with district labels
    - Pipe widths proportional to diameter/capacity
    - Pumps, tanks, and reservoirs with distinct clean markers and labels
    - Ground truth leak shown with concentric pulse-style rings + star marker
    - Top-5 suspect pipes highlighted with rank badges (#1-#5) and tooltips
    - Clutter-free Plotly controls
    """
    try:
        from app.assets.plotly_template import PRESSURE_COLORSCALE
    except ImportError:
        PRESSURE_COLORSCALE = [
            [0.0, "#1E6FD9"], [0.3, "#2FD3C9"], [0.6, "#E8A020"], [1.0, "#D7263D"]
        ]
    from scipy.spatial import ConvexHull

    fig = go.Figure()
    bg_color = "#0B1F3A" if dark_mode else "#FFFFFF"
    text_color = "#FFFFFF" if dark_mode else "#0B1F3A"
    pipe_base_color = "#243E5E" if dark_mode else "#BDD0E4"

    # 1. District Boundaries — Soft Translucent Convex Hulls
    if node_to_district:
        district_to_coords: Dict[str, List] = {}
        for node_name, dist_name in node_to_district.items():
            if node_name in wn.node_name_list:
                district_to_coords.setdefault(dist_name, []).append(
                    wn.get_node(node_name).coordinates
                )

        hull_palette = [
            ("rgba(30, 111, 217, 0.07)", "rgba(30, 111, 217, 0.35)"),
            ("rgba(47, 211, 201, 0.07)", "rgba(47, 211, 201, 0.35)"),
            ("rgba(46, 158, 107, 0.07)", "rgba(46, 158, 107, 0.35)"),
            ("rgba(232, 160, 32, 0.07)", "rgba(232, 160, 32, 0.35)"),
            ("rgba(155, 89, 182, 0.07)", "rgba(155, 89, 182, 0.35)"),
        ]

        for idx, (dist_name, coords) in enumerate(district_to_coords.items()):
            if len(coords) >= 3:
                try:
                    pts = np.array(coords)
                    hull = ConvexHull(pts)
                    hull_pts = pts[hull.vertices]
                    hx = list(hull_pts[:, 0]) + [hull_pts[0, 0]]
                    hy = list(hull_pts[:, 1]) + [hull_pts[0, 1]]
                    fill_c, line_c = hull_palette[idx % len(hull_palette)]
                    
                    fig.add_trace(go.Scatter(
                        x=hx, y=hy,
                        fill="toself",
                        fillcolor=fill_c,
                        line=dict(color=line_c, width=1.2, dash="dot"),
                        hoverinfo="text",
                        hovertext=f"District Zone: {dist_name}",
                        name=dist_name.split(" - ")[-1],
                        showlegend=False,
                    ))

                    # District Centroid Label
                    cx = float(np.mean(hull_pts[:, 0]))
                    cy = float(np.mean(hull_pts[:, 1]))
                    short_label = dist_name.split(" - ")[-1] if " - " in dist_name else dist_name
                    fig.add_annotation(
                        x=cx, y=cy,
                        text=f"<b>{short_label}</b>",
                        showarrow=False,
                        font=dict(size=10, color="rgba(255,255,255,0.55)" if dark_mode else "rgba(11,31,58,0.55)"),
                        bgcolor="rgba(11,31,58,0.45)" if dark_mode else "rgba(255,255,255,0.65)",
                        bordercolor="rgba(255,255,255,0.1)" if dark_mode else "rgba(11,31,58,0.1)",
                        borderpad=3,
                    )
                except Exception:
                    pass

    # 2. Distribution Pipes (width scaled by diameter)
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
        line=dict(color=pipe_base_color, width=1.8),
        hoverinfo="none",
        name="Distribution Pipes",
        showlegend=True,
    ))

    # 3. Top-5 Suspect Pipes (ranked severity highlighting with badges)
    if suspect_pipes:
        rank_colors = {0: "#D7263D", 1: "#E86420", 2: "#E8A020", 3: "#F4D03F", 4: "#F4D03F"}
        rank_widths = {0: 7.0, 1: 5.5, 2: 4.5, 3: 3.5, 4: 3.5}
        for idx, pipe_name in enumerate(suspect_pipes[:5]):
            if pipe_name in wn.pipe_name_list:
                pipe = wn.get_link(pipe_name)
                start_node = wn.get_node(pipe.start_node_name)
                end_node = wn.get_node(pipe.end_node_name)
                mid_x = (start_node.coordinates[0] + end_node.coordinates[0]) / 2
                mid_y = (start_node.coordinates[1] + end_node.coordinates[1]) / 2
                color = rank_colors.get(idx, "#F4D03F")
                width = rank_widths.get(idx, 3.5)

                fig.add_trace(go.Scatter(
                    x=[start_node.coordinates[0], end_node.coordinates[0]],
                    y=[start_node.coordinates[1], end_node.coordinates[1]],
                    mode="lines",
                    line=dict(color=color, width=width),
                    hovertext=f"🎯 Rank #{idx+1} Suspect: Pipe {pipe_name}<br>Priority Inspection Recommended",
                    hoverinfo="text",
                    name=f"Rank #{idx+1} Suspect ({pipe_name})",
                    showlegend=True,
                ))

                # Midpoint badge annotation
                fig.add_annotation(
                    x=mid_x, y=mid_y,
                    text=f"<b>#{idx+1}</b>",
                    showarrow=False,
                    font=dict(size=10, color=color),
                    bgcolor="rgba(11,31,58,0.85)" if dark_mode else "rgba(255,255,255,0.9)",
                    bordercolor=color,
                    borderwidth=1,
                    borderpad=2,
                )

    # 4. Junctions Colored by Pressure
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
        district = node_to_district.get(name, "Municipal Sector") if node_to_district else "Municipal Sector"
        status_str = "⚠️ Low Head (&lt; 15m)" if p_val < config.MIN_SERVICE_PRESSURE_M else "✅ Healthy Service"
        junction_text.append(
            f"<b>Node:</b> {name}<br><b>District:</b> {district}<br><b>Pressure:</b> {p_val:.1f} m<br><b>Status:</b> {status_str}"
        )

    fig.add_trace(go.Scatter(
        x=junction_x, y=junction_y,
        mode="markers",
        marker=dict(
            size=9,
            color=junction_pressures,
            colorscale=PRESSURE_COLORSCALE,
            colorbar=dict(
                title=dict(text="Pressure (m)", font=dict(color=text_color, size=11)),
                thickness=12, len=0.75,
                tickfont=dict(color=text_color, size=10),
            ),
            showscale=True,
            cmin=10.0, cmax=60.0,
            line=dict(color="rgba(255,255,255,0.3)" if dark_mode else "rgba(0,0,0,0.15)", width=1),
        ),
        text=junction_text,
        hoverinfo="text",
        name="Junction Nodes",
        showlegend=False,
    ))

    # 5. Pumps (Diamond, distinct clean styling)
    pump_x: List = []
    pump_y: List = []
    pump_text: List = []
    for name, pump in wn.pumps():
        start_node = wn.get_node(pump.start_node_name)
        pump_x.append(start_node.coordinates[0])
        pump_y.append(start_node.coordinates[1])
        pump_text.append(
            f"⚡ <b>Pump Station {name}</b><br>Intake: {pump.start_node_name} → Discharge: {pump.end_node_name}"
        )

    if pump_x:
        fig.add_trace(go.Scatter(
            x=pump_x, y=pump_y,
            mode="markers+text",
            marker=dict(
                symbol="diamond",
                size=22,
                color="#0B1F3A",
                line=dict(color="#2FD3C9", width=2.5),
            ),
            text=[f"Pump {name}" for name in wn.pump_name_list],
            textposition="top center",
            textfont=dict(color=text_color, size=10, family="Inter, sans-serif"),
            hovertext=pump_text,
            hoverinfo="text",
            name="Pump Stations",
        ))

    # 6. Storage Tanks (Square, aqua fill, distinct styling)
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
            f"🏢 <b>Elevated Storage Tank {name}</b><br>Current Head: {t_lvl:.2f} m<br>Capacity Limit: {tank.max_level:.1f} m"
        )

    if tank_x:
        fig.add_trace(go.Scatter(
            x=tank_x, y=tank_y,
            mode="markers+text",
            marker=dict(
                symbol="square",
                size=22,
                color="#2FD3C9",
                line=dict(color="#0B1F3A", width=2.5),
            ),
            text=[f"Tank {name}" for name in wn.tank_name_list],
            textposition="bottom center",
            textfont=dict(color=text_color, size=10, family="Inter, sans-serif"),
            hovertext=tank_text,
            hoverinfo="text",
            name="Elevated Tanks",
        ))

    # 7. Reservoirs (Triangle, ocean blue)
    if hasattr(wn, "reservoirs"):
        res_x: List = []
        res_y: List = []
        res_text: List = []
        for name, reservoir in wn.reservoirs():
            res_x.append(reservoir.coordinates[0])
            res_y.append(reservoir.coordinates[1])
            res_text.append(f"🌊 <b>Source Reservoir {name}</b><br>Primary intake source")
        if res_x:
            fig.add_trace(go.Scatter(
                x=res_x, y=res_y,
                mode="markers+text",
                marker=dict(
                    symbol="triangle-up",
                    size=22,
                    color="#1E6FD9",
                    line=dict(color="#FFFFFF", width=2),
                ),
                text=[f"Res {n}" for n, _ in wn.reservoirs()],
                textposition="top center",
                textfont=dict(color=text_color, size=10, family="Inter, sans-serif"),
                hovertext=res_text,
                hoverinfo="text",
                name="Source Reservoirs",
            ))

    # 8. Active Leak Marker (Concentric rings + Star)
    if active_leak_node and active_leak_node in wn.node_name_list:
        l_node = wn.get_node(active_leak_node)
        lx, ly = l_node.coordinates[0], l_node.coordinates[1]
        
        # Outer pulsing static ring
        fig.add_trace(go.Scatter(
            x=[lx], y=[ly],
            mode="markers",
            marker=dict(
                symbol="circle",
                size=44,
                color="rgba(0,0,0,0)",
                line=dict(color="#D7263D", width=2.5),
            ),
            hoverinfo="none",
            showlegend=False,
        ))
        # Inner ring
        fig.add_trace(go.Scatter(
            x=[lx], y=[ly],
            mode="markers",
            marker=dict(
                symbol="circle",
                size=28,
                color="rgba(215,38,61,0.2)",
                line=dict(color="#D7263D", width=1.5),
            ),
            hoverinfo="none",
            showlegend=False,
        ))
        # Star center
        fig.add_trace(go.Scatter(
            x=[lx], y=[ly],
            mode="markers+text",
            marker=dict(
                symbol="star",
                size=22,
                color="#D7263D",
                line=dict(color="#FFFFFF", width=2),
            ),
            text=["💥 GROUND TRUTH LEAK"],
            textposition="top right",
            textfont=dict(color="#D7263D", size=11, family="Inter, sans-serif"),
            hovertext=f"🚨 Active Ground-Truth Incident: Node {active_leak_node}",
            hoverinfo="text",
            name="Ground Truth Leak",
        ))

    # Layout styling
    fig.update_layout(
        title=dict(
            text=f"<b>Drinking Water Distribution Twin (Net3)</b> · Simulation Timestep {time_idx}:00",
            font=dict(color=text_color, size=14, family="Inter, sans-serif"),
        ),
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=text_color, family="Inter, sans-serif"),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            scaleanchor="x", scaleratio=1,
        ),
        margin=dict(l=10, r=10, t=44, b=10),
        height=540,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(11,31,58,0.85)" if dark_mode else "rgba(255,255,255,0.85)",
            bordercolor="rgba(255,255,255,0.15)" if dark_mode else "#DDE3ED",
            borderwidth=1,
            font=dict(color=text_color, size=11),
        ),
        dragmode=False,
        uirevision="constant",
        modebar_remove=[
            "toImage", "select2d", "lasso2d", "zoom2d",
            "pan2d", "autoScale2d", "resetScale2d",
        ],
    )

    return fig
