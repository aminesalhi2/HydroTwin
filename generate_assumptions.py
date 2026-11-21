"""Generate docs/ASSUMPTIONS.md automatically from config.py."""

from pathlib import Path
import config

def generate_assumptions_doc():
    doc = f"""# HydroTwin: Physical, Economic & Simulation Assumptions

> **MANDATORY NOTICE**: {config.DISCLAIMER_BANNER}
>
> **OPERATIONAL PRINCIPLE**: {config.DECISION_RULE_TEXT}

This document details all parameters, operational thresholds, and domain assumptions encoded in `config.py`.

---

## 1. Random Seeds and Temporal Resolution
- **Random Seed**: `{config.RANDOM_SEED}` (strictly enforced across all synthetic generation, noise models, and train/test splits for full reproducibility).
- **Simulation Duration**: `{config.SIMULATION_DURATION_HOURS} hours` (24-hour diurnal operational cycle).
- **Hydraulic Timestep**: `{config.TIMESTEP_SECONDS // 3600} hour` ({config.TIMESTEP_SECONDS} seconds).

---

## 2. Electricity Tariff Structure (Tunisia STEG Calibration)
Calibrated on the Tunisian National Electricity and Gas Company (STEG) Medium-Voltage Industrial Time-of-Use schedule:
- **Off-Peak Tariff (22:00 - 06:00)**: `{config.TARIFF_OFF_PEAK_TND_PER_KWH:.3f} TND/kWh` (~{config.TARIFF_OFF_PEAK_TND_PER_KWH * config.TND_TO_JPY:.1f} JPY/kWh)
- **Day/Standard Tariff (06:00 - 18:00, 21:00 - 22:00)**: `{config.TARIFF_DAY_TND_PER_KWH:.3f} TND/kWh` (~{config.TARIFF_DAY_TND_PER_KWH * config.TND_TO_JPY:.1f} JPY/kWh)
- **Peak Evening Tariff (18:00 - 21:00)**: `{config.TARIFF_PEAK_TND_PER_KWH:.3f} TND/kWh` (~{config.TARIFF_PEAK_TND_PER_KWH * config.TND_TO_JPY:.1f} JPY/kWh)
- **Currency Conversion Reference**: `1 TND ≈ {config.TND_TO_JPY} JPY`.

---

## 3. Hydraulic Service Constraints
- **Minimum Service Pressure**: `{config.MIN_SERVICE_PRESSURE_M} m` (~1.5 bar). Below this threshold, consumer taps suffer low pressure or aeration.
- **Pressure-Dependent Demand (PDD) Full Delivery Pressure**: `{config.REQUIRED_PRESSURE_PDD_M} m`. Demanded flow is 100% fulfilled at or above this head.
- **PDD Minimum Pressure**: `{config.MINIMUM_PRESSURE_PDD_M} m`. Below 0 m head, zero flow is delivered.
- **PDD Exponent**: `{config.PRESSURE_EXPONENT_PDD}` (standard orifice/Wagner relation).
- **Excess Pressure Burst Threshold**: `{config.EXCESS_PRESSURE_THRESHOLD_M} m` (~5.5 bar). Exceeding this pressure increases background pipe stress and leak rates.

---

## 4. Emergency Outage & Resilience Mode
- **Outage Window**: `{config.OUTAGE_START_HOUR}:00` to `{config.OUTAGE_START_HOUR + config.OUTAGE_DURATION_HOURS}:00` ({config.OUTAGE_DURATION_HOURS} hours duration).
- **Target Inoperative Asset**: Primary intake pump `Pump {config.OUTAGE_PUMP_ID}`.
- **Designated Priority District**: `{config.PRIORITY_DISTRICTS[0]}` (critical hospital / central infrastructure zone).
- **Priority Minimum Pressure Requirement**: `{config.PRIORITY_MIN_PRESSURE_M} m`.

---

## 5. Leak Severity Thresholds & Physical Modeling
Leaks are modeled as orifice discharge governed by Torricelli's law $Q_{{leak}} = C_d A \sqrt{{2 g H}}$:
- **Minor (Fissure / Joint Weep)**: Orifice area `{config.LEAK_AREA_MINOR_M2} m²`, typical flow `< {config.LEAK_SEVERITY_THRESHOLDS['minor']['max_flow_m3h']} m³/h`.
- **Moderate (Joint Shear / Large Crack)**: Orifice area `{config.LEAK_AREA_MODERATE_M2} m²`, typical flow `{config.LEAK_SEVERITY_THRESHOLDS['minor']['max_flow_m3h']} - {config.LEAK_SEVERITY_THRESHOLDS['moderate']['max_flow_m3h']} m³/h`.
- **Critical (Pipe Rupture / Main Burst)**: Orifice area `{config.LEAK_AREA_CRITICAL_M2} m²`, typical flow `> {config.LEAK_SEVERITY_THRESHOLDS['moderate']['max_flow_m3h']} m³/h`.

---

## 6. Water Balance & Loss Benchmarks
- **Tunisia National Non-Revenue Water Range**: **{config.TUNISIA_LOSS_RANGE_PCT[0]}% to {config.TUNISIA_LOSS_RANGE_PCT[1]}%** depending on region, aging network segments, and commercial meter slippage (always presented as a range, never a single statistic).
- **Japan Modern Dense Benchmark**: **{config.JAPAN_LOSS_BENCHMARK_PCT[0]}% to {config.JAPAN_LOSS_BENCHMARK_PCT[1]}%** (dense sensor coverage, rapid acoustic localization, active pressure management).
- **District Unexplained Water Gap Threshold**: `{config.DISTRICT_UNEXPLAINED_GAP_THRESHOLD_PCT}%`.
  *(Note: A water gap indicates an anomaly between inlet flow and billed consumption; it is not definitive proof of a physical crack, as meter inaccuracy and unauthorized use can also cause gaps).*

---

## 7. Sensor Topologies (Rich vs. Sparse)
- **Rich Mode (Dense Japanese Style)**:
  - `{config.RICH_PRESSURE_SENSOR_COUNT}` real-time telemetry pressure nodes across the network.
  - Full district inlet/outlet flow meters.
  - Additive Gaussian noise: Pressure $\\sigma = {config.SENSOR_NOISE_PRESSURE_STD_M}\\text{{ m}}$, Flow $\\sigma = {config.SENSOR_NOISE_FLOW_STD_M3S}\\text{{ m}}^3/\\text{{s}}$.
- **Sparse Mode (Resource-Constrained Utility Style)**:
  - `{config.SPARSE_PRESSURE_SENSOR_COUNT}` active telemetry pressure nodes.
  - Only primary trunk transmission flow meter.
  - Sensor #{config.SPARSE_FAILED_SENSOR_INDEX} exhibits simulated sensor failure (stuck or erratic reading).
"""
    output_path = Path(config.DOCS_DIR) / "ASSUMPTIONS.md"
    output_path.write_text(doc, encoding="utf-8")
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_assumptions_doc()
