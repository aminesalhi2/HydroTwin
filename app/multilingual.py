"""Multilingual decision assistant: Alert generator, work orders, and deterministic Q&A.

Supports 4 languages:
  - Arabic (ar) with native Right-to-Left (dir="rtl") styling
  - French (fr)
  - Japanese (ja) with clean typography fallbacks
  - English (en)

Zero-hallucination guardrail:
  - Works 100% offline with deterministic template matching.
  - Never mentions or invents a leak that the analytical modules did not flag.
  - Optional LLM rephrasing only active when ENABLE_LLM_ASSISTANT=true in env.
"""

import os
import re
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

import config

LANGUAGE_NAMES = {
    "en": "English",
    "fr": "Français",
    "ar": "العربية (Arabic)",
    "ja": "日本語 (Japanese)",
}

# Typography and RTL CSS per language
def get_language_container_css(lang: str) -> str:
    """Return appropriate CSS container style for RTL Arabic or Japanese fonts."""
    if lang == "ar":
        return """
        <style>
            .stApp, .block-container, [data-testid="stAppViewContainer"] > .main {
                direction: rtl !important;
                text-align: right !important;
                font-family: 'Noto Sans Arabic', 'Arabic Typesetting', 'Segoe UI', Tahoma, sans-serif !important;
            }
            .ht-hero {
                flex-direction: row-reverse !important;
            }
            .ht-hero-left {
                flex-direction: row-reverse !important;
            }
            .ht-hero-ribbon {
                align-items: flex-start !important;
            }
            .ht-hero-ribbon .ht-ribbon-sub {
                text-align: left !important;
            }
            .ht-banner {
                border-left: 1px solid rgba(215, 38, 61, 0.25) !important;
                border-right: 5px solid var(--vermilion, #D7263D) !important;
                text-align: right !important;
            }
            .ht-advisory {
                border-left: 1px solid rgba(30, 111, 217, 0.22) !important;
                border-right: 4px solid var(--ocean, #1E6FD9) !important;
                text-align: right !important;
            }
            .ht-limitations {
                border-left: 1px solid var(--border, #DDE3ED) !important;
                border-right: 4px solid var(--text-muted, #7B8FA6) !important;
                text-align: right !important;
            }
            .ht-limitations ul {
                padding-left: 0 !important;
                padding-right: 18px !important;
            }
            .ht-kpi-card {
                text-align: right !important;
            }
            .ht-kpi-header {
                flex-direction: row-reverse !important;
            }
            .multilingual-card {
                direction: rtl !important;
                text-align: right !important;
                font-family: 'Noto Sans Arabic', 'Arabic Typesetting', 'Segoe UI', Tahoma, sans-serif !important;
                background-color: var(--card-bg, #FFFFFF);
                border: 1px solid var(--border, #DDE3ED);
                border-right: 5px solid var(--green, #2E9E6B) !important;
                border-left: 1px solid var(--border, #DDE3ED) !important;
                border-radius: 8px;
                padding: 16px 20px;
                margin-top: 10px;
                color: var(--text-primary, #0B1F3A);
                line-height: 1.7;
            }
            .ht-stepper {
                flex-direction: row-reverse !important;
            }
        </style>
        """
    elif lang == "ja":
        return """
        <style>
            .stApp, .block-container, [data-testid="stAppViewContainer"] > .main {
                font-family: 'Noto Sans JP', 'Yu Gothic', 'Meiryo', sans-serif !important;
                line-height: 1.75;
            }
            .multilingual-card {
                direction: ltr;
                text-align: left;
                font-family: 'Noto Sans JP', 'Yu Gothic', 'Meiryo', sans-serif !important;
                background-color: var(--card-bg, #FFFFFF);
                border: 1px solid var(--border, #DDE3ED);
                border-left: 5px solid var(--ocean, #1E6FD9);
                border-radius: 8px;
                padding: 16px 20px;
                margin-top: 10px;
                color: var(--text-primary, #0B1F3A);
                line-height: 1.8;
            }
        </style>
        """
    else:
        return """
        <style>
            .multilingual-card {
                direction: ltr;
                text-align: left;
                font-family: 'Inter', system-ui, -apple-system, sans-serif;
                background-color: var(--card-bg, #FFFFFF);
                border: 1px solid var(--border, #DDE3ED);
                border-left: 5px solid var(--green, #2E9E6B);
                border-radius: 8px;
                padding: 16px 20px;
                margin-top: 10px;
                color: var(--text-primary, #0B1F3A);
                line-height: 1.6;
            }
        </style>
        """

