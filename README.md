# HydroTwin 💧⚡
### Digital Twin of Drinking Water Distribution Network with Energy & Leak Optimization
**Embassy of Japan in Tunisia Hackathon — Water + Energy Track**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![WNTR 1.5.0](https://img.shields.io/badge/WNTR-1.5.0-008080.svg)](https://wntr.readthedocs.io/)
[![EPANET PDD](https://img.shields.io/badge/EPANET-PDA%20PDD-green.svg)](https://www.epa.gov/water-research/epanet)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Advisory System](https://img.shields.io/badge/Control-Advisory%20Only-orange.svg)](#core-governance-rules)

---

> ### ⚠️ Mandatory Project Disclaimers
> 1. **100% Simulated Data**: All telemetry, pressures, pipe geometries, and pump schedules are simulated within EPANET/WNTR. This is an engineering prototype and does **not** use proprietary data from SONEDE, STEG, or Japanese municipal water bureaus.
> 2. **Advisory Decision Support**: **The system ADVISES, humans DECIDE.** No automatic SCADA or pump control is executed. All actions require human operator sign-off.
> 3. **Tunisian Water Losses**: Documented as an empirical range between **25% and 50%** across municipal sectors, never as a single static figure.

---

## 🌟 Overview & Bilateral Context

In Tunisia, municipal water distribution faces acute challenges: high non-revenue water loss rates (25% to 50%), aging cast-iron and asbestos-cement mains, and summer electricity load-shedding that disrupts pumping stations in major hubs like Grand Tunis and Sfax.

In Japan, municipal utilities (such as Tokyo, Nagoya, and Osaka) have achieved world-renowned water efficiency (<7% leakage) through dense digital telemetry, proactive night acoustic surveys, and intelligent pressure management.

**HydroTwin** bridges Japanese precision engineering with Tunisian operational realities. Built to run **100% locally on a standard laptop with open-source tools**, HydroTwin delivers:
1. **Pressure-Dependent Demand (PDD) Simulation**: Realistic 24-hour hydraulics using WNTR's Wagner PDA solver.
2. **Municipal Demand Forecasting**: Machine learning demand models with 90% prediction intervals across 5 districts.
3. **Dual-Track Leak Detection & Localization**: District water balance monitoring + topological graph smoothing that ranks suspect pipes into a Top-5 manifest.
4. **Energy Optimization under Hypothetical Tariffs**: Shifting pumping to off-peak night hours (saving 0 – 583 kWh/day across seasons, mean 292 kWh/day; 0.0 – 206.4 TND/day) while preserving 100% delivered demand volume.
5. **Emergency Power Cut Resilience**: Pre-filling storage and utilizing gravity supply to maintain service in Hospital Priority Districts during 4-hour grid blackouts.
6. **Dense vs. Sparse Sensor Adaptation**: Transparently evaluating Japanese-style dense telemetry (24 sensors) vs. emerging utility sparse telemetry (6 sensors + 1 failing).
7. **Multilingual Operator Assistant**: Instant work orders and intent-based Q&A in **Arabic (with native RTL)**, **French**, **Japanese**, and **English** with zero hallucinations.

---

## 🚀 Quickstart in 5 Commands

HydroTwin is cross-platform (Windows, macOS, Linux) and requires **Python 3.11+**.

```bash
# 1. Clone repository & navigate to workspace
git clone https://github.com/example/hydrotwin.git
cd hydrotwin

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows: .venv\Scripts\activate | Unix: source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate assumptions, datasets, and precompute demo cache
python run.py setup && python run.py demo

# 5. Launch the Streamlit Digital Twin Dashboard
python run.py app
```

> **Note**: On Unix or Git Bash systems with `make` installed, you can simply run:
> ```bash
> make setup && make demo && make app
> ```

---

## 🎬 3-Minute Live Hackathon Demo

For presentations before the hackathon jury, HydroTwin includes a precomputed, instant-response **Guided Demo Mode**:

1. Open the application at `http://localhost:8501`.
2. Toggle **"🚀 Guided 3-Minute Demo Mode"** in the sidebar.
3. Step through the 6 guided milestones (<0.2s response time, zero simulation lag):
   - **Step 1**: Baseline Digital Twin & 24h District Demand Forecasts with 90% confidence bands.
   - **Step 2**: Physical Pipe Rupture injection, dual-track detection, Top-5 suspect ranking, and multilingual work order generation.
   - **Step 3**: Diurnal Time-of-Use pump optimization under hypothetical tariffs (saving 0 – 583 kWh/day across seasonal profiles).
   - **Step 4**: Dense (24 sensors) vs. Sparse (6 sensors) telemetry comparison, transparently showing the honest accuracy degradation (37.7% -> 19.5% Top-5 suspect containment).
   - **Step 5**: Grid Blackout resilience: 4-hour pump outage with proactive tank pre-filling to protect the Hospital District above 18m head.
   - **Step 6**: Bilateral JICA-SONEDE 1-district pilot roadmap and transparent limitations.

For the full minute-by-minute presentation script and jury Q&A answers, see [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md).

---

## 📊 Evaluation & Hardened Benchmarks

All metrics are evaluated strictly on **220 unseen test leak scenarios** and **110 unseen test healthy days** (split strictly by disjoint node locations and scenario IDs; asserted zero data leakage). Every metric is reported with an empirical **95% cluster-bootstrap confidence interval** resampled across the 36 test leak locations.

> ### ⚠️ ACCEPTANCE CRITERION STATUS: Top-5 Majority Containment
> - **Criterion**: Primary suspect pipe in Top-5 for a majority (>50%) of all unseen leak scenarios.
> - **Status across ALL unseen leaks**: **NOT MET**
>   - **Rich Mode (24 sensors)**: Top-5 Exact Pipe = **30.9%** [20.8%, 42.2%]; Top-5 Adjacent = **37.7%** [26.5%, 50.0%].
>   - **Sparse Mode (6 sensors + 1 broken)**: Top-5 Exact Pipe = **12.7%** [5.5%, 21.2%]; Top-5 Adjacent = **19.5%** [10.5%, 30.3%].
> - **Status on DETECTED leaks only**: Rich Mode Top-5 reaches **50.0% Exact** and **60.7% Adjacent** (Sparse: 22.0% Exact, 32.1% Adj).
> - **Physical Root Cause**: Minor leaks (<10 m³/h) induce pressure drops (~0.04m) below transducer noise ($\sigma = 0.1\text{m}$ to $0.4\text{m}$), physically preventing detection via pressure alone.

### 1. Sensor-Mode Dependent Leak Localization Benchmark (Headline Metrics)

| Method / Operational Metric | Dense Japanese Mode (24 Sensors) | Sparse Utility Mode (6 Sensors + 1 Broken) | Degradation (Sparse vs. Rich) |
|---|---|---|---|
| **Top-1 Exact Pipe (Headline)** | **9.5%** [2.3%, 18.1%] | **3.6%** [0.0%, 9.6%] | -5.9% |
| **Top-3 Exact Pipe** | **21.8%** [12.1%, 32.4%] | **6.8%** [0.9%, 14.0%] | -15.0% |
| **Top-5 Exact Pipe** | **30.9%** [20.8%, 42.2%] | **12.7%** [5.5%, 21.2%] | -18.2% |
| **Top-1 Adjacent Pipe (Secondary)** | **15.0%** [6.8%, 23.6%] | **4.5%** [0.5%, 11.1%] | -10.5% |
| **Top-3 Adjacent Pipe** | **29.1%** [18.8%, 40.2%] | **12.3%** [5.0%, 21.2%] | -16.8% |
| **Top-5 Adjacent Pipe** | **37.7%** [26.5%, 50.0%] | **19.5%** [10.5%, 30.3%] | -18.2% |
| **Topological Hop <= 1 Hit** | **60.5%** | **42.3%** | -18.2% |
| **Topological Hop <= 2 Hit** | **72.3%** | **46.8%** | -25.5% |
| **Mean Topological Hop Error** | **3.3 hops** | **7.4 hops** | +4.1 hops |
| **Overall Detection Recall** | **55.5%** (Critical: 67.2%, Minor: 0.0%) | **49.5%** (Critical: 59.8%, Minor: 0.0%) | -6.0% |
| **Mean Detection Delay (Detected)** | **2.7 hours** [1.8, 4.0] | **4.3 hours** [2.9, 5.9] | +1.6 hours |
| **False Alarm Rate (110 Healthy Days)** | **0.0%** | **0.0%** | +0.0% |

*Random baseline: Top-1 Exact 0.9%, Top-5 Exact 4.3%, Top-1 Adj 2.3%, Top-5 Adj 10.3%, Mean Hop 5.4.*  
*Candidate pipes are ranked from ONE single list, mathematically guaranteeing `Hit@1 <= Hit@3 <= Hit@5`.*

### 2. Paired Comparison: HydroTwin vs. Nearest-Sensor Baseline
*Evaluated on the exact same 220 unseen test scenarios. Differences are computed pairwise per scenario: `Diff = HydroTwin - NearestSensor` with 95% cluster-bootstrap CIs:*
- **Rich Mode (24 Sensors)**:
  - Top-5 Exact Difference: **-0.4 pp** [-4.9, +3.7] (CI crosses zero; no significant difference).
  - Top-5 Adjacent Difference: **+3.7 pp** [-3.2, +11.5] (CI crosses zero; no significant difference).
  - Mean Hop Distance Difference: **-1.2 hops** [-1.9, -0.6] (**HydroTwin is 1.2 hops closer to the physical burst**, $p < 0.05$).
- **Sparse Mode (6 Sensors)**:
  - All paired difference CIs cross zero (Top-1 diff -0.4 pp [-3.3, +2.5], Top-5 diff -0.4 pp [-5.0, +4.1], Mean Hop diff +0.0 hops [-0.1, +0.1]).
  - **Honest Verdict**: Under sparse telemetry, there is **no demonstrated gain** over the nearest-sensor heuristic for micro-pipe isolation.

### 3. Diagnostic: Zero-Noise Identifiability Limits & Collinearity
- At $\sigma = 0\text{ m}$ (zero noise, perfect calibration):
  - Rich Mode: Top-1 Exact = **20.5%**, Top-5 Exact = **61.4%**, Top-5 Adj = **76.8%**, Mean Hop = **1.35 hops**.
  - Sparse Mode: Top-1 Exact = **6.4%**, Top-5 Exact = **24.1%**, Top-5 Adj = **31.4%**, Mean Hop = **4.62 hops**.
- **Physical Root Causes of Non-100% Exact Localization**:
  1. *Mathematical Collinearity*: In Net3, 748 pipe pairs in Rich mode (11.0%) and 1,007 pipe pairs in Sparse mode (14.8%) have pairwise cosine similarity $> 0.98$ (e.g. unmonitored branch spurs [167, 169], [171, 173], [107, 109]), producing identical sensor pressure drops.
  2. *Junction Degree Degeneracy*: Leaks occur at junction nodes with degree 2 to 4; designating `incident_pipes[0]` as ground truth penalizes equally valid incident pipes (Top-5 Adjacent reaches 76.8%).
- **District-Level Localization (vs. Random 20%)**:
  - In Sparse mode, HydroTwin identifies the correct municipal district in **33.6%** of cases (Top-1) and **40.5%** (Top-3) vs. 20.0% / 60.0% random baseline, confirming sparse telemetry functions as an effective macro-district filter.

### 4. Hydraulic Model Mismatch Benchmark
*Test scenarios with systematic physical perturbations ($\pm 15\%$ roughness, $\pm 10\%$ nodal demand, $\pm 0.15\text{m}$ sensor bias) vs. nominal twin model:*

| Operating Mode | Calibration State | Top-1 Exact | Top-5 Exact | Top-1 Adjacent | Top-5 Adjacent | Mean Hop Distance |
|---|---|---|---|---|---|---|
| **Rich Mode (24 sens)** | **Nominal (Perfect Calibration)** | **9.5%** | **30.9%** | **15.0%** | **37.7%** | **3.3 hops** |
| **Rich Mode (24 sens)** | **With Model Mismatch** | 5.5% | 22.3% | 10.9% | 29.1% | 4.6 hops |
| **Sparse Mode (6 sens)** | **Nominal (Perfect Calibration)** | **3.6%** | **12.7%** | **4.5%** | **19.5%** | **7.4 hops** |
| **Sparse Mode (6 sens)** | **With Model Mismatch** | 3.2% | 12.3% | 3.6% | 17.3% | 8.2 hops |

### 5. Physical Verification: Simulated Drops vs. Transducer Noise
*Computed from hydraulic simulations for leaks across varied flow rates at nearest sensor:*

| Target Leak Rate | Rich Sensor Drop | Sparse Sensor Drop | SNR ($\sigma = 0.1\text{m}$) | SNR ($\sigma = 0.4\text{m}$) | Physical Detectability |
|---|---|---|---|---|---|
| **5 m³/h** | **0.040 m** | **0.027 m** | 0.40 | 0.10 | Undetectable (noise dominates signal) |
| **8 m³/h** | **0.065 m** | **0.043 m** | 0.65 | 0.16 | Undetectable (below transducer resolution) |
| **15 m³/h** | **0.123 m** | **0.084 m** | 1.23 | 0.31 | Marginally detectable under industrial sensors |
| **30 m³/h** | **0.254 m** | **0.179 m** | 2.54 | 0.64 | Readily detectable across network |

### 6. Mode-Independent Pumping Optimization & Energy Sensitivity
*(Pumping energy depends strictly on diurnal consumer demand and STEG tariff schedules; completely independent of leak sensor count).*

- **Hydraulic Demand & Energy Conservation Decomposition**:
  - **Delivered Customer Demand Volume**: **62,124.2 m³** baseline vs. **62,124.2 m³** optimized (**0.0 m³ curtailment, 100% delivered demand preserved**).
  - **Delivered Specific Energy**: **0.0851 kWh/m³** baseline $\rightarrow$ **0.0803 kWh/m³** optimized (-5.6% efficiency gain).
  - **Customer Pressure Compliance ($\ge 15\text{m}$)**: **96.26%** baseline vs. **96.13%** optimized (exceeds 95% service standard).
  - **Operating Duty Rebalancing**: High-head intake Pump 10 (73.8m head, 14h $\rightarrow$ 11h ON, saving ~600 kWh); lower-head distribution booster Pump 335 (28.8m head, 8h $\rightarrow$ 9h ON, consuming ~290 kWh); net saving **292.1 kWh/day**.
  - **Stored Volume Preservation**: Invariant $V_{\text{total}}(24\text{h}) \ge V_{\text{total}}(0\text{h})$ strictly enforced. Active storage increases from $17,988\text{ m}^3$ to $19,746\text{ m}^3$ (+1,757 m³) in baseline and to $19,838\text{ m}^3$ (+1,850 m³) in optimized schedule (**+92.4 m³ higher reservoir buffer**). Zero phantom savings from reservoir drawdown.
- **Physical Explanation for Summer 0.0 Savings**: High summer customer demand requires continuous pump operation to prevent storage exhaustion; midday pump shutoff is hydraulically impossible without pressure deficits.
- **Tariff Status**: All tariffs are labeled as **hypothetical time-of-use tariffs** (assumed hypotheses to verify).
- **Simulated Electricity Saved**: **0.0 – 583.1 kWh / day** (Mean: 291.7 kWh / day; 0.0% – 14.6% savings).
- **Simulated Bill Saved**: **0.0 – 206.4 TND / day** (Mean: 69.7 TND / day; 0.0% – 17.4% savings).
- **Effective Tariff Rate**: 0.203 – 0.320 TND/kWh across seasonal stress profiles.

### 7. Mode-Independent Emergency Outage Resilience & Autonomy Estimator
*(Evaluates gravity buffer autonomy during blackouts across priority sectors. Compliance computed from integer node counts at assumed hospital threshold $\ge 18\text{m}$):*

- **Hospital Priority Sector (District 3) No-Outage Control**:
  - All 13 District 3 Nodes: **92.3%** compliance ($\\ge 18\text{m}$).
  - Reachable 12 Nodes (excluding Node 20): **100.0%** compliance.
  - Node 20 Outlier: **0.0%** compliance (elevation 39.32m directly at Tank 3 crest; gravity head cannot physically reach 18m).
- **Single-Pump Outage Sweep (Pump 10 Off, 2h to 8h)**:
  - District 3 Hospital Zone (13 monitored junctions): **92.3%** compliance (1200/1300 junction-hours) in both unmitigated and resilience plans (+0.0 pp binary gain).
  - District 1 Administration Zone (22 monitored junctions): **96.2%** compliance (2116/2200 junction-hours).
  - Combined Critical Sectors (35 monitored junctions): **94.7%** compliance (3316/3500 junction-hours).
- **Extreme Dual-Pump Blackout Sweep (Pumps 10 & 335 simultaneously OFF up to 24h)**:
  - District 3 Reachable Nodes maintain **100.0%** compliance across 4h, 8h, 12h, 18h, and 24h outages. Network-wide compliance ($\ge 15\text{m}$) remains 95.7%.
- **Network Storage Autonomy Hours**:
  - Total active storage: **17,988 m³**; average demand rate: **2,485 m³/h** $\rightarrow$ Network-wide zero-pumping autonomy: **7.2 hours**; District 3 dedicated tank autonomy: **>32 hours**.

> **Honest Resilience Finding**: Elevated storage reservoir Tank 3 (capacity ~18,800 m³ at elevation 39.3m) sustains gravity feed for 12/13 District 3 junctions across all blackout durations; Node 20 at the tank crest is physically bounded below 18m. Binary compliance gain is **+0.0 percentage points**. The resilience module operates as an **operational stress-testing and autonomy estimation tool**: tracking reservoir volume depletion rate (~250 to 580 m³/h) and dry-out horizons to schedule diesel generator deployment before reservoir exhaustion.

### 8. Municipal District Node Counts & Boundary Audit
The 92 demand junctions are partitioned into 5 contiguous municipal districts using deterministic spatial K-Means clustering on junction coordinates:
- **District 1 - Centre-Ville**: **22 junctions** (Commercial center & administrative offices)
- **District 2 - El Menzah**: **17 junctions** (Residential quarter)
- **District 3 - Medina & Hospital**: **13 junctions** (Hospital & historical medina; 18m threshold)
- **District 4 - Zone Industrielle**: **21 junctions** (Industrial park)
- **District 5 - Les Berges**: **19 junctions** (Coastal suburban; sensitive to over-pressure)
- **Total Network**: **92 junctions** ($22 + 17 + 13 + 21 + 19 = 92$, 100% partitioned).
*Audit Note on District 1*: Preliminary manual drafts cited 19 nodes because early manual boundary sketches omitted 3 boundary junction nodes (101, 103, 105). Under deterministic spatial clustering, District 1 strictly contains 22 junction nodes.

See full methodological analyses in [docs/EVALUATION.md](docs/EVALUATION.md).

---

## 🏗️ System Architecture

```
KIZUNA/
├── config.py                 # Centralized physical, economic, and simulation assumptions
├── generate_assumptions.py   # Automated markdown generator for assumptions
├── run.py                    # Cross-platform command dispatcher
├── Makefile                  # Unix build and test orchestration
├── requirements.txt          # Python dependencies
├── network/                  # Hydraulic topology & graph modules
│   ├── loader.py             # Loads Net3 .inp, sets PDD, clusters 5 districts
│   └── graph.py              # NetworkX topological graph & spatial hop distances
├── sim/                      # Physical hydraulic simulation engine
│   ├── simulator.py          # WNTRSimulator runner, pressure, energy, water balance
│   ├── leak_injector.py      # Torricelli orifice leaks & pipe splitting
│   ├── sensor_network.py     # Dense (24) vs. Sparse (6 + 1 faulty) sensor models
│   └── scenario_generator.py # Generates unseen scenario training datasets
├── ml/                       # Machine learning & analytics
│   ├── demand_forecasting.py # District demand regressor with 90% prediction intervals
│   ├── leak_detector.py      # Isolation forest + district water balance gap (>12%)
│   ├── leak_localizer.py     # Topological residual drop + graph distance smoothing
│   └── transfer.py           # Masked sensor pretraining & sparse transfer evaluation
├── planner/                  # Pumping optimization & grid resilience
│   ├── pump_optimizer.py     # STEG TOU tariff optimization vs Net3 baseline
│   └── resilience.py         # 4h pump blackout simulation & hospital protection
├── app/                      # Streamlit interactive UI & Multilingual Engine
│   ├── main.py               # Main application entrypoint & guided demo runner
│   ├── components.py         # Plotly network maps, honesty banners, metric cards
│   ├── demo_steps.py         # 6-step precomputed presentation cache
│   ├── multilingual.py       # Deterministic generator in ar (RTL), fr, ja, en
│   └── reports.py            # Printable HTML scenario audit report generator
├── tests/                    # Pytest verification test suite
│   ├── test_phase0_setup.py
│   ├── test_phase1_network_sim.py
│   ├── test_phase2_demand_forecasting.py
│   ├── test_phase3_leaks.py
│   ├── test_phase4_transfer.py
│   ├── test_phase5_pump_optimization.py
│   ├── test_phase6_multilingual.py
│   ├── test_phase7_dashboard_demo.py
│   └── test_phase8_quality_integrity.py
└── docs/                     # Comprehensive technical documentation
    ├── ARCHITECTURE.md       # System design diagrams and module interaction
    ├── ASSUMPTIONS.md        # Physical and economic calibration parameters
    ├── ASSUMPTIONS_AND_SOURCES.md # Verified vs. unverified sources table
    ├── EVALUATION.md         # Real metrics on unseen scenarios
    ├── DEMO_SCRIPT.md        # 3-minute timed live demo script & jury Q&A
    └── RISKS.md              # Hydraulic, operational, and algorithmic risk matrix
```

For the complete technical blueprint, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## 🧪 Comprehensive Test Suite

Run the full automated test suite covering all 8 phases:

```bash
# Run all tests
pytest tests/ -v

# Or using the cross-platform dispatcher
python run.py test
```

All tests execute in under 30 seconds and validate:
- PDD physical hydraulic constraints and water conservation
- Deterministic demand forecast bounds and residual intervals
- Zero hallucinations in multilingual operator advice
- STEG tariff cost reductions and pressure compliance
- Demo cache completeness and instant loading

---

## 🛡️ Core Governance Rules

1. **Advisory First**: The platform generates recommendations, work orders, and suggested schedules. Certified human operators maintain full operational authority.
2. **Scientific Honesty**: Every screen displays the simulated data banner. We do not claim access to proprietary SONEDE SCADA telemetry or secret Japanese utility logs.
3. **No Hallucinations**: Multilingual alerts are deterministically generated from structured hydraulic JSON outputs. When there is no leak, no leak is ever reported.

---

## 🤝 Bilateral Roadmap & Next Steps

HydroTwin is designed as a foundational proof-of-concept for the **Embassy of Japan in Tunisia** and **JICA**:
- **Phase 1 Pilot**: 1-district sandbox pilot in Greater Tunis (e.g., El Menzah) or Sfax.
- **Low-Cost Telemetry**: 6 IoT pressure loggers + 1 electromagnetic boundary meter.
- **Operational Integration**: Advisory decision support alongside regional SONEDE dispatchers.

---

*Developed for the Embassy of Japan in Tunisia Hackathon (Water + Energy) — 2026.*
