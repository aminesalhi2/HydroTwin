"""Custom Plotly template for HydroTwin — calm precision palette."""

import plotly.graph_objects as go
import plotly.io as pio

HYDROTWIN_COLORS = {
    'navy': '#0B1F3A',
    'ocean': '#1E6FD9',
    'aqua': '#2FD3C9',
    'sand': '#F4EFE6',
    'vermilion': '#D7263D',
    'green': '#2E9E6B',
    'amber': '#E8A020',
    'pipe_normal': '#8FA8C8',
    'pipe_suspect_1': '#D7263D',
    'pipe_suspect_2': '#E8A020',
    'pipe_suspect_3': '#F4D03F',
}

PRESSURE_COLORSCALE = [
    [0.0, '#1E6FD9'],   # Low pressure — ocean blue
    [0.3, '#2FD3C9'],   # Normal — aqua
    [0.6, '#E8A020'],   # Elevated — amber
    [1.0, '#D7263D'],   # Very high — vermilion
]


def get_hydrotwin_template():
    template = go.layout.Template()
    template.layout.font = dict(family='Inter, system-ui, sans-serif', color='#0B1F3A', size=13)
    template.layout.paper_bgcolor = '#FFFFFF'
    template.layout.plot_bgcolor = '#F8FAFD'
    template.layout.colorway = [
        '#1E6FD9', '#2FD3C9', '#2E9E6B', '#E8A020', '#D7263D', '#8FA8C8', '#6C5CE7'
    ]
    template.layout.xaxis = dict(
        gridcolor='#DDE3ED', gridwidth=1, linecolor='#DDE3ED',
        tickfont=dict(size=11, color='#4A6080')
    )
    template.layout.yaxis = dict(
        gridcolor='#DDE3ED', gridwidth=1, linecolor='#DDE3ED',
        tickfont=dict(size=11, color='#4A6080')
    )
    template.layout.legend = dict(
        bgcolor='rgba(255,255,255,0.9)', bordercolor='#DDE3ED', borderwidth=1,
        font=dict(size=12), orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1
    )
    template.layout.margin = dict(l=16, r=16, t=48, b=16)
    template.layout.hoverlabel = dict(
        bgcolor='#0B1F3A', bordercolor='#1E6FD9', font=dict(color='#FFFFFF', size=12)
    )
    template.layout.title = dict(
        font=dict(size=15, color='#0B1F3A', family='Inter, sans-serif'),
        x=0.0, xanchor='left', pad=dict(l=4)
    )
    return template


def register_template():
    pio.templates['hydrotwin'] = get_hydrotwin_template()
    pio.templates.default = 'plotly_white+hydrotwin'
