# HydroTwin — Screenshots Guide

Screenshots document the UI state at key demo steps for sharing with judges, JICA partners, and SONEDE stakeholders.

## Taking Screenshots with Playwright

Since Playwright may not be installed, we provide both automated and manual options.

### Option A: Manual Screenshots

1. Launch the app: `python -m streamlit run app/main.py`
2. Open browser to `http://localhost:8501`
3. Navigate to each demo step (1–6) using the sidebar stepper
4. Use the browser's built-in screenshot shortcut:
   - **Chrome/Edge**: F12 → three dots menu → "Capture screenshot"
   - **Firefox**: F12 → three dots menu → "Take a screenshot"
   - **Windows**: `Win + Shift + S` (Snipping Tool) or `PrtScn`

### Option B: Playwright (if installed)

```bash
# Install Playwright
pip install playwright
playwright install chromium

# Take screenshots
python docs/screenshots/capture.py
```

### Recommended Screenshot Set

| Filename | Content | Demo Step |
|----------|---------|-----------|
| `01_hero_banner.png` | Hero header + honesty banner + KPI cards | — |
| `02_twin_map_rich.png` | Network map — rich sensor mode, healthy | Step 1 |
| `03_leak_detected.png` | Network map — leak star + suspect pipes | Step 2 |
| `04_work_order_ar.png` | Arabic RTL work order | Step 2 (Arabic) |
| `05_pump_schedule.png` | Duty-rebalancing dispatch chart | Step 3 |
| `06_sparse_comparison.png` | Rich vs sparse accuracy bar chart | Step 4 |
| `07_outage_tanks.png` | Tank fill gauges + autonomy cards | Step 5 |
| `08_pilot_roadmap.png` | JICA bilateral roadmap | Step 6 |

### Naming Convention

```
KIZUNA/docs/screenshots/
  YYYY-MM-DD_stepN_description.png
```

### Playwright Capture Script (Template)

```python
# docs/screenshots/capture.py
from playwright.sync_api import sync_playwright
import time

def capture_all():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto("http://localhost:8501")
        time.sleep(3)  # wait for Streamlit to load

        # Hero + KPI cards
        page.screenshot(path="docs/screenshots/01_hero_banner.png", full_page=False)

        # Navigate to demo mode — click toggle
        page.locator("text=Guided 3-Minute Demo Mode").click()
        time.sleep(1)
        page.screenshot(path="docs/screenshots/02_twin_map_rich.png")

        browser.close()

if __name__ == "__main__":
    capture_all()
```

> [!NOTE]
> Streamlit requires the app to be running before Playwright can capture screenshots. Start the server with `python -m streamlit run app/main.py` in a separate terminal.
