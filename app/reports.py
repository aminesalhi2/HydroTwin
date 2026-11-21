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
            body {{
                font-family: {'Segoe UI, Tahoma, Arial, sans-serif' if is_rtl else 'system-ui, -apple-system, sans-serif'};
                line-height: 1.5;
                color: #2c3e50;
                margin: 30px;
                background-color: #ffffff;
            }}
            .banner {{
                background-color: #fff3cd;
                border: 1px solid #ffeeba;
                color: #856404;
                padding: 12px;
                border-radius: 4px;
                font-size: 0.85rem;
                margin-bottom: 20px;
                font-weight: bold;
            }}
            .header {{
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}
            .metric-box {{
                display: inline-block;
                width: 22%;
                margin: 1%;
                padding: 12px;
                border: 1px solid #ecf0f1;
                background-color: #f8f9fa;
                border-radius: 6px;
                box-sizing: border-box;
                text-align: center;
            }}
            .metric-val {{
                font-size: 1.4rem;
                font-weight: bold;
                color: #2980b9;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 16px;
                margin-bottom: 24px;
            }}
            th {{
                background-color: #f2f4f8;
                padding: 10px;
                border: 1px solid #ddd;
                text-align: {'right' if is_rtl else 'left'};
            }}
            .footer {{
                margin-top: 30px;
                border-top: 1px solid #eee;
                padding-top: 10px;
                font-size: 0.8rem;
                color: #7f8c8d;
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
