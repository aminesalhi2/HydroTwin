"""Scenario report generation in HTML format for operator export."""

from datetime import datetime
from typing import Dict, List, Any
import config
from app.multilingual import TEMPLATES

_REPORT_LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 76" width="36" height="42" fill="none">
  <defs>
    <linearGradient id="repGrad" x1="32" y1="2" x2="32" y2="74" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#2FD3C9"/>
      <stop offset="100%" stop-color="#1E6FD9"/>
    </linearGradient>
  </defs>
  <path d="M32 3 C32 3 10 32 10 50 C10 63 19.8 73 32 73 C44.2 73 54 63 54 50 C54 32 32 3 32 3 Z" fill="url(#repGrad)" stroke="#1E6FD9" stroke-width="1.8"/>
  <circle cx="32" cy="36" r="4.5" fill="#2FD3C9" stroke="#FFFFFF" stroke-width="1.5"/>
  <circle cx="22" cy="54" r="4" fill="#1E6FD9" stroke="#FFFFFF" stroke-width="1.5"/>
  <circle cx="42" cy="54" r="4" fill="#FFFFFF" stroke="#2FD3C9" stroke-width="1.5"/>
  <line x1="32" y1="36" x2="22" y2="54" stroke="#FFFFFF" stroke-width="1.8"/>
  <line x1="32" y1="36" x2="42" y2="54" stroke="#FFFFFF" stroke-width="1.8"/>
  <line x1="22" y1="54" x2="42" y2="54" stroke="#2FD3C9" stroke-width="1.8"/>
