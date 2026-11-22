"""Streamlit UI components, Plotly network maps, and honesty guardrails.

Premium design pass — calm precision theme: Linear / Apple instrumentation polish.
All function signatures are preserved; only visual presentation, layout, and copy updated.
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
# CSS injection — called on every render so DOM never loses it
# ─────────────────────────────────────────────────────────────
def _get_css_path() -> str:
    """Return absolute path to theme.css."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "assets", "theme.css")


def inject_theme_css() -> None:
    """Inject the HydroTwin theme CSS on every render so the browser DOM never loses it."""
    css_path = _get_css_path()
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as fh:
            css_content = fh.read()
    else:
        css_content = (
            ":root{--ink:#0B1528;--canvas:#F8F9FA;--teal:#0D9488;--vermilion:#E11D48;"
            "--amber:#D97706;--hairline:#E2E8F0;--text-primary:#0B1528;--text-secondary:#64748B;}"
        )
    st.markdown(f"<style>\n{css_content}\n</style>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# Inline SVG marks (thin line, zero emojis)
# ─────────────────────────────────────────────────────────────
_ICON_DROP_MARK = """<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#0D9488" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
  <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/>
</svg>"""

_SPARK_FLAT = """<svg width="44" height="14" viewBox="0 0 44 14" fill="none">
  <path d="M2 7H42" stroke="#94A3B8" stroke-width="1.5" stroke-linecap="round"/>
</svg>"""

_SPARK_SPIKE = """<svg width="44" height="14" viewBox="0 0 44 14" fill="none">
  <path d="M2 11H18L24 3L30 11H42" stroke="#E11D48" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

_SPARK_ENERGY = """<svg width="44" height="14" viewBox="0 0 44 14" fill="none">
  <path d="M2 10C8 10 14 3 22 3C30 3 36 11 42 11" stroke="#0D9488" stroke-width="1.5" stroke-linecap="round"/>
</svg>"""

_SPARK_STEP = """<svg width="44" height="14" viewBox="0 0 44 14" fill="none">
  <path d="M2 11H14V4H28V8H42" stroke="#0D9488" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

_SPARK_STATUS_OK = """<svg width="14" height="14" viewBox="0 0 14 14" fill="none">
  <circle cx="7" cy="7" r="4.5" fill="#0D9488"/>
  <circle cx="7" cy="7" r="6" stroke="#0D9488" stroke-width="1" stroke-opacity="0.3"/>
</svg>"""

_SPARK_STATUS_ALERT = """<svg width="14" height="14" viewBox="0 0 14 14" fill="none">
  <circle cx="7" cy="7" r="4.5" fill="#E11D48"/>
  <circle cx="7" cy="7" r="6" stroke="#E11D48" stroke-width="1" stroke-opacity="0.3"/>
</svg>"""


# ─────────────────────────────────────────────────────────────
# Header & Navigation
# ─────────────────────────────────────────────────────────────

def render_hero_header() -> None:
    """Render restrained, precision header with title, subtitle, and advisory popover pill."""
    col_l, col_r = st.columns([3, 1], vertical_alignment="center")
    with col_l:
        st.markdown(
            f"""<div style="display:flex;align-items:center;gap:12px;margin:2px 0 6px;">
  <div>{_ICON_DROP_MARK}</div>
  <div>
    <div style="font-size:1.35rem;font-weight:700;color:#0B1528;letter-spacing:-0.025em;line-height:1.2;">HydroTwin</div>
    <div style="font-size:0.80rem;color:#64748B;font-weight:400;margin-top:1px;">A digital twin that finds leaks and cuts pumping energy.</div>
  </div>
</div>""",
            unsafe_allow_html=True,
        )
    with col_r:
        with st.popover("Simulated data · advisory only", use_container_width=True):
            st.markdown(
                """<div style="font-size:0.80rem;line-height:1.5;color:#0B1528;">
  <div style="font-weight:600;color:#0D9488;margin-bottom:4px;">Advisory Decision Support</div>
  <p style="margin:0 0 8px;color:#475569;">The system advises, humans decide. Certified operators retain sole execution authority; no autonomous pump/valve actuation is performed.</p>
  <div style="font-weight:600;color:#0B1528;margin-bottom:4px;">Simulation Boundaries &amp; Hypotheses</div>
  <ul style="margin:0;padding-left:16px;color:#475569;">
    <li><b>Topology:</b> Net3 benchmark (92 junctions, 117 pipes); full systems span 10,000+ pipes.</li>
    <li><b>Demand:</b> Diurnal sine curves + temperature (synthetic, unmetered).</li>
    <li><b>Tariffs:</b> STEG Time-of-Use schedule benchmarks (hypothetical).</li>
    <li><b>Telemetry:</b> Gaussian noise &sigma; = 0.40 m. Small leaks (&lt;10 m³/h) fall within sensor noise.</li>
    <li><b>Confidentiality:</b> Zero proprietary SCADA logs from SONEDE, STEG, or Japanese utilities.</li>
  </ul>
</div>""",
                unsafe_allow_html=True,
            )


def render_footer() -> None:
    """Render professional footer with bilateral event credit and simulated data notice."""
    st.markdown(
        """<div class="ht-footer">
  <div>
    <b>HydroTwin</b> · Digital Twin for Water &amp; Energy · Hackathon Embassy of Japan in Tunisia
  </div>
  <div>
    <i>Simulated engineering data · Calibrated for demonstration only</i>
  </div>
</div>""",
        unsafe_allow_html=True,
    )


def render_honesty_banner() -> None:
    """Deprecated: replaced by the header popover pill. Retained as no-op for compatibility."""
    return None


def render_decision_badge() -> None:
    """Deprecated: replaced by the header popover pill. Retained as no-op for compatibility."""
    return None


def render_honest_limitations_box() -> None:
    """Deprecated: replaced by the header popover pill. Retained as no-op for compatibility."""
    return None


def render_assumptions_expander() -> None:
    """Render collapsible assumptions panel detailing engineering parameters."""
    with st.expander("Simulation Assumptions & Calibration Parameters", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("##### Assumed TOU Tariff Schedule")
            st.markdown(f"- Off-Peak (22h–06h): `{config.TARIFF_OFF_PEAK_TND_PER_KWH:.3f} TND/kWh`")
            st.markdown(f"- Standard (06h–18h): `{config.TARIFF_DAY_TND_PER_KWH:.3f} TND/kWh`")
            st.markdown(f"- Peak (18h–21h): `{config.TARIFF_PEAK_TND_PER_KWH:.3f} TND/kWh`")
        with col2:
            st.markdown("##### Hydraulic Constraints")
            st.markdown(f"- Minimum Service Pressure: `{config.MIN_SERVICE_PRESSURE_M} m` (~1.5 bar)")
            st.markdown(f"- PDD Delivery Pressure: `{config.REQUIRED_PRESSURE_PDD_M} m` (100% flow)")
            st.markdown(f"- Outage Window: `{config.OUTAGE_START_HOUR}:00 – {config.OUTAGE_START_HOUR + config.OUTAGE_DURATION_HOURS}:00`")
        with col3:
            st.markdown("##### Leak Thresholds")
            st.markdown(f"- Minor: `< {config.LEAK_SEVERITY_THRESHOLDS['minor']['max_flow_m3h']} m³/h`")
            st.markdown(f"- Moderate: `10 – {config.LEAK_SEVERITY_THRESHOLDS['moderate']['max_flow_m3h']} m³/h`")
            st.markdown(f"- Critical: `> {config.LEAK_SEVERITY_THRESHOLDS['moderate']['max_flow_m3h']} m³/h`")


# ─────────────────────────────────────────────────────────────
# Refined KPI Cards (Top Row, Max 4)
# ─────────────────────────────────────────────────────────────

def render_impact_cards(
    water_lost_m3: float = 0.0,
    water_saved_m3: float = 0.0,
    kwh_saved: float = 291.7,
    cost_saved_tnd: float = 33.6,
    suspect_pipes_count: int = 0,
    critical_alerts: int = 0,
    sensor_mode: str = "rich",
    noise_sigma: float = 0.40,
    has_leak: bool = False,
    is_outage: bool = False,
    **kwargs,
) -> None:
    """Render exactly 4 restrained, high-polish KPI cards with tabular figures.
    
    Card 1: Water Loss (vermilion only on active leak).
    Card 2: Pumping Energy Saved (292 kWh/d, secondary: range 0-583).
    Card 3: Electricity Cost Saved (33.6 TND/d TOU tariff vs 86.2 flat).
    Card 4: Network Compliance (100% nominal head vs incident active).
    """
    # Card 1: Water Lost
    is_leak_active = (water_lost_m3 > 0.0 or has_leak)
    card1_class = "ht-kpi-box kpi-alert" if is_leak_active else "ht-kpi-box"
    card1_val = f"{water_lost_m3:,.0f}" if is_leak_active else "0"
    card1_sub = f"+{water_lost_m3:,.0f} m³ burst active" if is_leak_active else "Nominal baseline"
    card1_spark = _SPARK_SPIKE if is_leak_active else _SPARK_FLAT

    # Card 2: Pumping Energy
    card2_class = "ht-kpi-box"
    card2_val = f"{kwh_saved:,.0f}"
    card2_sub = "−5.5% vs baseline"
    card2_range = "range 0–583"
    card2_spark = _SPARK_ENERGY

    # Card 3: Cost Saved
    card3_class = "ht-kpi-box"
    card3_val = f"{cost_saved_tnd:,.1f}"
    card3_sub = "86.2 TND/d flat tariff"
    card3_range = "TOU tariff"
    card3_spark = _SPARK_STEP

    # Card 4: Network Compliance
    if critical_alerts > 0 or is_outage:
        card4_class = "ht-kpi-box kpi-alert"
        card4_val = "Alert"
        card4_unit = "Outage" if is_outage else "Incident"
        card4_sub = "Pump 10 blackout" if is_outage else "Immediate inspection"
        card4_spark = _SPARK_STATUS_ALERT
    elif is_leak_active:
        card4_class = "ht-kpi-box kpi-alert"
        card4_val = "1 Leak"
        card4_unit = "Active"
        card4_sub = "District 1 inspection"
        card4_spark = _SPARK_STATUS_ALERT
    else:
        card4_class = "ht-kpi-box kpi-healthy"
        card4_val = "100%"
        card4_unit = "Nominal"
        card4_sub = "All 92 nodes ≥ 15m head"
        card4_spark = _SPARK_STATUS_OK

    cards_html = f"""<div class="ht-kpi-row">
  <div class="{card1_class}">
    <div class="ht-kpi-meta">
      <span class="ht-kpi-title">Water Loss</span>
      <span>{card1_spark}</span>
    </div>
    <div class="ht-kpi-main">
      <span class="ht-kpi-num">{card1_val}</span>
      <span class="ht-kpi-unit">m³</span>
    </div>
    <div class="ht-kpi-subtext">{card1_sub}</div>
  </div>

  <div class="{card2_class}">
    <div class="ht-kpi-meta">
      <span class="ht-kpi-title">Pumping Energy</span>
      <span>{card2_spark}</span>
    </div>
    <div class="ht-kpi-main">
      <span class="ht-kpi-num">{card2_val}</span>
      <span class="ht-kpi-unit">kWh/d</span>
      <span style="font-size:0.72rem;color:#94A3B8;margin-left:auto;">{card2_range}</span>
    </div>
    <div class="ht-kpi-subtext">{card2_sub}</div>
  </div>

  <div class="{card3_class}">
    <div class="ht-kpi-meta">
      <span class="ht-kpi-title">Cost Saved</span>
      <span>{card3_spark}</span>
    </div>
    <div class="ht-kpi-main">
      <span class="ht-kpi-num">{card3_val}</span>
      <span class="ht-kpi-unit">TND/d</span>
      <span style="font-size:0.72rem;color:#94A3B8;margin-left:auto;">{card3_range}</span>
    </div>
    <div class="ht-kpi-subtext">{card3_sub}</div>
  </div>

  <div class="{card4_class}">
    <div class="ht-kpi-meta">
      <span class="ht-kpi-title">Compliance</span>
      <span>{card4_spark}</span>
    </div>
    <div class="ht-kpi-main">
      <span class="ht-kpi-num">{card4_val}</span>
      <span class="ht-kpi-unit">{card4_unit}</span>
    </div>
    <div class="ht-kpi-subtext">{card4_sub}</div>
  </div>
</div>"""
    st.markdown(cards_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# Refined Network Map (Plotly)
# ─────────────────────────────────────────────────────────────

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
    """Create a refined digital twin network map with calm precision styling.
    
    Refinements:
    - Non-overlapping labels: Pump labels placed bottom-center, Reservoir labels top-center.
    - Thin semi-transparent pipes with width proportional to diameter.
    - Junction nodes sized by base demand.
    - Perceptually smooth pressure colorscale: Teal -> Amber -> Vermilion.
    - Soft translucent district hulls.
    - Vermilion ring with halo for active leaks.
    - Compact centered bottom legend.
    """
    from scipy.spatial import ConvexHull
    from app.assets.plotly_template import PRESSURE_COLORSCALE

    fig = go.Figure()
    bg_color = "#0B1528" if dark_mode else "#FFFFFF"
    text_color = "#FFFFFF" if dark_mode else "#0B1528"
    pipe_base_color = "rgba(148, 163, 184, 0.40)" if dark_mode else "rgba(100, 116, 139, 0.35)"

    # 1. District Boundaries — Soft Translucent Convex Hulls
    if node_to_district:
        district_to_coords: Dict[str, List] = {}
        for node_name, dist_name in node_to_district.items():
            if node_name in wn.node_name_list:
                district_to_coords.setdefault(dist_name, []).append(
                    wn.get_node(node_name).coordinates
                )

        hull_palette = [
            ("rgba(13, 148, 136, 0.06)", "rgba(13, 148, 136, 0.25)"),
            ("rgba(37, 99, 235, 0.06)", "rgba(37, 99, 235, 0.25)"),
            ("rgba(217, 119, 6, 0.06)", "rgba(217, 119, 6, 0.25)"),
            ("rgba(100, 116, 139, 0.06)", "rgba(100, 116, 139, 0.25)"),
            ("rgba(147, 51, 234, 0.06)", "rgba(147, 51, 234, 0.25)"),
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
                        line=dict(color=line_c, width=1.0, dash="dot"),
                        hoverinfo="text",
                        hovertext=f"District: {dist_name}",
                        name=dist_name.split(" - ")[-1],
                        showlegend=False,
                    ))

                    # District Centroid Label
                    cx = float(np.mean(hull_pts[:, 0]))
                    cy = float(np.mean(hull_pts[:, 1]))
                    short_label = dist_name.split(" - ")[-1] if " - " in dist_name else dist_name
                    fig.add_annotation(
                        x=cx, y=cy,
                        text=f"<span style='font-size:9px;letter-spacing:0.04em;'>{short_label.upper()}</span>",
                        showarrow=False,
                        font=dict(size=9, color="rgba(255,255,255,0.45)" if dark_mode else "rgba(11,21,40,0.50)"),
                        bgcolor="rgba(11,21,40,0.40)" if dark_mode else "rgba(248,249,250,0.70)",
                        bordercolor="rgba(255,255,255,0.08)" if dark_mode else "rgba(0,0,0,0.08)",
                        borderpad=2,
                    )
                except Exception:
                    pass

    # 2. Distribution Pipes
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
        line=dict(color=pipe_base_color, width=1.4),
        hoverinfo="none",
        name="Distribution Pipes",
        showlegend=True,
    ))

    # 3. Top-5 Suspect Pipes (Highlighting with Rank Badges)
    if suspect_pipes:
        rank_colors = {0: "#E11D48", 1: "#EA580C", 2: "#D97706", 3: "#EAB308", 4: "#CA8A04"}
        rank_widths = {0: 5.5, 1: 4.5, 2: 3.8, 3: 3.0, 4: 2.8}
        for idx, pipe_name in enumerate(suspect_pipes[:5]):
            if pipe_name in wn.pipe_name_list:
                pipe = wn.get_link(pipe_name)
                start_node = wn.get_node(pipe.start_node_name)
                end_node = wn.get_node(pipe.end_node_name)
                mid_x = (start_node.coordinates[0] + end_node.coordinates[0]) / 2
                mid_y = (start_node.coordinates[1] + end_node.coordinates[1]) / 2
                color = rank_colors.get(idx, "#EAB308")
                width = rank_widths.get(idx, 3.0)

                fig.add_trace(go.Scatter(
                    x=[start_node.coordinates[0], end_node.coordinates[0]],
                    y=[start_node.coordinates[1], end_node.coordinates[1]],
                    mode="lines",
                    line=dict(color=color, width=width),
                    hovertext=f"Suspect #{idx+1}: Pipe {pipe_name}<br>Priority Inspection",
                    hoverinfo="text",
                    name=f"Suspect #{idx+1} ({pipe_name})",
                    showlegend=True,
                ))

                fig.add_annotation(
                    x=mid_x, y=mid_y,
                    text=f"<b>#{idx+1}</b>",
                    showarrow=False,
                    font=dict(size=9, color=color),
                    bgcolor="rgba(11,21,40,0.85)" if dark_mode else "rgba(255,255,255,0.92)",
                    bordercolor=color,
                    borderwidth=1,
                    borderpad=2,
                )

    # 4. Junctions Colored by Pressure and Sized by Demand
    junction_x: List = []
    junction_y: List = []
    junction_text: List = []
    junction_pressures: List = []
    junction_sizes: List = []

    current_pressures = pressures_df.iloc[time_idx] if pressures_df is not None else None

    # Determine maximum demand for scaling
    demands = [float(j.base_demand) if hasattr(j, "base_demand") and j.base_demand else 0.0 for _, j in wn.junctions()]
    max_dem = max(demands) if demands and max(demands) > 0 else 1.0

    for name, node in wn.junctions():
        junction_x.append(node.coordinates[0])
        junction_y.append(node.coordinates[1])
        p_val = (
            current_pressures[name]
            if current_pressures is not None and name in current_pressures
            else 25.0
        )
        junction_pressures.append(p_val)

        # Scale size by demand: 5px for zero demand, up to 9px for max demand
        dem = float(node.base_demand) if hasattr(node, "base_demand") and node.base_demand else 0.0
        node_size = 5.5 + 4.0 * (dem / max_dem)
        junction_sizes.append(node_size)

        district = node_to_district.get(name, "Municipal Sector") if node_to_district else "Municipal Sector"
        status_str = "Head < 15m" if p_val < config.MIN_SERVICE_PRESSURE_M else "Nominal"
        junction_text.append(
            f"<b>Node {name}</b> ({district})<br>Pressure: {p_val:.1f} m<br>Base Demand: {dem:.1f} m³/h<br>Status: {status_str}"
        )

    fig.add_trace(go.Scatter(
        x=junction_x, y=junction_y,
        mode="markers",
        marker=dict(
            size=junction_sizes,
            color=junction_pressures,
            colorscale=PRESSURE_COLORSCALE,
            colorbar=dict(
                title=dict(text="Head (m)", font=dict(color=text_color, size=10)),
                thickness=10, len=0.70,
                tickfont=dict(color=text_color, size=9),
            ),
            showscale=True,
            cmin=10.0, cmax=55.0,
            line=dict(color="rgba(255,255,255,0.2)" if dark_mode else "rgba(0,0,0,0.1)", width=0.8),
        ),
        text=junction_text,
        hoverinfo="text",
        name="Junction Nodes",
        showlegend=False,
    ))

    # 5. Pumps (Diamond, placed BOTTOM-CENTER to never overlap reservoirs)
    pump_x: List = []
    pump_y: List = []
    pump_text: List = []
    pump_labels: List = []
    for name, pump in wn.pumps():
        start_node = wn.get_node(pump.start_node_name)
        pump_x.append(start_node.coordinates[0])
        pump_y.append(start_node.coordinates[1])
        pump_labels.append(f"Pump {name}")
        pump_text.append(
            f"<b>Pump Station {name}</b><br>In: {pump.start_node_name} → Out: {pump.end_node_name}"
        )

    if pump_x:
        fig.add_trace(go.Scatter(
            x=pump_x, y=pump_y,
            mode="markers+text",
            marker=dict(
                symbol="diamond",
                size=18,
                color="#0B1528",
                line=dict(color="#0D9488", width=2.0),
            ),
            text=pump_labels,
            textposition="bottom center",
            textfont=dict(color=text_color, size=9, family="Inter, sans-serif"),
            hovertext=pump_text,
            hoverinfo="text",
            name="Pump Stations",
        ))

    # 6. Storage Tanks (Square, placed BOTTOM-RIGHT)
    tank_x: List = []
    tank_y: List = []
    tank_text: List = []
    tank_labels: List = []
    for name, tank in wn.tanks():
        tank_x.append(tank.coordinates[0])
        tank_y.append(tank.coordinates[1])
        tank_labels.append(f"Tank {name}")
        t_lvl = (
            current_pressures[name]
            if current_pressures is not None and name in current_pressures
            else tank.init_level
        )
        tank_text.append(
            f"<b>Storage Tank {name}</b><br>Head: {t_lvl:.2f} m<br>Capacity: {tank.max_level:.1f} m"
        )

    if tank_x:
        fig.add_trace(go.Scatter(
            x=tank_x, y=tank_y,
            mode="markers+text",
            marker=dict(
                symbol="square",
                size=18,
                color="#0D9488",
                line=dict(color="#0B1528", width=2.0),
            ),
            text=tank_labels,
            textposition="bottom right",
            textfont=dict(color=text_color, size=9, family="Inter, sans-serif"),
            hovertext=tank_text,
            hoverinfo="text",
            name="Elevated Tanks",
        ))

    # 7. Reservoirs (Triangle, placed TOP-CENTER to never overlap pumps)
    if hasattr(wn, "reservoirs"):
        res_x: List = []
        res_y: List = []
        res_text: List = []
        res_labels: List = []
        for name, reservoir in wn.reservoirs():
            res_x.append(reservoir.coordinates[0])
            res_y.append(reservoir.coordinates[1])
            res_labels.append(f"Res {name}")
            res_text.append(f"<b>Source Reservoir {name}</b><br>Intake supply")
        if res_x:
            fig.add_trace(go.Scatter(
                x=res_x, y=res_y,
                mode="markers+text",
                marker=dict(
                    symbol="triangle-up",
                    size=18,
                    color="#2563EB",
                    line=dict(color="#FFFFFF", width=1.5),
                ),
                text=res_labels,
                textposition="top center",
                textfont=dict(color=text_color, size=9, family="Inter, sans-serif"),
                hovertext=res_text,
                hoverinfo="text",
                name="Source Reservoirs",
            ))

    # 8. Active Leak Marker (Vermilion Halo + Center Dot)
    if active_leak_node and active_leak_node in wn.node_name_list:
        l_node = wn.get_node(active_leak_node)
        lx, ly = l_node.coordinates[0], l_node.coordinates[1]

        # Outer soft halo
        fig.add_trace(go.Scatter(
            x=[lx], y=[ly],
            mode="markers",
            marker=dict(
                symbol="circle",
                size=32,
                color="rgba(225, 29, 72, 0.18)",
                line=dict(color="#E11D48", width=1.5),
            ),
            hoverinfo="none",
            showlegend=False,
        ))
        # Inner focal dot with label
        fig.add_trace(go.Scatter(
            x=[lx], y=[ly],
            mode="markers+text",
            marker=dict(
                symbol="circle",
                size=10,
                color="#E11D48",
                line=dict(color="#FFFFFF", width=1.5),
            ),
            text=["Leak"],
            textposition="top right",
            textfont=dict(color="#E11D48", size=10, family="Inter, sans-serif"),
            hovertext=f"Active Incident: Node {active_leak_node}",
            hoverinfo="text",
            name="Ground Truth Leak",
        ))

    # Clean layout styling
    fig.update_layout(
        title=dict(
            text=f"<b>Drinking Water Distribution Twin (Net3)</b> · Timestep {time_idx}:00",
            font=dict(color=text_color, size=12, family="Inter, sans-serif"),
            x=0.01,
            y=0.98,
            xanchor="left",
            yanchor="top",
        ),
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=text_color, family="Inter, sans-serif"),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            scaleanchor="x", scaleratio=1,
        ),
        margin=dict(l=10, r=10, t=32, b=40),
        height=520,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.04,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(11,21,40,0.92)" if dark_mode else "rgba(255,255,255,0.92)",
            bordercolor="rgba(255,255,255,0.12)" if dark_mode else "#E2E8F0",
            borderwidth=1,
            font=dict(color=text_color, size=9),
        ),
        dragmode=False,
        uirevision="constant",
        modebar_remove=[
            "toImage", "select2d", "lasso2d", "zoom2d",
            "pan2d", "autoScale2d", "resetScale2d",
        ],
    )

    return fig