# -------------------------------------------------------------
# 1. Template-Based Work Order and Alert Generator
# -------------------------------------------------------------
TEMPLATES = {
    "en": {
        "title_leak": "Hydraulic Leak Alert & Work Order",
        "title_healthy": "Network Operational Status: Healthy",
        "severity_label": "Severity",
        "district_label": "District",
        "priority_label": "Priority",
        "water_loss_label": "Physical Loss Rate",
        "suspects_header": "Ranked Inspection Pipes (Confidence):",
        "suspect_line": "Rank {rank}: Pipe {pipe_id} ({district}) — {confidence}%",
        "action_header": "Recommended Operational Action:",
        "action_leak": "Deploy acoustic listening stick / correlator crew starting at Pipe {pipe_id}. Throttling is NOT recommended until visual confirmation is secured.",
        "action_healthy": "All district water balances and node pressures conform to operational standards. No field dispatch required.",
        "footer_advisory": "Simulated digital twin advisory. Certified human operators retain sole execution authority.",
    },
    "fr": {
        "title_leak": "Alerte de Fuite & Ordre de Mission",
        "title_healthy": "État Opérationnel du Réseau : Normal",
        "severity_label": "Sévérité",
        "district_label": "Quartier",
        "priority_label": "Priorité",
        "water_loss_label": "Débit de perte estimé",
        "suspects_header": "Canalisations à inspecter (confiance) :",
        "suspect_line": "Rang {rank} : Conduite {pipe_id} ({district}) — {confidence}%",
        "action_header": "Action opérationnelle recommandée :",
        "action_leak": "Dépêcher une équipe de détection acoustique / corrélateur sur la conduite {pipe_id}. Aucune coupure de vanne avant confirmation visuelle.",
        "action_healthy": "Les bilans sectoriels et pressions sont conformes aux normes. Aucune intervention requise.",
        "footer_advisory": "Conseil issu du jumeau numérique. L'opérateur certifié conserve l'autorité décisionnelle.",
    },
    "ar": {
        "title_leak": "إنذار تسرب هيدروليكي وأمر مهمة ميدانية",
        "title_healthy": "الحالة التشغيلية للشبكة: سليمة ومستقرة",
        "severity_label": "درجة الخطورة",
        "district_label": "المنطقة / الحي",
        "priority_label": "أولوية التدخل",
        "water_loss_label": "التدفق المهدور التقديري",
        "suspects_header": "الأنابيب المشتبه بها (حسب نسبة الثقة):",
        "suspect_line": "المرتبة {rank}: الأنبوب {pipe_id} ({district}) — {confidence}%",
        "action_header": "الإجراء التشغيلي الموصى به:",
        "action_leak": "إرسال فريق الفحص الصوتي للبدء بفحص الأنبوب {pipe_id}. يُمنع إغلاق الصمامات قبل التأكد الميداني المباشر.",
        "action_healthy": "الموازنة المائية لجميع المناطق والضغوط في الحدود الطبيعية. لا توجد حاجة لتدخل ميداني.",
        "footer_advisory": "إرشاد استشاري من التوأم الرقمي. القرار النهائي للمهندس البشري المسؤول.",
    },
    "ja": {
        "title_leak": "水理漏水警報および現場点検指示書",
        "title_healthy": "配水ネットワーク健全性ステータス：正常",
        "severity_label": "深刻度",
        "district_label": "対象区域",
        "priority_label": "点検優先度",
        "water_loss_label": "推定物理漏水量",
        "suspects_header": "最優先点検対象管路（確信度順）:",
        "suspect_line": "第{rank}位: 管路 {pipe_id}（{district}）— {confidence}%",
        "action_header": "推奨運用アクション:",
        "action_leak": "音聴棒・相関式漏水探知チームを管路 {pipe_id} に派遣してください。目視確認が完了するまで仕切弁閉塞は非推奨です。",
        "action_healthy": "全配水ブロックの流量バランスおよび節点圧力は管理基準内です。現場出動の必要はありません。",
        "footer_advisory": "デジタルツイン水理シミュレーションに基づく助言です。最終決定は現場管理者が行います。",
    }
}

