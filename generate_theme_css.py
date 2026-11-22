import os
import base64

def generate():
    here = os.path.dirname(os.path.abspath(__file__))
    font_dir = os.path.join(here, "app", "assets", "fonts")

    def b64(name):
        with open(os.path.join(font_dir, name), "rb") as f:
            return base64.b64encode(f.read()).decode("ascii")

    f_inter_reg = b64("Inter-Regular.woff2")
    f_inter_med = b64("Inter-Medium.woff2")
    f_inter_sem = b64("Inter-SemiBold.woff2")
    f_inter_bld = b64("Inter-Bold.woff2")
    f_arab_reg = b64("NotoSansArabic-Regular.woff2")
    f_arab_bld = b64("NotoSansArabic-Bold.woff2")
    f_jp_reg = b64("NotoSansJP-Regular.woff2")
    f_jp_bld = b64("NotoSansJP-Bold.woff2")

    css = f"""/* =================================================================
   HydroTwin — Calm Precision Design System
   Japanese Minimalism × Mediterranean Warmth
   100% Offline (all fonts local base64 woff2, zero external CDNs)
   ================================================================= */

/* ── FONT FACES ─────────────────────────────────────────────── */
@font-face {{
  font-family: 'Inter';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('data:font/woff2;base64,{f_inter_reg}') format('woff2'),
       local('Inter Regular'), local('Inter'), local('Segoe UI'), local('Arial');
}}
@font-face {{
  font-family: 'Inter';
  font-style: normal;
  font-weight: 500;
  font-display: swap;
  src: url('data:font/woff2;base64,{f_inter_med}') format('woff2'),
       local('Inter Medium'), local('Segoe UI Semibold');
}}
@font-face {{
  font-family: 'Inter';
  font-style: normal;
  font-weight: 600;
  font-display: swap;
  src: url('data:font/woff2;base64,{f_inter_sem}') format('woff2'),
       local('Inter SemiBold'), local('Segoe UI Semibold');
}}
@font-face {{
  font-family: 'Inter';
  font-style: normal;
  font-weight: 700;
  font-display: swap;
  src: url('data:font/woff2;base64,{f_inter_bld}') format('woff2'),
       local('Inter Bold'), local('Segoe UI Bold'), local('Arial Bold');
}}
@font-face {{
  font-family: 'Noto Sans Arabic';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('data:font/woff2;base64,{f_arab_reg}') format('woff2'),
       local('Noto Sans Arabic'), local('Arabic Typesetting'), local('Segoe UI'), local('Arial');
}}
@font-face {{
  font-family: 'Noto Sans Arabic';
  font-style: normal;
  font-weight: 700;
  font-display: swap;
  src: url('data:font/woff2;base64,{f_arab_bld}') format('woff2'),
       local('Noto Sans Arabic Bold'), local('Segoe UI Bold');
}}
@font-face {{
  font-family: 'Noto Sans JP';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('data:font/woff2;base64,{f_jp_reg}') format('woff2'),
       local('Noto Sans JP'), local('Yu Gothic'), local('Meiryo'), local('Hiragino Kaku Gothic ProN');
}}
@font-face {{
  font-family: 'Noto Sans JP';
  font-style: normal;
  font-weight: 700;
  font-display: swap;
  src: url('data:font/woff2;base64,{f_jp_bld}') format('woff2'),
       local('Noto Sans JP Bold'), local('Yu Gothic Bold'), local('Meiryo Bold');
}}

/* ── DESIGN TOKENS (CSS Variables) ─────────────────────────── */
:root {{
  /* Semantic Palette — Calm Precision */
  --ink:             #0B1528;
  --ink-surface:     #132238;
  --ink-border:      rgba(255, 255, 255, 0.10);
  
  --canvas:          #F8F9FA;
  --card:            #FFFFFF;
  --hairline:        #E2E8F0;
  --hairline-dark:   #CBD5E1;
  
  --teal:            #0D9488;
  --teal-hover:      #0F766E;
  --teal-light:      rgba(13, 148, 136, 0.08);
  --teal-border:     rgba(13, 148, 136, 0.25);
  
  --vermilion:       #E11D48;
  --vermilion-light: rgba(225, 29, 72, 0.08);
  --vermilion-border:rgba(225, 29, 72, 0.25);
  
  --green:           #059669;
  --green-light:     rgba(5, 150, 105, 0.08);
  --amber:           #D97706;
  --amber-light:     rgba(217, 119, 6, 0.08);

  /* Typography Colors */
  --text-primary:    #0F172A;
  --text-secondary:  #475569;
  --text-muted:      #94A3B8;

  /* Geometry & Elevation — Restrained, 1px Hairlines */
  --radius-sm:       6px;
  --radius-md:       8px;
  --radius-lg:       10px;
  --shadow-subtle:   0 1px 2px rgba(15, 23, 42, 0.04);
  --shadow-hover:    0 4px 12px rgba(15, 23, 42, 0.06);

  /* Fonts */
  --font-latin:      'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-arabic:     'Noto Sans Arabic', 'Arabic Typesetting', 'Segoe UI', Tahoma, sans-serif;
  --font-jp:         'Noto Sans JP', 'Yu Gothic', 'Meiryo', 'Hiragino Kaku Gothic ProN', sans-serif;
  --font-mono:       ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}}

/* ── GLOBAL RESETS & CANVAS ────────────────────────────────── */
body, .stApp {{
  font-family: var(--font-latin) !important;
  color: var(--text-primary) !important;
  background-color: var(--canvas) !important;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}}

.stApp header {{
  background: transparent !important;
}}

.block-container {{
  padding-top: 1rem !important;
  padding-bottom: 2.5rem !important;
  max-width: 1440px !important;
}}

/* Headings */
h1, h2, h3, h4, h5, h6 {{
  font-family: var(--font-latin) !important;
  color: var(--text-primary);
  font-weight: 600;
  letter-spacing: -0.02em;
  margin-top: 0.25rem;
  margin-bottom: 0.25rem;
}}

p, span, label {{
  font-family: var(--font-latin);
}}

/* Tabular figures for numbers everywhere */
.tabular, [data-testid="stMetricValue"] {{
  font-variant-numeric: tabular-nums !important;
  letter-spacing: -0.02em !important;
}}

/* ── REFINED HEADER (Flat, Clean, No Heavy Gradient) ───────── */
.ht-header-bar {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0 16px;
  border-bottom: 1px solid var(--hairline);
  margin-bottom: 16px;
  gap: 16px;
}}

.ht-header-left {{
  display: flex;
  align-items: center;
  gap: 14px;
}}

.ht-header-mark {{
  width: 32px;
  height: 38px;
  flex-shrink: 0;
}}

.ht-header-title {{
  font-size: 1.45rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.03em;
  line-height: 1.2;
}}

.ht-header-subtitle {{
  font-size: 0.82rem;
  color: var(--text-secondary);
  font-weight: 400;
  margin-top: 1px;
}}

.ht-header-right {{
  display: flex;
  align-items: center;
  gap: 10px;
}}

/* Slim Pill: Simulated Data · Advisory Only */
.ht-pill-advisory {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #FFFFFF;
  border: 1px solid var(--hairline);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.74rem;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}}

.ht-pill-advisory:hover {{
  border-color: var(--teal);
  color: var(--teal);
  box-shadow: var(--shadow-subtle);
}}

.ht-pill-dot {{
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--teal);
}}

.ht-ribbon-subtle {{
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 10px;
  border-radius: 6px;
  background: var(--teal-light);
  border: 1px solid var(--teal-border);
  color: var(--teal);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.02em;
}}

/* ── HORIZONTAL SCENARIO STEPPER ───────────────────────────── */
.ht-stepper-wrap {{
  display: flex;
  align-items: center;
  gap: 8px;
  background: #FFFFFF;
  border: 1px solid var(--hairline);
  border-radius: var(--radius-md);
  padding: 6px 10px;
  margin-bottom: 18px;
}}

.ht-step-tab {{
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  font-size: 0.80rem;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
  border: 1px solid transparent;
  user-select: none;
}}

.ht-step-tab:hover {{
  background: var(--teal-light);
  color: var(--teal);
}}

.ht-step-tab.active {{
  background: var(--teal-light);
  border-color: var(--teal);
  color: var(--teal);
  font-weight: 600;
}}

.ht-step-tab.active.outage {{
  background: var(--vermilion-light);
  border-color: var(--vermilion);
  color: var(--vermilion);
}}

.ht-step-badge {{
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--hairline);
  color: var(--text-secondary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.68rem;
  font-weight: 700;
}}

.ht-step-tab.active .ht-step-badge {{
  background: var(--teal);
  color: #FFFFFF;
}}

.ht-step-tab.active.outage .ht-step-badge {{
  background: var(--vermilion);
  color: #FFFFFF;
}}

/* ── REFINED KPI CARDS (Max 4, Restrained, No Truncation) ──── */
.ht-kpi-row {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}}

@media (max-width: 1100px) {{
  .ht-kpi-row {{
    grid-template-columns: repeat(2, 1fr);
  }}
}}

@media (max-width: 600px) {{
  .ht-kpi-row {{
    grid-template-columns: 1fr;
  }}
}}

.ht-kpi-box {{
  background: #FFFFFF;
  border: 1px solid var(--hairline);
  border-radius: var(--radius-md);
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 104px;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}}

.ht-kpi-box:hover {{
  border-color: var(--hairline-dark);
  box-shadow: var(--shadow-subtle);
}}

.ht-kpi-box.kpi-alert {{
  border-left: 3px solid var(--vermilion);
}}

.ht-kpi-box.kpi-healthy {{
  border-left: 3px solid var(--teal);
}}

.ht-kpi-meta {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}}

.ht-kpi-title {{
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
}}

.ht-kpi-main {{
  display: flex;
  align-items: baseline;
  gap: 5px;
}}

.ht-kpi-num {{
  font-size: 1.60rem;
  font-weight: 700;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
  line-height: 1.1;
  letter-spacing: -0.03em;
}}

.ht-kpi-box.kpi-alert .ht-kpi-num {{
  color: var(--vermilion);
}}

.ht-kpi-unit {{
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--text-muted);
}}

.ht-kpi-subtext {{
  font-size: 0.72rem;
  color: var(--text-muted);
  margin-top: 4px;
  line-height: 1.3;
}}

/* ── TICKET CARDS (Work Orders) ────────────────────────────── */
.ht-ticket {{
  background: #FFFFFF;
  border: 1px solid var(--hairline);
  border-radius: var(--radius-md);
  padding: 16px 18px;
  margin-bottom: 12px;
}}

.ht-ticket-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--hairline);
  margin-bottom: 12px;
}}

.ht-ticket-id {{
  font-family: var(--font-mono);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
}}

.ht-ticket-pill {{
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.70rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}}

.ht-ticket-pill.minor {{
  background: var(--amber-light);
  color: var(--amber);
}}

.ht-ticket-pill.moderate {{
  background: rgba(234, 88, 12, 0.08);
  color: #EA580C;
}}

.ht-ticket-pill.critical {{
  background: var(--vermilion-light);
  color: var(--vermilion);
}}

.ht-ticket-pill.healthy {{
  background: var(--green-light);
  color: var(--green);
}}

.ht-ticket-action {{
  background: var(--canvas);
  border: 1px solid var(--hairline);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  font-size: 0.80rem;
  color: var(--text-primary);
  margin-top: 10px;
}}

/* ── CONFIDENCE BARS ───────────────────────────────────────── */
.ht-bar-row {{
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  font-size: 0.76rem;
}}

.ht-bar-label {{
  width: 90px;
  flex-shrink: 0;
  font-weight: 500;
  color: var(--text-primary);
}}

.ht-bar-track {{
  flex: 1;
  height: 6px;
  background: var(--hairline);
  border-radius: 3px;
  overflow: hidden;
}}

.ht-bar-fill {{
  height: 100%;
  background: var(--teal);
  border-radius: 3px;
}}

.ht-bar-fill.alert {{
  background: var(--vermilion);
}}

.ht-bar-pct {{
  width: 44px;
  text-align: right;
  font-variant-numeric: tabular-nums;
  color: var(--text-secondary);
  font-weight: 600;
}}

/* ── SIDEBAR STYLING — DEEP INDIGO INK ─────────────────────── */
[data-testid="stSidebar"] {{
  background-color: var(--ink) !important;
  border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
}}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {{
  color: rgba(255, 255, 255, 0.88) !important;
  font-size: 0.80rem !important;
}}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{
  color: #FFFFFF !important;
}}

[data-testid="stSidebar"] hr {{
  border-color: rgba(255, 255, 255, 0.08) !important;
  margin: 0.8rem 0 !important;
}}

.ht-side-section {{
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--teal) !important;
  padding: 8px 0 3px;
}}

/* Sidebar Form Controls */
[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
  background-color: var(--ink-surface) !important;
  border: 1px solid var(--ink-border) !important;
  border-radius: var(--radius-sm) !important;
  color: #FFFFFF !important;
}}

[data-testid="stSidebar"] div[data-baseweb="select"] * {{
  color: #FFFFFF !important;
  background-color: transparent !important;
}}

div[data-baseweb="popover"] ul,
div[data-baseweb="menu"] {{
  background-color: var(--ink-surface) !important;
  border: 1px solid var(--ink-border) !important;
}}

div[data-baseweb="popover"] li,
div[data-baseweb="menu"] li {{
  color: #FFFFFF !important;
  background-color: var(--ink-surface) !important;
}}

div[data-baseweb="popover"] li:hover,
div[data-baseweb="menu"] li:hover {{
  background-color: var(--teal) !important;
  color: #FFFFFF !important;
}}

/* Sidebar Segmented Control / Button Group */
[data-testid="stSidebar"] [data-testid="stButtonGroup"] {{
  background-color: var(--ink-surface) !important;
  border: 1px solid var(--ink-border) !important;
  border-radius: var(--radius-sm) !important;
  padding: 2px !important;
}}

[data-testid="stSidebar"] button[data-testid="stBaseButton-segmented_control"] {{
  background-color: transparent !important;
  color: rgba(255, 255, 255, 0.70) !important;
  border: none !important;
  font-weight: 500 !important;
  font-size: 0.76rem !important;
}}

[data-testid="stSidebar"] button[data-testid="stBaseButton-segmented_control"]:hover {{
  color: #FFFFFF !important;
}}

[data-testid="stSidebar"] button[data-testid="stBaseButton-segmented_controlActive"] {{
  background-color: var(--teal) !important;
  color: #FFFFFF !important;
  font-weight: 600 !important;
  border: none !important;
  border-radius: 4px !important;
  font-size: 0.76rem !important;
}}

/* Sidebar Captions */
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
  color: rgba(255, 255, 255, 0.55) !important;
  font-size: 0.72rem !important;
  line-height: 1.35 !important;
}}

/* Sidebar Buttons */
[data-testid="stSidebar"] .stButton > button {{
  background-color: var(--teal) !important;
  color: #FFFFFF !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  font-weight: 600 !important;
  font-size: 0.78rem !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15) !important;
}}

[data-testid="stSidebar"] .stButton > button:hover {{
  background-color: var(--teal-hover) !important;
}}

/* ── TABS STYLING — CLEAN MINIMAL UNDERLINE ─────────────────── */
.stTabs [data-baseweb="tab-list"] {{
  gap: 16px !important;
  background-color: transparent !important;
  border-bottom: 1px solid var(--hairline) !important;
  padding-bottom: 0 !important;
  margin-bottom: 14px !important;
}}

.stTabs [data-baseweb="tab"] {{
  border-radius: 0 !important;
  padding: 8px 4px !important;
  font-weight: 500 !important;
  font-size: 0.84rem !important;
  color: var(--text-secondary) !important;
  background-color: transparent !important;
  border: none !important;
  border-bottom: 2px solid transparent !important;
}}

.stTabs [data-baseweb="tab"]:hover {{
  color: var(--text-primary) !important;
}}

.stTabs [aria-selected="true"] {{
  color: var(--teal) !important;
  border-bottom: 2px solid var(--teal) !important;
  font-weight: 600 !important;
}}

/* ── MULTILINGUAL RTL & TYPOGRAPHY ─────────────────────────── */
[lang="ar"], [dir="rtl"] {{
  direction: rtl !important;
  text-align: right !important;
  font-family: var(--font-arabic) !important;
}}

[lang="ar"] .ht-kpi-main {{
  flex-direction: row-reverse;
}}

[lang="ja"] {{
  font-family: var(--font-jp) !important;
}}

/* ── FOOTER ────────────────────────────────────────────────── */
.ht-footer {{
  margin-top: 36px;
  padding: 16px 0;
  border-top: 1px solid var(--hairline);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 0.72rem;
  color: var(--text-muted);
}}
"""

    out_path = os.path.join(here, "app", "assets", "theme.css")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(css)
    print(f"Generated theme.css successfully ({len(css)} bytes)")

if __name__ == "__main__":
    generate()