</svg>"""

def generate_scenario_report_html(
    scenario_title: str,
    district: str,
    severity: str,
    water_loss_m3: float,
    kwh_saved: float,
    cost_saved_tnd: float,
    suspect_pipes: List[Dict[str, Any]],
    work_order_html: str,
    lang: str = "en"
) -> str:
    """Generate a clean, printable A4 HTML audit report of a hydraulic scenario."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    is_rtl = (lang == "ar")
    sev_upper = severity.upper()
    sev_color = "#D7263D" if severity == "critical" else "#E86420" if severity == "moderate" else "#E8A020"
    
    rows_html = ""
    for s in suspect_pipes[:5]:
        rows_html += f"""
        <tr>
            <td style="padding: 9px 12px; border-bottom: 1px solid #DDE3ED; text-align: center;"><b>#{s['rank']}</b></td>
            <td style="padding: 9px 12px; border-bottom: 1px solid #DDE3ED; text-align: center;">Pipe {s['pipe_id']}</td>
            <td style="padding: 9px 12px; border-bottom: 1px solid #DDE3ED;">{s.get('district', district)}</td>
            <td style="padding: 9px 12px; border-bottom: 1px solid #DDE3ED; text-align: center; color: #1E6FD9; font-weight: 700;">{s['probability_pct']}%</td>
            <td style="padding: 9px 12px; border-bottom: 1px solid #DDE3ED;">{s.get('recommendation', 'Inspect first')}</td>
        </tr>
        """
        
    html = f"""<!DOCTYPE html>
<html lang="{lang}" dir="{'rtl' if is_rtl else 'ltr'}">
<head>
    <meta charset="utf-8">
    <title>HydroTwin Operational Scenario Audit Report — {scenario_title}</title>
    <style>
        @page {{
            size: A4 portrait;
            margin: 15mm 18mm 20mm 18mm;
            @bottom-right {{
                content: "Page 1 of 1";
                font-size: 8pt;
                color: #7B8FA6;
            }}
        }}
        :root {{
            --navy: #0B1F3A;
            --ocean: #1E6FD9;
            --aqua: #2FD3C9;
            --sand: #F4EFE6;
            --vermilion: #D7263D;
            --green: #2E9E6B;
            --amber: #E8A020;
            --border: #DDE3ED;
            --text-secondary: #4A6080;
        }}
        body {{
            font-family: {'Segoe UI, Tahoma, Arial, sans-serif' if is_rtl else 'Inter, system-ui, -apple-system, sans-serif'};
            line-height: 1.5;
            color: #0B1F3A;
            margin: 0;
            padding: 24px;
            background-color: #FFFFFF;
            font-size: 10pt;
        }}
        .report-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 2.5px solid #0B1F3A;
            padding-bottom: 14px;
            margin-bottom: 18px;
        }}
        .report-title {{
            font-size: 16pt;
            font-weight: 700;
            color: #0B1F3A;
            letter-spacing: -0.02em;
            margin: 0;
        }}
        .report-subtitle {{
            font-size: 8.5pt;
            color: #4A6080;
            margin-top: 3px;
        }}
        .banner {{
            background-color: #FFF9F8;
            border: 1px solid rgba(215, 38, 61, 0.3);
            border-left: 5px solid var(--vermilion);
            color: var(--vermilion);
            padding: 10px 14px;
            border-radius: 6px;
            font-size: 8.5pt;
            margin-bottom: 18px;
            font-weight: 600;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-bottom: 20px;
        }}
        .metric-box {{
            padding: 12px;
            border: 1px solid #DDE3ED;
            border-top: 3px solid var(--ocean);
            background-color: #FAFCFE;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-label {{
            font-size: 8pt;
            color: #4A6080;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            font-weight: 600;
            margin-bottom: 4px;
        }}
        .metric-val {{
            font-size: 15pt;
            font-weight: 700;
            color: #0B1F3A;
            font-variant-numeric: tabular-nums;
        }}
        .section-title {{
            font-size: 11pt;
            font-weight: 700;
            color: #0B1F3A;
            margin-top: 18px;
            margin-bottom: 8px;
            border-bottom: 1px solid #EDF1F7;
            padding-bottom: 4px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 8px;
            margin-bottom: 18px;
            font-size: 9pt;
        }}
        th {{
            background-color: #0B1F3A;
            color: #FFFFFF;
            padding: 8px 12px;
            text-align: {'right' if is_rtl else 'left'};
            font-size: 8pt;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}
        tr:nth-child(even) td {{ background-color: #F8FAFD; }}
        .severity-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 8pt;
            font-weight: 700;
        }}
        .footer {{
            margin-top: 24px;
            border-top: 1px solid #DDE3ED;
            padding-top: 10px;
            font-size: 8pt;
            color: #7B8FA6;
            line-height: 1.5;
        }}
    </style>
</head>
<body>
    <div class="report-header">
        <div style="display:flex; align-items:center; gap:12px;">
            {_REPORT_LOGO_SVG}
            <div>
                <h1 class="report-title">HydroTwin · Official Advisory Incident Audit</h1>
                <div class="report-subtitle">
                    Japan ⇄ Tunisia Water + Energy Track · Hackathon 2026
                </div>
            </div>
        </div>
        <div style="text-align:{'left' if is_rtl else 'right'}; font-size:8pt; color:#4A6080;">
            <div><b>Generated:</b> {now_str}</div>
            <div><b>Language:</b> {lang.upper()} · Audit ID: HT-{datetime.now().strftime("%Y%m%d%H%M")}</div>
        </div>
    </div>

    <div class="banner">
        ⚠️ {config.HONESTY_BANNER_TEXT}
    </div>

    <div style="margin-bottom: 12px;">
        <span style="font-size:10pt;"><b>Scenario:</b> {scenario_title} &nbsp;|&nbsp; <b>Sector:</b> {district}</span>
    </div>

    <div class="metric-grid">
        <div class="metric-box">
            <div class="metric-label">Water Loss (Sim.)</div>
            <div class="metric-val">{water_loss_m3:,.0f} m³</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">Electricity Saved</div>
            <div class="metric-val" style="color: #2E9E6B;">{kwh_saved:,.1f} kWh</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">Financial Savings</div>
            <div class="metric-val" style="color: #1E6FD9;">{cost_saved_tnd:.2f} TND</div>
        </div>
        <div class="metric-box" style="border-top-color: {sev_color};">
            <div class="metric-label">Incident Severity</div>
            <div class="metric-val" style="color: {sev_color};">{sev_upper}</div>
        </div>
    </div>

    <div class="section-title">📋 Operational Work Order Dispatch</div>
    <div style="background:#FAFCFE; border:1px solid #DDE3ED; border-radius:8px; padding:12px; margin-bottom:16px;">
        {work_order_html}
    </div>

    <div class="section-title">🔍 Ranked Suspect Pipe Manifest (Confidence Order)</div>
    <table>
        <thead>
            <tr>
                <th style="width: 10%; text-align: center;">Rank</th>
                <th style="width: 18%; text-align: center;">Pipe Asset</th>
                <th style="width: 26%;">District / Zone</th>
                <th style="width: 16%; text-align: center;">Confidence</th>
                <th style="width: 30%;">Recommended Field Action</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>

    <div class="footer">
        <b>Operational Decision Guardrail:</b> {config.DECISION_RULE_TEXT}<br>
        <b>Honest Prototype Boundaries:</b> Synthetic Net3 benchmark topology (92 nodes, 117 pipes). Zero proprietary SCADA data from SONEDE/STEG. Certified human operators retain sole execution authority.
        <div style="margin-top:4px; text-align:{'left' if is_rtl else 'right'};">HydroTwin v1.0.0 · Page 1 of 1</div>
    </div>
</body>
</html>"""
    return html
