"""Scenario report generation in HTML format for operator export."""

from datetime import datetime
from typing import Dict, List, Any
import config
from app.multilingual import TEMPLATES

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
    """Generate a clean, printable HTML audit report of a hydraulic scenario."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    t = TEMPLATES.get(lang, TEMPLATES["en"])
    is_rtl = (lang == "ar")
    
    rows_html = ""
    for s in suspect_pipes[:5]:
        rows_html += f"""
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: center;"><b>#{s['rank']}</b></td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">Pipe {s['pipe_id']}</td>
            <td style="padding: 8px; border: 1px solid #ddd;">{s.get('district', district)}</td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: center;"><b>{s['probability_pct']}%</b></td>
            <td style="padding: 8px; border: 1px solid #ddd;">{s.get('recommendation', 'Inspect first')}</td>
        </tr>
        """
        
    html = f"""
    <!DOCTYPE html>
    <html lang="{lang}" dir="{'rtl' if is_rtl else 'ltr'}">
    <head>
        <meta charset="utf-8">
        <title>HydroTwin Operational Scenario Report</title>
        <style>
            /* HydroTwin Report — calm precision palette */
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
                line-height: 1.6;
                color: var(--navy);
                margin: 30px;
                background-color: var(--sand);
            }}
            .banner {{
                background-color: #FEF0F0;
                border-left: 6px solid var(--vermilion);
                color: var(--vermilion);
                padding: 12px 16px;
                border-radius: 8px;
                font-size: 0.85rem;
                margin-bottom: 20px;
                font-weight: 700;
            }}
            .header {{
                border-bottom: 3px solid var(--ocean);
                padding-bottom: 12px;
                margin-bottom: 24px;
            }}
            .metric-box {{
                display: inline-block;
                width: 22%;
                margin: 1%;
                padding: 14px;
                border: 1px solid var(--border);
                border-top: 4px solid var(--ocean);
                background-color: #FFFFFF;
                border-radius: 12px;
                box-sizing: border-box;
                text-align: center;
                box-shadow: 0 2px 8px rgba(11,31,58,0.06);
            }}
            .metric-val {{
                font-size: 1.5rem;
                font-weight: 700;
                color: var(--ocean);
                font-variant-numeric: tabular-nums;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 16px;
                margin-bottom: 24px;
                background: #FFFFFF;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 1px 6px rgba(11,31,58,0.06);
            }}
            th {{
                background-color: var(--navy);
                color: #FFFFFF;
                padding: 10px 12px;
                border: none;
                text-align: {'right' if is_rtl else 'left'};
                font-size: 0.82rem;
                letter-spacing: 0.04em;
                text-transform: uppercase;
            }}
            td {{
                border-bottom: 1px solid var(--border);
                padding: 9px 12px;
                font-size: 0.88rem;
            }}
            tr:last-child td {{ border-bottom: none; }}
            tr:hover td {{ background-color: #F8FAFD; }}
            .footer {{
                margin-top: 30px;
                border-top: 2px solid var(--border);
                padding-top: 12px;
                font-size: 0.8rem;
                color: var(--text-secondary);
            }}
        </style>
    </head>
    <body>
        <div class="banner">
            ⚠️ {config.DISCLAIMER_BANNER}
        </div>
        
        <div class="header">
            <h2 style="margin: 0; color: #1a5276;">💧 HydroTwin Digital Water Twin — Official Advisory Audit</h2>
            <div style="font-size: 0.9rem; color: #7f8c8d; margin-top: 4px;">
                Scenario: <b>{scenario_title}</b> | Generated at: {now_str} | Language: {lang.upper()}
            </div>
        </div>
        
        <div style="margin-bottom: 20px;">
            <div class="metric-box">
                <div style="font-size: 0.8rem; color: #666;">Water Loss (Sim.)</div>
                <div class="metric-val">{water_loss_m3:,.0f} m³</div>
            </div>
            <div class="metric-box">
                <div style="font-size: 0.8rem; color: #666;">Electricity Saved</div>
                <div class="metric-val">{kwh_saved:,.1f} kWh</div>
            </div>
            <div class="metric-box">
                <div style="font-size: 0.8rem; color: #666;">Tariff Saved</div>
                <div class="metric-val">{cost_saved_tnd:.2f} TND</div>
            </div>
            <div class="metric-box">
                <div style="font-size: 0.8rem; color: #666;">Severity Level</div>
                <div class="metric-val" style="color: #c0392b;">{severity.upper()}</div>
            </div>
        </div>
        
        <h3>📋 Multilingual Advisory Work Order</h3>
        {work_order_html}
        
        <h3>🔍 Ranked Suspect Pipe Manifest</h3>
        <table>
            <thead>
                <tr>
                    <th style="width: 10%; text-align: center;">Rank</th>
                    <th style="width: 15%; text-align: center;">Pipe Asset</th>
                    <th style="width: 25%;">District / Sector</th>
                    <th style="width: 15%; text-align: center;">Confidence</th>
                    <th style="width: 35%;">Recommended Action</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        
        <div class="footer">
            <b>Operational Guardrail:</b> {config.DECISION_RULE_TEXT}<br>
            HydroTwin Hackathon Edition — Japan ⇄ Tunisia Bilateral Water-Energy Digital Twin.
        </div>
    </body>
    </html>
    """
    return html