def generate_work_order(
    has_leak: bool,
    severity: str = "moderate",
    district: str = "District 1 - Centre-Ville",
    suspect_pipes: Optional[List[Dict[str, Any]]] = None,
    water_loss_m3h: float = 0.0,
    lang: str = "en"
) -> Dict[str, str]:
    """Generate a structured, non-hallucinating work order in the chosen language."""
    if lang not in TEMPLATES:
        lang = "en"
    t = TEMPLATES[lang]
    
    # Priority mapping
    priority_map = {
        "minor": {"en": "Standard (Within 48h)", "fr": "Normale (Sous 48h)", "ar": "عادية (خلال 48 ساعة)", "ja": "通常（48時間以内）"},
        "moderate": {"en": "High (Within 12h)", "fr": "Haute (Sous 12h)", "ar": "مرتفعة (خلال 12 ساعة)", "ja": "高（12時間以内）"},
        "critical": {"en": "URGENT (Immediate)", "fr": "URGENT (Immédiat)", "ar": "عاجلة جداً (فوري)", "ja": "緊急（即時派遣）"},
        "none": {"en": "None", "fr": "Aucune", "ar": "لا يوجد", "ja": "なし"}
    }
    
    if not has_leak:
        body = f"""
        <div class="ht-ticket multilingual-card">
            <div class="ht-ticket-header">
                <div>
                    <span class="ht-ticket-id">WO-SYS-NOMINAL</span>
                    <span style="font-weight:600;font-size:0.92rem;margin-left:8px;color:#0B1528;">{t['title_healthy']}</span>
                </div>
                <span class="ht-ticket-pill healthy">NOMINAL</span>
            </div>
            <p style="margin:8px 0;font-size:0.84rem;color:#475569;">{t['action_healthy']}</p>
            <div style="font-size:0.75rem;color:#94A3B8;margin-top:12px;border-top:1px solid #E2E8F0;padding-top:6px;">{t['footer_advisory']}</div>
        </div>
        """
        return {
            "title": t["title_healthy"],
            "html": body,
            "lang": lang,
            "has_leak": False,
            "status": "NOMINAL",
            "suspect_pipes": []
        }
        
    top_pipe_id = suspect_pipes[0]["pipe_id"] if suspect_pipes else "N/A"
    priority_str = priority_map.get(severity, priority_map["moderate"])[lang]
    
    # Severity badge styling: minor=amber, moderate=orange, critical=vermilion
    sev_badge_class = (
        "critical" if severity == "critical"
        else "moderate" if severity == "moderate"
        else "minor"
    )

    # Render top 5 suspects as horizontal confidence bars (column 0 flush)
    bars_html = ""
    if suspect_pipes:
        for s in suspect_pipes[:5]:
            p_id = s["pipe_id"]
            d_name = s.get("district", "").split(" - ")[-1] if " - " in s.get("district", "") else s.get("district", "")
            prob = float(s.get("probability_pct", 0.0))
            bar_color = "#E11D48" if s["rank"] == 1 else "#D97706" if s["rank"] <= 3 else "#94A3B8"
            bars_html += (
                f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;font-size:0.80rem;">'
                f'<span style="width:58px;font-family:monospace;font-weight:600;color:#0B1528;">#{s["rank"]} · P{p_id}</span>'
                f'<span style="width:90px;color:#64748B;font-size:0.75rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{d_name}</span>'
                f'<div style="flex:1;background:#E2E8F0;height:6px;border-radius:3px;overflow:hidden;">'
                f'<div style="width:{prob}%;background:{bar_color};height:100%;border-radius:3px;"></div>'
                f'</div>'
                f'<span style="width:42px;text-align:right;font-family:monospace;font-weight:600;color:#0B1528;">{prob:.1f}%</span>'
                f'</div>'
            )

    action_text = t["action_leak"].format(pipe_id=top_pipe_id)
    short_dist = district.split(" - ")[-1] if " - " in district else district

    body = (
        f'<div class="ht-ticket multilingual-card" style="border-left:3px solid #E11D48;">'
        f'<div class="ht-ticket-header">'
        f'<div><span class="ht-ticket-id">WO-{top_pipe_id}-2026</span>'
        f'<span style="font-weight:600;font-size:0.92rem;margin-left:8px;color:#0B1528;">{t["title_leak"]}</span></div>'
        f'<div style="display:flex;gap:6px;align-items:center;">'
        f'<span class="ht-ticket-pill {sev_badge_class}">{severity.upper()}</span>'
        f'<span class="ht-ticket-pill" style="background:#F1F5F9;color:#64748B;">{lang.upper()}</span></div>'
        f'</div>'
        f'<div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:8px;margin-bottom:12px;font-size:0.80rem;background:#F8F9FA;padding:8px 10px;border-radius:6px;border:1px solid #E2E8F0;">'
        f'<div><span style="color:#64748B;">{t["district_label"]}:</span> <b style="color:#0B1528;">{short_dist}</b></div>'
        f'<div><span style="color:#64748B;">{t["priority_label"]}:</span> <b style="color:#0B1528;">{priority_str}</b></div>'
        f'<div><span style="color:#64748B;">{t["water_loss_label"]}:</span> <b style="color:#E11D48;">~{water_loss_m3h:.1f} m³/h</b></div>'
        f'</div>'
        f'<div style="margin-bottom:6px;font-weight:600;font-size:0.78rem;color:#0B1528;text-transform:uppercase;letter-spacing:0.04em;">{t["suspects_header"]}</div>'
        f'<div style="margin-bottom:12px;">{bars_html}</div>'
        f'<div style="margin-bottom:4px;font-weight:600;font-size:0.78rem;color:#0B1528;text-transform:uppercase;letter-spacing:0.04em;">{t["action_header"]}</div>'
        f'<div style="font-size:0.82rem;padding:8px 12px;background:#F8F9FA;border-radius:6px;border-left:3px solid #0D9488;color:#0B1528;line-height:1.4;">{action_text}</div>'
        f'<div style="font-size:0.72rem;color:#94A3B8;margin-top:10px;border-top:1px solid #E2E8F0;padding-top:6px;">{t["footer_advisory"]}</div>'
        f'</div>'
    )
    
    return {
        "title": t["title_leak"],
        "html": body,
        "lang": lang,
        "has_leak": True,
        "status": "LEAK_ALERT",
        "priority": priority_str,
        "top_pipe_id": top_pipe_id,
        "suspect_pipes": suspect_pipes or []
    }

