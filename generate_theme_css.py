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
  /* Brand Palette */
  --navy:            #0B1F3A;
  --navy-light:      #152E52;
  --ocean:           #1E6FD9;
  --ocean-hover:     #1658B0;
  --aqua:            #2FD3C9;
  --aqua-dark:       #1EBAB0;
  --sand:            #F7F5F0;
  --sand-light:      #FAF8F3;
  --sand-dark:       #EDE7DC;
  --vermilion:       #D7263D;
  --vermilion-soft:  rgba(215, 38, 61, 0.08);
  --green:           #2E9E6B;
  --green-soft:      rgba(46, 158, 107, 0.08);
  --amber:           #E8A020;
  --amber-soft:      rgba(232, 160, 32, 0.08);
  --white:           #FFFFFF;

  /* Surfaces & Text */
  --bg-page:         var(--sand);
  --card-bg:         #FFFFFF;
  --text-primary:    #0B1F3A;
  --text-secondary:  #4A6080;
  --text-muted:      #7B8FA6;
  --border:          #DDE3ED;
  --border-subtle:   #EDF1F7;

  /* Elevations & Geometry */
  --shadow-sm:       0 1px 3px rgba(11, 31, 58, 0.04);
  --shadow-card:     0 4px 16px -2px rgba(11, 31, 58, 0.06), 0 2px 6px -1px rgba(11, 31, 58, 0.03);
  --shadow-elevated: 0 8px 24px -4px rgba(11, 31, 58, 0.12), 0 4px 12px -2px rgba(11, 31, 58, 0.06);
  --radius-xs:       6px;
  --radius-sm:       10px;
  --radius-md:       14px;
  --radius-lg:       18px;

  /* Typography */
  --font-latin:      'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-arabic:     'Noto Sans Arabic', 'Arabic Typesetting', 'Segoe UI', Tahoma, sans-serif;
  --font-jp:         'Noto Sans JP', 'Yu Gothic', 'Meiryo', 'Hiragino Kaku Gothic ProN', sans-serif;
}}

/* ── DARK MODE THEME ────────────────────────────────────────── */
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg-page:        #081220;
    --card-bg:        #0E2038;
    --text-primary:   #EEF4FC;
    --text-secondary: #9DB4D0;
    --text-muted:     #6C84A3;
    --border:         #1C3352;
    --border-subtle:  #152840;
    --shadow-card:    0 4px 16px rgba(0, 0, 0, 0.35);
  }}
}}

/* ── PROJECTOR HIGH-CONTRAST MODE ──────────────────────────── */
.ht-projector, body.ht-projector {{
  --bg-page:        #FFFFFF !important;
  --card-bg:        #FFFFFF !important;
  --text-primary:   #000000 !important;
  --text-secondary: #1F2937 !important;
  --border:         #1E6FD9 !important;
  --shadow-card:    0 2px 8px rgba(0,0,0,0.15) !important;
}}

/* ── GLOBAL RESETS & STREAMLIT TWEAKS ──────────────────────── */
body, .stApp {{
  font-family: var(--font-latin) !important;
  color: var(--text-primary) !important;
  background-color: var(--bg-page) !important;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}}

.stApp header {{
  background: transparent !important;
}}

.block-container {{
  padding-top: 1.5rem !important;
  padding-bottom: 3rem !important;
  max-width: 1400px !important;
}}

h1, h2, h3, h4, h5, h6 {{
  font-family: var(--font-latin) !important;
  color: var(--navy);
  font-weight: 600;
  letter-spacing: -0.02em;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}}

.ht-hero h1, .ht-hero h2, .ht-hero h3, .ht-hero div.ht-hero-title {{
  color: #FFFFFF !important;
}}

p, span, label {{
  font-family: var(--font-latin);
}}

