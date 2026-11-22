# HydroTwin Design System — Calm Precision

> Japanese Minimalism × Mediterranean Warmth

## Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--navy` | `#0B1F3A` | Primary dark, text, backgrounds |
| `--ocean` | `#1E6FD9` | Primary blue, links, active states |
| `--aqua` | `#2FD3C9` | Water accent, highlights, success indicators |
| `--sand` | `#F4EFE6` | Light background (Mediterranean warmth) |
| `--vermilion` | `#D7263D` | Alerts, honesty banner, Japan nod |
| `--green` | `#2E9E6B` | Healthy/OK, completed states |
| `--amber` | `#E8A020` | Warnings, minor severity |
| `--white` | `#FFFFFF` | Card backgrounds |
| `--text-primary` | `#0B1F3A` | Main text |
| `--text-secondary` | `#4A6080` | Supporting text, labels |
| `--border` | `#DDE3ED` | Dividers, card borders |

## Fonts

All fonts are bundled as local `woff2` files in `app/assets/fonts/`. **No CDN dependency.**

| Font | Usage | File |
|------|-------|------|
| **Inter** (400/500/600/700) | Latin text, UI elements | `Inter-{weight}.woff2` |
| **Noto Sans Arabic** (400/700) | Arabic RTL content | `NotoSansArabic-{weight}.woff2` |
| **Noto Sans JP** (400/700) | Japanese content | `NotoSansJP-{weight}.woff2` |

Fallback chain: `system-ui → -apple-system → sans-serif` (works fully offline even if woff2 stubs are invalid).

## Components

### `.ht-hero`
Full-width hero header card. Navy gradient background, flex row: logo left, title+tagline center, ribbon right. Used once at top of every page.

### `.ht-banner`
Honesty disclaimer — always visible, vermilion left border 6px, sand background. Contains the simulated-data warning and offline chip.

### `.ht-advisory`
Advisory badge — ocean-tinted `#E8F2FF` background, 4px ocean left border. Displays the decision-rule text.

### `.ht-limitations`
Honest limitations box — white bg, `#DDE3ED` border, grey left border 5px. Bullet list of prototype constraints.

### `.ht-kpi-grid` / `.ht-kpi-card`
5-column responsive grid of KPI summary cards. Each card has a colored top border (`kpi-blue`, `kpi-green`, `kpi-ocean`, `kpi-red`, `kpi-aqua`), 16px border-radius, card shadow, icon + label + value + sublabel layout.

### `.ht-stepper`
Demo stepper — flex row of numbered circles (32px) connected by lines. Active circle = ocean, completed = green, todo = sand/grey.

### `.ht-work-card`
Work order card with severity badge. Badge classes: `severity-minor` (amber), `severity-moderate` (orange), `severity-critical` (vermilion), `severity-healthy` (green).

### `.multilingual-card`
Language-aware container. RTL Arabic gets right border + Noto Sans Arabic. Japanese gets Noto Sans JP. LTR languages get Inter.

### `.ht-autonomy-row` / `.ht-autonomy-card`
Two-column display for outage autonomy metrics. Blind = amber theme, Resilience = green theme.

## Light/Dark Mode

The CSS includes `@media (prefers-color-scheme: dark)` overrides that:
- Flip `--sand` to `#0F1A2E` (deep navy background)
- Flip `--card-bg` to `#1A2A42`
- Flip `--border` to `#2A3A52`
- Adjust text colors for contrast

> [!NOTE]
> Streamlit's own theme config in `.streamlit/config.toml` takes precedence. Dark mode media queries serve as a fallback for the HTML report export.

## Projector Mode

Add class `ht-projector` to `<body>` or `.stApp` for high-contrast mode (larger KPI values, thicker top borders, white background). Useful for conference demos.

To activate: inject `<script>document.body.classList.add('ht-projector')</script>` via `st.markdown`.

## Network Map Design

The Plotly network figure uses a **dark navy background** (`plot_bgcolor="#0B1F3A"`) for a "digital twin control room" aesthetic:
- Pipes: `#2A4A6A` (muted, readable on dark)
- Junctions: Colored by pressure using `PRESSURE_COLORSCALE` (blue→aqua→amber→red)
- Suspect pipes: Rank 1 = vermilion width 7, Rank 2–3 = amber width 5, Rank 4–5 = yellow width 3
- Pumps: Diamond marker, navy fill, aqua border
- Tanks: Square marker, aqua fill, navy border
- Active leak: Star + ring (pulsing ring effect via two traces)

## Rollback Instructions

```bash
# View all changed files
git diff --name-only master design

# Rollback specific file
git checkout master -- app/components.py

# Full rollback to master
git checkout master

# View this branch's design files only
git stash list
```

> [!CAUTION]
> Rollback removes ALL design changes. The `.streamlit/config.toml` and `app/assets/` directory will be gone. Run `git stash` first if you want to preserve any work.

## File Inventory

| File | Purpose |
|------|---------|
| `.streamlit/config.toml` | Streamlit theme configuration |
| `app/assets/theme.css` | Full design system CSS |
| `app/assets/logo.svg` | Water drop + network graph logo (64×80) |
| `app/assets/favicon.svg` | Smaller favicon version (32×40) |
| `app/assets/plotly_template.py` | Custom Plotly `hydrotwin` template |
| `app/assets/fonts/*.woff2` | Offline font bundles |
| `app/components.py` | Premium UI components (all signatures preserved) |
| `app/main.py` | Main app with hero header + demo stepper |
| `app/multilingual.py` | Updated CSS for RTL/JP font references |
| `app/reports.py` | HTML report with new palette |
| `docs/DESIGN.md` | This document |
| `docs/screenshots/README.md` | Screenshot guide |