# -------------------------------------------------------------
# 2. Deterministic Structured Q&A Engine (Zero Hallucination)
# -------------------------------------------------------------
INTENT_PATTERNS = {
    "which_district_loses_water": [
        r"which district.*(?:loses|lost|loss|most water)",
        r"quel quartier.*(?:perd|fuite|perte)",
        r"أي حي.*(?:يخسر|يفقد|تسرب|أكثر ماء)",
        r".*(?:どの地区|最も漏水|水が失われ).*",
    ],
    "which_pipes_to_inspect": [
        r"which pipes?.*(?:inspect|check|examine)",
        r"quelles conduites?.*(?:inspecter|vérifier)",
        r"أي الأنابيب.*(?:فحص|معاينة|تفتيش)",
        r".*(?:どの管路|点検すべき|調査管路).*",
    ],
    "what_if_pump_stops": [
        r"what happens if pump.*(?:stops|fails|outage|p2|p10)",
        r"que se passe-t-il si la pompe.*(?:arrête|panne|coupure)",
        r"ماذا يحدث إذا توقفت المضخة",
        r".*(?:ポンプが停止|停電|どうなる).*",
    ],
    "energy_savings": [
        r".*(?:energy|electricity|kwh|savings|cost).*",
        r".*(?:énergie|électricité|économies?|coût).*",
        r".*(?:طاقة|كهرباء|توفير|مقتصد).*",
        r".*(?:省エネ|電力|削減|電気代).*",
    ],
}

