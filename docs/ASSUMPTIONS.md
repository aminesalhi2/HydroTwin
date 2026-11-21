# HydroTwin: Physical, Economic & Simulation Assumptions

> **MANDATORY NOTICE**: SIMULATED DATA - NOT SONEDE OR OPERATOR DATA. Calibrated on published engineering and academic figures for demonstration purposes only.
>
> **OPERATIONAL PRINCIPLE**: The system ADVISES, humans DECIDE. No autonomous pump or valve control is performed. Recommendations require operator sign-off.

This document details all parameters, operational thresholds, and domain assumptions encoded in `config.py`.

---

## 1. Random Seeds and Temporal Resolution
- **Random Seed**: `42` (strictly enforced across all synthetic generation, noise models, and train/test splits for full reproducibility).
- **Simulation Duration**: `24 hours` (24-hour diurnal operational cycle).
- **Hydraulic Timestep**: `1 hour` (3600 seconds).

---

## 2. Electricity Tariff Structure (Tunisia STEG Calibration)
Calibrated on the Tunisian National Electricity and Gas Company (STEG) Medium-Voltage Industrial Time-of-Use schedule:
- **Off-Peak Tariff (22:00 - 06:00)**: `0.210 TND/kWh` (~10.1 JPY/kWh)
- **Day/Standard Tariff (06:00 - 18:00, 21:00 - 22:00)**: `0.295 TND/kWh` (~14.2 JPY/kWh)
- **Peak Evening Tariff (18:00 - 21:00)**: `0.380 TND/kWh` (~18.2 JPY/kWh)
- **Currency Conversion Reference**: `1 TND ≈ 48.0 JPY`.

---

## 3. Hydraulic Service Constraints
- **Minimum Service Pressure**: `15.0 m` (~1.5 bar). Below this threshold, consumer taps suffer low pressure or aeration.
- **Pressure-Dependent Demand (PDD) Full Delivery Pressure**: `20.0 m`. Demanded flow is 100% fulfilled at or above this head.
- **PDD Minimum Pressure**: `0.0 m`. Below 0 m head, zero flow is delivered.
- **PDD Exponent**: `0.5` (standard orifice/Wagner relation).
- **Excess Pressure Burst Threshold**: `55.0 m` (~5.5 bar). Exceeding this pressure increases background pipe stress and leak rates.

---

## 4. Emergency Outage & Resilience Mode
- **Outage Window**: `14:00` to `18:00` (4 hours duration).
- **Target Inoperative Asset**: Primary intake pump `Pump 10`.
- **Designated Priority District**: `District 3 - Medina & Hospital` (critical hospital / central infrastructure zone).
- **Priority Minimum Pressure Requirement**: `18.0 m`.

---

## 5. Leak Severity Thresholds & Physical Modeling
Leaks are modeled as orifice discharge governed by Torricelli's law $Q_{leak} = C_d A \sqrt{2 g H}$:
- **Minor (Fissure / Joint Weep)**: Orifice area `0.0003 m²`, typical flow `< 10.0 m³/h`.
- **Moderate (Joint Shear / Large Crack)**: Orifice area `0.0012 m²`, typical flow `10.0 - 30.0 m³/h`.
- **Critical (Pipe Rupture / Main Burst)**: Orifice area `0.0035 m²`, typical flow `> 30.0 m³/h`.

---

## 6. Water Balance & Loss Benchmarks
- **Tunisia National Non-Revenue Water Range**: **25.0% to 50.0%** depending on region, aging network segments, and commercial meter slippage (always presented as a range, never a single statistic).
- **Japan Modern Dense Benchmark**: **3.0% to 7.0%** (dense sensor coverage, rapid acoustic localization, active pressure management).
- **District Unexplained Water Gap Threshold**: `12.0%`.
  *(Note: A water gap indicates an anomaly between inlet flow and billed consumption; it is not definitive proof of a physical crack, as meter inaccuracy and unauthorized use can also cause gaps).*

---

## 7. Sensor Topologies (Rich vs. Sparse)
- **Rich Mode (Dense Japanese Style)**:
  - `24` real-time telemetry pressure nodes across the network.
  - Full district inlet/outlet flow meters.
  - Additive Gaussian noise: Pressure $\sigma = 0.4\text{ m}$, Flow $\sigma = 0.002\text{ m}^3/\text{s}$.
- **Sparse Mode (Resource-Constrained Utility Style)**:
  - `6` active telemetry pressure nodes.
  - Only primary trunk transmission flow meter.
  - Sensor #2 exhibits simulated sensor failure (stuck or erratic reading).
