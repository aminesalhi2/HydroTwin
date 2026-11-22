"""Custom Plotly template and chart helpers for HydroTwin — calm precision palette.

Design Tokens:
- Indigo ink: #0B1528
- Off-white canvas: #F8F9FA
- Water-teal: #0D9488
- Vermilion: #E11D48
- Amber: #D97706
- Neutral greys: #64748B, #94A3B8, #CBD5E1, #E2E8F0
"""

from typing import Optional
import plotly.graph_objects as go
import plotly.io as pio

HYDROTWIN_COLORS = {
    'ink': '#0B1528',
    'canvas': '#F8F9FA',
    'teal': '#0D9488',
    'teal_light': '#CCFBF1',
    'vermilion': '#E11D48',
    'vermilion_light': '#FFE4E6',
    'amber': '#D97706',
    'amber_light': '#FEF3C7',
    'grey_dark': '#334155',
    'grey_mid': '#64748B',
    'grey_light': '#94A3B8',
    'hairline': '#E2E8F0',
    # Map & pipe specifics
    'pipe_normal': '#94A3B8',
    'pipe_suspect_1': '#E11D48',
    'pipe_suspect_2': '#D97706',
    'pipe_suspect_3': '#F59E0B',
    # Legacy aliases to maintain full backwards-compatibility
    'navy': '#0B1528',
    'ocean': '#0D9488',
    'aqua': '#0D9488',
    'sand': '#F8F9FA',
    'green': '#0D9488',
}

# Perceptually uniform smooth scale: Teal -> Amber -> Vermilion
PRESSURE_COLORSCALE = [
    [0.0, '#0D9488'],   # Nominal / Low pressure — calm teal
    [0.5, '#D97706'],   # Elevated — warm amber
    [1.0, '#E11D48'],   # Very high stress — vermilion
]


def get_hydrotwin_template() -> go.layout.Template:
    """Create a high-polish, restrained Plotly template with 2px lines, dotted horizontal grid, and no outer box."""
    template = go.layout.Template()
    template.layout.font = dict(
        family='Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        color='#0B1528',
        size=12,
    )
    template.layout.paper_bgcolor = 'rgba(0,0,0,0)'
    template.layout.plot_bgcolor = 'rgba(0,0,0,0)'
    template.layout.colorway = [
        '#0D9488',  # Primary water teal
        '#0B1528',  # Deep indigo ink
        '#64748B',  # Neutral slate
        '#D97706',  # Amber
        '#E11D48',  # Vermilion alert
        '#2563EB',  # Secondary blue
    ]
    template.layout.xaxis = dict(
        gridcolor='#E2E8F0',
        griddash='dot',
        gridwidth=1,
        showline=False,
        zeroline=False,
        tickfont=dict(size=11, color='#64748B', family='Inter, sans-serif'),
        title_font=dict(size=12, color='#0B1528'),
    )
    template.layout.yaxis = dict(
        gridcolor='#E2E8F0',
        griddash='dot',
        gridwidth=1,
        showline=False,
        zeroline=False,
        tickfont=dict(size=11, color='#64748B', family='Inter, sans-serif'),
        title_font=dict(size=12, color='#0B1528'),
    )
    template.layout.legend = dict(
        bgcolor='rgba(255, 255, 255, 0.92)',
        bordercolor='#E2E8F0',
        borderwidth=1,
        font=dict(size=11, color='#0B1528'),
        orientation='h',
        yanchor='bottom',
        y=-0.22,
        xanchor='center',
        x=0.5,
    )
    template.layout.margin = dict(l=24, r=24, t=40, b=28)
    template.layout.hoverlabel = dict(
        bgcolor='#0B1528',
        bordercolor='#1E293B',
        font=dict(color='#FFFFFF', size=11, family='JetBrains Mono, SF Mono, Consolas, monospace'),
    )
    template.layout.title = dict(
        font=dict(size=13, color='#0B1528', family='Inter, sans-serif', weight=600),
        x=0.0,
        xanchor='left',
        pad=dict(l=0, b=8),
    )
    return template


def register_template() -> None:
    """Register the HydroTwin template as Plotly's default."""
    pio.templates['hydrotwin'] = get_hydrotwin_template()
    pio.templates.default = 'plotly_white+hydrotwin'


# ─────────────────────────────────────────────────────────────
# Helper functions for standard chart annotations
# ─────────────────────────────────────────────────────────────

def add_event_vrect(
    fig: go.Figure,
    x0: float,
    x1: float,
    label: str,
    color: str = 'vermilion',
    opacity: float = 0.08,
) -> None:
    """Add a quiet shaded vertical event band (e.g. outage or off-peak tariff)."""
    hex_col = HYDROTWIN_COLORS.get(color, '#E11D48')
    fig.add_vrect(
        x0=x0,
        x1=x1,
        fillcolor=hex_col,
        opacity=opacity,
        line=dict(color=hex_col, width=1, dash='dot'),
        annotation_text=label,
        annotation_position='top left',
        annotation_font=dict(size=10, color=hex_col, family='Inter, sans-serif'),
    )


def add_threshold_line(
    fig: go.Figure,
    y_val: float = 15.0,
    label: str = 'Min Service Head (15m)',
    color: str = '#94A3B8',
) -> None:
    """Add a quiet horizontal reference line for minimum service head or physical limit."""
    fig.add_hline(
        y=y_val,
        line=dict(color=color, width=1.2, dash='dot'),
        annotation_text=label,
        annotation_position='bottom right',
        annotation_font=dict(size=10, color=color, family='Inter, sans-serif'),
    )


def add_shaded_saving_band(
    fig: go.Figure,
    x: list,
    y_baseline: list,
    y_optimized: list,
    label: str = 'Pumping Energy Saved',
) -> None:
    """Highlight the area between baseline and optimized curves with water-teal shading."""
    fig.add_trace(go.Scatter(
        x=x,
        y=y_baseline,
        mode='lines',
        name='Default Schedule',
        line=dict(color='#64748B', width=2, dash='dot'),
        hoverinfo='skip',
    ))
    fig.add_trace(go.Scatter(
        x=x,
        y=y_optimized,
        mode='lines',
        name='Optimized Duty',
        fill='tonexty',
        fillcolor='rgba(13, 148, 136, 0.12)',
        line=dict(color='#0D9488', width=2.2),
        hoverinfo='skip',
    ))