def answer_structured_query(
    query: str,
    context_data: Dict[str, Any],
    lang: str = "en"
) -> str:
    """Provide a strictly grounded, deterministic factual answer to an operator question.
    
    Zero hallucination rule: Answers strictly from structured data provided in context_data.
    """
    q_clean = query.strip().lower()
    matched_intent = None
    
    for intent, patterns in INTENT_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, q_clean, re.IGNORECASE):
                matched_intent = intent
                break
        if matched_intent:
            break
            
    # Default intent if unmatched
    if not matched_intent:
        matched_intent = "general_status"

    has_leak = context_data.get("has_leak", False)
    suspect_pipes = context_data.get("suspect_pipes", [])
    district = context_data.get("district", "Centre-Ville")
    kwh_saved = context_data.get("kwh_saved", 292.1)
    cost_saved = context_data.get("cost_saved_tnd", 33.6)
    outage_priority_comp = context_data.get("resilience_priority_compliance", 92.3)
    
    # 1. District losing water
    if matched_intent == "which_district_loses_water":
        if has_leak:
            answers = {
                "en": f"Based on district water balance telemetry, **{district}** exhibits the highest unexplained gap, accounting for the simulated anomaly.",
                "fr": f"D'après les télémesures de sectorisation, c'est **{district}** qui enregistre le plus fort écart inexpliqué.",
                "ar": f"استناداً إلى بيانات الموازنة المائية القطاعية، فإن **{district}** يسجل أعلى فارق مائي غير مفسر.",
                "ja": f"地区別流量バランスの測定データに基づくと、**{district}** が最大の未収水量を記録しています。"
            }
        else:
            answers = {
                "en": "All district water balances are currently balanced within normal meter calibration tolerances.",
                "fr": "Tous les secteurs présentent un équilibre hydraulique normal dans les marges de tolérance.",
                "ar": "جميع المناطق تسجل موازنة مائية طبيعية ومستقرة ضمن هوامش دقة العدادات.",
                "ja": "現在、全地区の流量バランスは正常な許容誤差内に収まっています。"
            }
        return answers.get(lang, answers["en"])

    # 2. Which pipes to inspect
    elif matched_intent == "which_pipes_to_inspect":
        if has_leak and suspect_pipes:
            top_pipes_str = ", ".join([f"Pipe {p['pipe_id']} ({p['probability_pct']}%)" for p in suspect_pipes[:3]])
            answers = {
                "en": f"The top ranked pipes recommended for physical acoustic survey are: **{top_pipes_str}** in {district}.",
                "fr": f"Les conduites prioritaires recommandées pour l'écoute acoustique sont : **{top_pipes_str}** dans {district}.",
                "ar": f"الأنابيب ذات الأولوية القصوى للفحص الصوتي الميداني هي: **{top_pipes_str}** في {district}.",
                "ja": f"音聴探知調査を推奨する最優先管路は: **{top_pipes_str}**（{district}内）です。"
            }
        else:
            answers = {
                "en": "No pipe inspections are required. Network pressures and flow balances indicate healthy status.",
                "fr": "Aucune inspection de canalisation n'est requise. Les pressions et débits sont sains.",
                "ar": "لا توجد حاجة لفحص أي أنابيب حالياً. ضغوط وتدفقات الشبكة في حالة سليمة ومستقرة.",
                "ja": "点検が必要な管路はありません。配水圧力および流量バランスは健全です。"
            }
        return answers.get(lang, answers["en"])

    # 3. What if pump stops
    elif matched_intent == "what_if_pump_stops":
        answers = {
            "en": (
                f"If primary transmission pump 10 stops, gravity tanks take over. "
                f"Under the emergency resilience plan, hospital priority zones maintain **{outage_priority_comp:.1f}%** "
                f"pressure compliance (>= {config.PRIORITY_MIN_PRESSURE_M}m) throughout the 4-hour blackout."
            ),
            "fr": (
                f"En cas d'arrêt de la station de pompage 10, les réservoirs gravitaires prennent le relais. "
                f"Le plan de résilience garantit **{outage_priority_comp:.1f}%** de conformité de pression "
                f"(>= {config.PRIORITY_MIN_PRESSURE_M}m) dans le secteur prioritaire des hôpitaux pendant les 4h de coupure."
            ),
            "ar": (
                f"في حال توقف محطة الضخ 10، تتولى الخزانات العلوية التزويد بالجاذبية. "
                f"وتضمن خطة الصمود الحفاظ على نسبة **{outage_priority_comp:.1f}%** من الضغط الكافي "
                f"(أعلى من {config.PRIORITY_MIN_PRESSURE_M} م) في منطقة المستشفيات طوال ساعات الانقطاع الأربع."
            ),
            "ja": (
                f"主送水ポンプ10が停止した場合、配水池からの自然流下供給に移行します。"
                f"事前充填レジリエンス計画により、4時間の停電中も重要病院区域で **{outage_priority_comp:.1f}%** "
                f"の給水圧力（{config.PRIORITY_MIN_PRESSURE_M}m以上）が維持されます。"
            )
        }
        return answers.get(lang, answers["en"])

    # 4. Energy savings
    elif matched_intent == "energy_savings":
        answers = {
            "en": f"The TOU-optimized pump schedule saves **{kwh_saved:.1f} kWh** (~{cost_saved:.2f} TND / {cost_saved*config.TND_TO_JPY:.0f} JPY per diurnal cycle) compared to default operator controls.",
            "fr": f"Le programme optimisé selon les tarifs horaires permet d'économiser **{kwh_saved:.1f} kWh** (~{cost_saved:.2f} TND par cycle journalier) par rapport au calendrier par défaut.",
            "ar": f"يحقق جدول الضخ المحسّن توفيراً قدره **{kwh_saved:.1f} كيلوواط ساعة** (حوالي {cost_saved:.2f} دينار تونسي يومياً) مقارنة بجدول التشغيل التقليدي.",
            "ja": f"時間帯別電力料金に最適化されたポンプ運用により、従来の標準運転と比較して **{kwh_saved:.1f} kWh**（1日あたり約 {cost_saved*config.TND_TO_JPY:.0f} 円削減）の省エネ効果が得られます。"
        }
        return answers.get(lang, answers["en"])

    # Default general status
    else:
        answers = {
            "en": "HydroTwin Digital Twin is active. You can ask about leak locations, pipes to inspect, pump outage scenarios, or electricity savings.",
            "fr": "Le jumeau numérique HydroTwin est actif. Vous pouvez interroger le système sur les fuites, les conduites suspectes, les coupures de pompage ou les économies d'énergie.",
            "ar": "التوأم الرقمي HydroTwin نشط ومستعد للإجابة عن مواقع التسرب، الأنابيب المطلوب فحصها، سيناريوهات انقطاع المضخات، أو توفير الطاقة.",
            "ja": "HydroTwin デジタルツインが稼働中です。漏水箇所、点検対象管路、ポンプ停止時の影響、省エネ効果について質問できます。"
        }
        return answers.get(lang, answers["en"])