/* ── HERO HEADER ───────────────────────────────────────────── */
.ht-hero {{
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  background: linear-gradient(135deg, #0B1F3A 0%, #112B4F 55%, #184275 100%) !important;
  color: #FFFFFF !important;
  padding: 22px 28px;
  border-radius: var(--radius-lg);
  margin-bottom: 18px;
  box-shadow: var(--shadow-elevated);
  position: relative;
  overflow: hidden;
  border: 1.5px solid rgba(47, 211, 201, 0.35) !important;
}}

.ht-hero * {{
  color: #FFFFFF !important;
}}

/* Subtle Wave Background (Seigaiha / Mediterranean Wave Motif) */
.ht-hero::before {{
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  opacity: 0.07;
  background-image: radial-gradient(circle at 100% 150%, #2FD3C9 24%, transparent 25%),
                    radial-gradient(circle at 0% 150%, #2FD3C9 24%, transparent 25%),
                    radial-gradient(circle at 50% 100%, #1E6FD9 10%, transparent 11%),
                    radial-gradient(circle at 100% 50%, #2FD3C9 15%, transparent 16%),
                    radial-gradient(circle at 0% 50%, #2FD3C9 15%, transparent 16%);
  background-size: 60px 30px;
  pointer-events: none;
}}

.ht-hero-left {{
  display: flex;
  align-items: center;
  gap: 20px;
  z-index: 1;
}}

.ht-hero-logo {{
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  filter: drop-shadow(0 2px 8px rgba(47, 211, 201, 0.35));
}}

.ht-hero-text {{
  display: flex;
  flex-direction: column;
}}

.ht-hero-title, .ht-hero h1, .ht-hero div.ht-hero-title {{
  font-family: var(--font-latin) !important;
  font-size: 2.15rem !important;
  font-weight: 800 !important;
  color: #FFFFFF !important;
  letter-spacing: -0.03em !important;
  line-height: 1.15 !important;
  margin: 0 !important;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.4) !important;
}}

.ht-hero-tagline {{
  font-size: 0.94rem !important;
  color: rgba(255, 255, 255, 0.90) !important;
  margin-top: 4px !important;
  font-weight: 400 !important;
  letter-spacing: -0.01em !important;
}}

.ht-hero-ribbon {{
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  z-index: 1;
}}

.ht-ribbon-badge {{
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px !important;
  background: rgba(47, 211, 201, 0.18) !important;
  border: 1.5px solid #2FD3C9 !important;
  color: #2FD3C9 !important;
  font-size: 0.82rem !important;
  font-weight: 700 !important;
  padding: 5px 12px !important;
  border-radius: 20px !important;
  letter-spacing: 0.03em !important;
  white-space: nowrap !important;
}}

.ht-ribbon-sub {{
  font-size: 0.74rem !important;
  color: rgba(255, 255, 255, 0.75) !important;
  text-align: right !important;
  letter-spacing: 0.02em !important;
}}

/* ── MANDATORY HONESTY BANNER ──────────────────────────────── */
.ht-banner {{
  background-color: #FFF9F8;
  border: 1px solid rgba(215, 38, 61, 0.25);
  border-left: 5px solid var(--vermilion);
  border-radius: var(--radius-sm);
  padding: 12px 18px;
  margin-bottom: 12px;
  display: flex;
  align-items: flex-start;
  gap: 14px;
  box-shadow: var(--shadow-sm);
}}

.ht-banner-body {{
  flex: 1;
}}

.ht-banner-title {{
  font-weight: 700;
  color: var(--vermilion);
  font-size: 0.88rem;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 3px;
}}

.ht-banner-sub {{
  font-size: 0.80rem;
  color: #5A6D82;
  line-height: 1.45;
}}

/* ── CHIPS & BADGES ────────────────────────────────────────── */
.ht-chip {{
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: rgba(11, 31, 58, 0.06);
  border: 1px solid rgba(11, 31, 58, 0.12);
  color: var(--navy);
  font-size: 0.72rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 12px;
  white-space: nowrap;
}}

.ht-chip-offline {{
  background: rgba(46, 158, 107, 0.12);
  border-color: rgba(46, 158, 107, 0.35);
  color: var(--green);
}}

.ht-chip-tariff {{
  background: rgba(232, 160, 32, 0.12);
  border-color: rgba(232, 160, 32, 0.35);
  color: #B27008;
  font-size: 0.68rem;
  margin-left: 6px;
}}

/* ── ADVISORY DECISION SUPPORT NOTICE ──────────────────────── */
.ht-advisory {{
  background-color: #F0F6FF;
  border: 1px solid rgba(30, 111, 217, 0.22);
  border-left: 4px solid var(--ocean);
  border-radius: var(--radius-sm);
  padding: 10px 16px;
  margin-bottom: 12px;
  font-size: 0.84rem;
  color: var(--navy);
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: var(--shadow-sm);
}}

.ht-advisory strong {{
  color: var(--ocean);
  font-weight: 600;
}}

/* ── HONEST LIMITATIONS BOX ────────────────────────────────── */
.ht-limitations {{
  background-color: #FFFFFF;
  border: 1px solid var(--border);
  border-left: 4px solid var(--text-muted);
  border-radius: var(--radius-sm);
  padding: 14px 18px;
  margin-bottom: 18px;
  box-shadow: var(--shadow-sm);
}}

.ht-limitations-title {{
  font-weight: 700;
  color: var(--navy);
  font-size: 0.86rem;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}}

.ht-limitations ul {{
  margin: 0;
  padding-left: 18px;
  font-size: 0.81rem;
  color: var(--text-secondary);
  line-height: 1.55;
}}

.ht-limitations li {{
  margin-bottom: 3px;
}}

.ht-limitations b {{
  color: var(--navy);
}}

/* ── KPI CARDS GRID (Responsive, No Truncation) ────────────── */
.ht-kpi-grid {{
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 22px;
}}

@media (max-width: 1200px) {{
  .ht-kpi-grid {{
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }}
}}

@media (max-width: 768px) {{
  .ht-kpi-grid {{
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }}
}}

.ht-kpi-card {{
  background: var(--card-bg);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  border: 1px solid var(--border);
  border-top: 4px solid var(--ocean);
  padding: 16px 16px 14px;
  min-height: 125px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  overflow: visible;
}}

.ht-kpi-card:hover {{
  transform: translateY(-2px);
  box-shadow: var(--shadow-elevated);
}}

.ht-kpi-card.kpi-water    {{ border-top-color: var(--ocean); }}
.ht-kpi-card.kpi-energy   {{ border-top-color: var(--green); }}
.ht-kpi-card.kpi-suspect  {{ border-top-color: var(--aqua-dark); }}
.ht-kpi-card.kpi-alert    {{ border-top-color: var(--vermilion); }}
.ht-kpi-card.kpi-sensor   {{ border-top-color: var(--ocean); }}

.ht-kpi-header {{
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}}

.ht-kpi-icon {{
  width: 22px;
  height: 22px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}}

.ht-kpi-label {{
  font-size: 0.72rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
  line-height: 1.2;
}}

.ht-kpi-value {{
  font-size: 1.65rem;
  font-weight: 700;
  color: var(--navy);
  font-variant-numeric: tabular-nums;
  line-height: 1.15;
  letter-spacing: -0.02em;
  margin-bottom: 4px;
}}

.ht-kpi-value-range {{
  font-size: 1.10rem;
  font-weight: 700;
  color: var(--navy);
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
}}

.ht-kpi-unit {{
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--text-muted);
  margin-left: 2px;
}}

.ht-kpi-sublabel {{
  font-size: 0.74rem;
  color: var(--text-secondary);
  line-height: 1.35;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
}}

.ht-kpi-sublabel.alert {{
  color: var(--vermilion);
  font-weight: 600;
}}

.ht-kpi-sublabel.nominal {{
  color: var(--green);
  font-weight: 500;
}}

/* ── DEMO STEPPER ───────────────────────────────────────────── */
.ht-stepper {{
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 0;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-card);
  overflow-x: auto;
}}

.ht-step-node {{
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  cursor: pointer;
}}

.ht-step-num {{
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: 700;
  transition: all 0.15s ease;
  font-variant-numeric: tabular-nums;
}}

.ht-step-active .ht-step-num {{
  background: var(--ocean);
  color: #FFFFFF;
  box-shadow: 0 2px 10px rgba(30, 111, 217, 0.45);
}}

.ht-step-done .ht-step-num {{
  background: var(--green);
  color: #FFFFFF;
}}

.ht-step-todo .ht-step-num {{
  background: #F0F4FA;
  color: var(--text-muted);
  border: 1.5px solid var(--border);
}}

.ht-step-label {{
  font-size: 0.72rem;
  color: var(--text-secondary);
  text-align: center;
  white-space: nowrap;
  font-weight: 500;
}}

.ht-step-active .ht-step-label {{
  color: var(--ocean);
  font-weight: 700;
}}

.ht-step-done .ht-step-label {{
  color: var(--green);
  font-weight: 600;
}}

.ht-step-line {{
  flex: 1;
  height: 2px;
  background: var(--border);
  min-width: 24px;
  margin: 0 8px 18px;
}}

.ht-step-line-done {{
  background: var(--green);
}}

/* ── SEGMENTED CONTROL ─────────────────────────────────────── */
.ht-seg-control {{
  display: inline-flex;
  background: #E8EEF7;
  border-radius: 20px;
  padding: 3px;
  gap: 3px;
}}

.ht-seg-tab {{
  padding: 5px 14px;
  border-radius: 16px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  color: var(--text-secondary);
  background: transparent;
  border: none;
}}

.ht-seg-tab.active {{
  background: var(--ocean);
  color: #FFFFFF;
  box-shadow: 0 1px 6px rgba(30, 111, 217, 0.35);
}}

/* ── AUTONOMY DISPLAY ──────────────────────────────────────── */
.ht-autonomy-row {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin: 16px 0;
}}

.ht-autonomy-card {{
  border-radius: var(--radius-md);
  padding: 18px 20px;
  text-align: center;
  box-shadow: var(--shadow-sm);
}}

.ht-autonomy-blind {{
  background: #FFFDF7;
  border: 2px solid var(--amber);
}}

.ht-autonomy-resil {{
  background: #F6FCF9;
  border: 2px solid var(--green);
}}

.ht-auto-label {{
  font-size: 0.76rem;
  color: var(--text-secondary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 6px;
}}

.ht-auto-value {{
  font-size: 2.3rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.03em;
  line-height: 1;
  margin-bottom: 4px;
}}

.ht-autonomy-blind .ht-auto-value {{ color: var(--amber); }}
.ht-autonomy-resil .ht-auto-value {{ color: var(--green); }}

.ht-auto-sub {{
  font-size: 0.74rem;
  color: var(--text-secondary);
}}

/* ── WORK ORDERS & MULTILINGUAL CARDS ──────────────────────── */
.ht-work-card {{
  background: #FFFFFF;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  padding: 16px 20px;
  margin-bottom: 14px;
  border: 1px solid var(--border);
  border-left: 5px solid var(--border);
}}

.severity-badge {{
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}}

.severity-minor    {{ background: rgba(232, 160, 32, 0.15); color: #B27008; }}
.severity-moderate {{ background: rgba(232, 100, 32, 0.15); color: #C45500; }}
.severity-critical {{ background: rgba(215, 38, 61, 0.15);  color: var(--vermilion); }}
.severity-healthy  {{ background: rgba(46, 158, 107, 0.15); color: var(--green); }}

.multilingual-card {{
  background: #FFFFFF;
  border: 1px solid var(--border);
  border-left: 5px solid var(--green);
  border-radius: var(--radius-sm);
  padding: 16px 20px;
  margin-top: 10px;
  font-family: var(--font-latin);
  color: var(--text-primary);
  font-size: 0.90rem;
  line-height: 1.6;
  direction: ltr;
  text-align: left;
  box-shadow: var(--shadow-sm);
}}

[lang=\"ar\"] .multilingual-card,
.multilingual-card.rtl {{
  direction: rtl;
  text-align: right;
  font-family: var(--font-arabic) !important;
  border-left: 1px solid var(--border);
  border-right: 5px solid var(--green);
}}

[lang=\"ja\"] .multilingual-card {{
  font-family: var(--font-jp) !important;
  border-left-color: var(--ocean);
}}

/* ── TABS STYLING ──────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
  gap: 8px !important;
  background-color: transparent !important;
  border-bottom: 2px solid var(--border) !important;
  padding-bottom: 2px !important;
}}
.stTabs [data-baseweb="tab"] {{
  border-radius: 8px 8px 0 0 !important;
  padding: 8px 16px !important;
  font-weight: 600 !important;
  color: var(--text-secondary) !important;
  background-color: transparent !important;
  border: none !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
  color: var(--ocean) !important;
  background-color: rgba(30, 111, 217, 0.06) !important;
}}
.stTabs [aria-selected="true"] {{
  color: var(--ocean) !important;
  border-bottom: 3px solid var(--ocean) !important;
  font-weight: 700 !important;
}}

/* ── SIDEBAR STYLING ───────────────────────────────────────── */
[data-testid="stSidebar"] {{
  background-color: #0B1F3A !important;
  border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
}}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {{
  color: rgba(255, 255, 255, 0.90) !important;
}}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{
  color: #FFFFFF !important;
}}

[data-testid="stSidebar"] hr {{
  border-color: rgba(255, 255, 255, 0.12) !important;
  margin: 1rem 0 !important;
}}

.ht-sidebar-section {{
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #2FD3C9 !important;
  padding: 10px 0 4px;
}}

/* Sidebar Form Controls */
[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
  background-color: #142844 !important;
  border: 1px solid rgba(255, 255, 255, 0.22) !important;
  border-radius: 8px !important;
  color: #FFFFFF !important;
}}
[data-testid="stSidebar"] div[data-baseweb="select"] * {{
  color: #FFFFFF !important;
  background-color: transparent !important;
}}

/* Dropdown popover menu options */
div[data-baseweb="popover"] ul,
div[data-baseweb="menu"] {{
  background-color: #142844 !important;
  border: 1px solid rgba(255, 255, 255, 0.18) !important;
}}
div[data-baseweb="popover"] li,
div[data-baseweb="menu"] li {{
  color: #FFFFFF !important;
  background-color: #142844 !important;
}}
div[data-baseweb="popover"] li:hover,
div[data-baseweb="menu"] li:hover {{
  background-color: #1E6FD9 !important;
  color: #FFFFFF !important;
}}

/* Segmented Control in Sidebar */
[data-testid="stSidebar"] [data-testid="stButtonGroup"] {{
  background-color: #142844 !important;
  border: 1px solid rgba(255, 255, 255, 0.20) !important;
  border-radius: 8px !important;
  padding: 3px !important;
}}

[data-testid="stSidebar"] button[data-testid="stBaseButton-segmented_control"] {{
  background-color: transparent !important;
  color: rgba(255, 255, 255, 0.75) !important;
  border: none !important;
  font-weight: 600 !important;
}}

[data-testid="stSidebar"] button[data-testid="stBaseButton-segmented_control"]:hover {{
  background-color: rgba(255, 255, 255, 0.08) !important;
  color: #FFFFFF !important;
}}

[data-testid="stSidebar"] button[data-testid="stBaseButton-segmented_controlActive"] {{
  background-color: #1E6FD9 !important;
  color: #FFFFFF !important;
  font-weight: 700 !important;
  border: none !important;
  border-radius: 6px !important;
}}

/* Sidebar Radio Buttons */
[data-testid="stSidebar"] div[role="radiogroup"] label {{
  color: rgba(255, 255, 255, 0.90) !important;
}}

/* Sidebar Captions */
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
  color: rgba(255, 255, 255, 0.70) !important;
}}

/* Sidebar Buttons */
[data-testid="stSidebar"] .stButton > button {{
  background-color: #1E6FD9 !important;
  color: #FFFFFF !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2) !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
  background-color: #1658B0 !important;
}}

/* ── FOOTER ────────────────────────────────────────────────── */
.ht-footer {{
  margin-top: 40px;
  padding: 20px 0;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 0.78rem;
  color: var(--text-muted);
}}
"""

    out_path = os.path.join(here, "app", "assets", "theme.css")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(css)
    print(f"Generated theme.css successfully ({len(css)} bytes)")

if __name__ == "__main__":
    generate()
