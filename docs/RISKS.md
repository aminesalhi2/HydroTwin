# HydroTwin: Operational, Hydraulic & Algorithmic Risk Assessment

> **GOVERNANCE MANDATE**: Water distribution networks constitute critical life-support infrastructure. Implementing digital twins and AI advisory systems entails hydraulic, operational, and institutional risks that must be systematically evaluated and mitigated.

---

## 1. Risk Matrix Overview

| Risk Category | Specific Failure Mode | Severity | Probability | Primary Mitigation Strategy |
|---|---|---|---|---|
| **Hydraulic** | Water hammer / pressure transients from sudden pump switching | Critical | Medium | Soft-start ramping, gradual valve throttling, max 1 dispatch shift/hour |
| **Hydraulic** | Water age & stagnation in storage tanks during off-peak refill | Moderate | Medium | Tank turnover rules (minimum 30% daily volume cycle), residual chlorine tracking |
| **Hydraulic** | Low-pressure cavitation in elevated districts (e.g. Ennasr) | High | Low | Hardcoded constraint: minimum 15m service head across all customer junctions |
| **Operational** | Operator alarm fatigue from false-positive leak alerts | Moderate | Low | Dual-track confirmation: require both water-balance discrepancy and pressure drop |
| **Telemetry** | Sensor drift, calibration loss, or dead battery | Moderate | High | Sparse-mode fault tolerance, spatial graph consensus filtering |
| **Commercial** | Conflating meter under-registration with physical leakage | Moderate | High | Explicit advisory labeling: "Water balance gap reflects physical loss + apparent loss" |
| **Algorithmic** | Out-of-distribution seasonal heat waves distorting demand forecast | Low | Medium | 90% empirical prediction intervals, fallback to historical diurnal averages |
| **Cybersecurity** | Remote manipulation of pump dispatch / telemetry tampering | Critical | Low | Air-gapped advisory posture: zero direct SCADA control interfaces |

---

## 2. In-Depth Hydraulic & Engineering Risks

### 2.1 Water Hammer and Dynamic Pressure Surges
- **Risk**: Shifting large pump operations to take advantage of STEG off-peak tariffs (22:00 - 06:00) could cause rapid momentum changes ($\Delta v$) in transmission mains, generating transient pressure waves (water hammer) governed by the Joukowsky equation:
  $$\Delta P = \rho \cdot a \cdot \Delta v$$
- **Mitigation**:
  1. The optimizer restricts pump status switches to a maximum of 2 transitions per 24-hour cycle.
  2. The digital twin enforces advisory warnings recommending variable frequency drive (VFD) ramping over a minimum of 180 seconds rather than instantaneous hard contactor switching.

### 2.2 Elevated Storage Stagnation & Chlorine Residual Decay
- **Risk**: Excessive pre-filling of storage tanks during off-peak hours could lead to prolonged hydraulic retention times (water age $> 48\text{ hours}$), causing disinfectant residual dissipation and secondary bacterial regrowth.
- **Mitigation**:
  1. Tank storage levels are constrained between 25% and 95% of active capacity.
  2. The schedule ensures full daily tank volume turnover, cycling at least 40% of tank volume during the morning draw (06:00 - 12:00).

### 2.3 Excess Pressure Burst Acceleration
- **Risk**: Over-pressurizing low-elevation zones (> 5.5 bar) during off-peak pumping increases background leakage flow according to Torricelli's orifice relationship ($Q \propto \sqrt{P}$) and elevates burst probability on aging asbestos-cement and cast-iron mains.
- **Mitigation**:
  1. Objective function penalizes excess nodal pressure above $55\text{ m}$.
  2. High-pressure zones trigger pressure-reducing valve (PRV) advisory recommendations.

---

## 3. Telemetry, Sensor & Measurement Risks

### 3.1 Sparse Sensor Unobservability
- **Risk**: In emerging networks with sparse instrumentation (6 loggers across 100+ km of pipe), small fissures ($< 10\text{ m}^3/\text{h}$) may produce pressure drops smaller than ambient sensor noise ($\sigma = 0.4\text{ m}$), making exact localization mathematically non-unique.
- **Mitigation**:
  1. HydroTwin explicitly displays the expanded topological search radius (average 2.6 hops in sparse mode).
  2. Work orders never guarantee a single pipe; they output a ranked candidate manifest for field acoustic correlators.

### 3.2 Apparent Losses vs. Real Physical Leaks
- **Risk**: Aging residential mechanical water meters typically suffer from under-registration at low flow rates, while unauthorized tappings create unexplained consumption. Treating every district water balance gap as an underground burst leads to wasted excavation costs.
- **Mitigation**:
  1. Every work order explicitly lists: *"Unexplained gap indicates water balance discrepancy; check meter calibration and unauthorized draw before excavation."*
  2. The system requires spatial pressure drop correlation before recommending physical excavation.

---

## 4. Machine Learning & Algorithmic Guardrails

### 4.1 Zero-Hallucination Multilingual Architecture
- **Risk**: Generative language models can hallucinate plausible-sounding pipe failures or invent imaginary burst coordinates, misleading utility dispatchers.
- **Mitigation**:
  1. The multilingual assistant operates deterministically using template-based generation strictly bound to the WNTR simulation output JSON.
  2. If `has_leak == False`, the assistant is programmatically prevented from reporting any leak.
  3. Optional LLM rephrasing is locked behind an environment variable and strictly conditioned on verified JSON facts.

### 4.2 Concept Drift and Seasonal Shocks
- **Risk**: Extreme climate events (e.g., heatwaves $> 45^\circ\text{C}$ in central Tunisia) can cause municipal water demand to surge outside the training distribution of the Random Forest regressor.
- **Mitigation**:
  1. Demand forecasts output 90% prediction intervals so operators can see uncertainty bands widen under extreme inputs.
  2. The model uses conservative clipping against physical maximum pumping capacity.

---

## 5. Institutional & Governance Safeguards

### 5.1 Human-in-the-Loop Advisory Doctrine
- **Hard Rule**: HydroTwin has **no direct control connections** to SCADA plcs, variable frequency drives, or motorized gate valves.
- **Workflow**:
  ```mermaid
  flowchart LR
      AI["HydroTwin Advisory Twin"] -->|Generates Work Order & Schedule| ENG["Certified SONEDE Operator"]
      ENG -->|Reviews, Validates & Signs Off| DISPATCH["Field Crew / SCADA Dispatch"]
  ```
- All pump schedule adjustments and field inspections require explicit operator authorization, ensuring legal accountability and operational safety remain with certified utility personnel.
