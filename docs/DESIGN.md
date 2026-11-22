# HydroTwin Design Specification — Control-Room Precision

> **Identity**: Japan × Tunisia · Clean, restrained, high-end control-room instrumentation.
> **Benchmark aesthetic**: Linear / Stripe / Apple dashboards — generous whitespace, hairline borders, tabular figures, zero visual clutter.

---

## 1. Design Tokens & Palette

Strict 4-color semantic palette defined in `app/assets/theme.css` and `.streamlit/config.toml`:

| Token | Value | Semantic Role |
|---|---|---|
| `--ink-bg` | `#0B1528` | Sidebar, control-room console panels, map canvas |
| `--ink-surface` | `#132238` | Sidebar inputs, dropdowns, segmented control base |
| `--canvas-bg` | `#F8F9FA` | Main page canvas (warm off-white, projector-friendly) |
| `--card-bg` | `#FFFFFF` | Metric cards, ticket surfaces, popovers |
| `--hairline` | `#E2E8F0` | 1px clean dividers and card borders |
| `--teal` | `#0D9488` | **Single primary water accent** (brand, active tabs, healthy states) |
| `--teal-subtle` | `rgba(13, 148, 136, 0.08)` | Active selections, soft chips, highlight fills |
| `--vermilion` | `#E11D48` | **Single reserved alert color** (leaks, active outages, critical warnings ONLY) |
| `--vermilion-subtle` | `rgba(225, 29, 72, 0.08)` | Alert ticket backgrounds, outage band fills |
| `--amber` | `#D97706` | Secondary advisory notices, moderate warnings |
| `--text-primary` | `#0F172A` | Primary typography (high-contrast slate) |
| `--text-secondary` | `#475569` | Secondary labels, units, helper text |
| `--text-muted` | `#94A3B8` | Subtle captions, timestamps, reference lines |

---

## 2. Typography & Iconography

- **UI Font**: `Inter` (local woff2: 400, 500, 600, 700), `system-ui, -apple-system, sans-serif`.
- **Numbers / Metrics**: Monospace tabular figures (`font-variant-numeric: tabular-nums`, monospace fallback for gauges).
- **Arabic Typography**: `Noto Sans Arabic` (local woff2), auto-applied on `[lang="ar"]` with full right-to-left mirroring (`direction: rtl`).
- **Japanese Typography**: `Noto Sans JP` (local woff2), clean line-height and letter-spacing for kanji/kana.
- **Iconography**: **100% SVG line icons (2px stroke)**. Zero emojis across the entire interface (sidebar, buttons, tabs, status pills, work orders).

---

## 3. Layout & Information Density

- **Header**:
  - Left: Refined SVG droplet network mark + "HydroTwin" + tagline *"A digital twin that finds leaks and cuts pumping energy."*
  - Right: Single slim clickable pill: `Simulated data · advisory only` $\to$ opens `st.popover` with concise bulleted prototype limits.
  - Eliminated: bulky red disclaimer banner, blue advisory box, and honest limitations panel from the default viewport.
- **Top Stepper**:
  - Horizontal clean segmented scenario switcher: `1 Normal` · `2 Leak` · `3 Night Pumping` · `4 Power Outage`.
  - One-click instant dispatch (<150 ms) to that scenario.
- **KPI Cards (Top Row, Exactly 4)**:
  1. **Water Loss Rate**: Primary value in m³/h (0 if healthy; vermilion if leak active) + subtext.
  2. **Pumping Energy**: Primary value `292 kWh/d saved` + small secondary `Range: 0–583 kWh/d` + mini sparkline.
  3. **Tariff Savings**: Primary value `33.6 TND/d` (TOU rate) + secondary `86.2 TND/d flat tariff`.
  4. **Network State**: "Nominal (100% Compliance)" or "Incident Active: District 1" with hairline top accent.

---

## 4. Plotly Chart Template (`hydrotwin_clean`)

Standardized Plotly theme applied across every chart:
- **Geometry**: 2px thin traces; fill areas at 10% opacity (`rgba(13, 148, 136, 0.10)`).
- **Grid & Axes**: Transparent background, no outer frame/box, horizontal dotted gridlines only (`#E2E8F0`, 1px dot). Zero vertical gridlines.
- **Threshold Lines**: Quiet reference lines (`add_hline`) with right-side annotations for 15 m minimum pressure rule.
- **Event Annotations**:
  - Leak start: Vermilion marker + vertical dashed hairline.
  - Pump outage window: Subtle shaded band (`rgba(225, 29, 72, 0.08)`) with "Pump Outage" label.
  - Off-peak tariff strip: Soft teal band (`rgba(13, 148, 136, 0.05)`).
- **Hover**: Compact unified card showing time, exact metric, units, and delta vs baseline.
- **Legend**: Inline annotations at trace ends or compact horizontal pill bar at the bottom; never obscuring chart headers.

---

## 5. Map Refinements

- **Dark Navy Canvas**: Deep control-room contrast (`#0B1528`).
- **District Zones**: Translucent convex hulls with soft fill and subtle dashed outline.
- **Label Collision Fix**: Offset vectors for clustered node labels (e.g. `Res River` vs `Pump 335`, `Res Lake` vs `Pump 10`) preventing text overlap.
- **Pipes**: 1.5–3.5px width scaled by flow; muted semi-transparent `#334155`.
- **Pressure Color Scale**: Perceptually uniform (Teal $\to$ Amber $\to$ Vermilion).
- **Leak Marker**: Vermilion target ring with outer glow halo and compact inspection tag.

---

## 6. Functional Tabs

1. **Digital Twin Map**: Live hydraulic state, timeline hour slider, clean bottom legend.
2. **Leak Detection & Work Orders**:
   - Work order rendered as an engineering ticket (severity pill, target DMA, estimated burst flow, prioritized suspect pipes as confidence bars, actionable step).
   - District water balance table with inline gap progress bars.
3. **Energy & Outage**:
   - Before/after pumping power curves with shaded energy saving area.
   - Tank autonomy drainage curves (Outage-Blind vs Pre-Fill Plan).
4. **Operator Assistant**:
   - Clean chat-style response card with language pills and full RTL support for Arabic.

---

## 7. Implementation Roadmap

1. **Tokens & CSS**: Update `app/assets/theme.css` with clean palette, hairline borders, remove emojis.
2. **Header & Stepper**: Modern header layout with `st.popover` for advisory notice, horizontal scenario stepper.
3. **KPI Cards**: Max 4 cards with single primary numbers, tabular figures, secondary range text.
4. **Plotly Template**: Thin lines, dotted horizontal grid, threshold lines, shaded outage/tariff bands.
5. **Map**: Offset labels to fix overlaps, clean pipe widths, compact bottom legend.
6. **Tabs Polish**: Ticket work orders, inline balance bars, clean assistant interface.
7. **Verification & Commit**: Full pytest suite, visual snapshots, atomic commits on branch `design`.
