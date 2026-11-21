# HydroTwin: Assumptions, Verification Status & Sources

> **MANDATORY NOTICE**: All data utilized and displayed within HydroTwin is **100% simulated**. It does **not** represent proprietary operational telemetry from the Société Nationale d'Exploitation et de Distribution des Eaux (SONEDE), the Tunisian Ministry of Agriculture, or any specific Japanese water bureau.

This document transparently distinguishes between **Verified Empirical Sources** (used to calibrate simulated orders of magnitude) and **Unverified / Assumed Parameters** (engineering approximations).

---

## 1. Verified Sources & Calibration Anchors

| Item / Domain | Published Reference / Source | Calibration in HydroTwin | Notes & Verification Status |
|---|---|---|---|
| **Tunisian Water Losses (NRW)** | *L'Economiste Maghrébin*, CESE, Ministry of Agriculture Reports | Modeled as a range: **25% to 50%** across municipal sectors | **VERIFIED RANGE**. Losses vary widely between older urban cores (Medina/Centre-Ville: 40-50%) and newer developments (~25-30%). Never cited as a single static figure. |
| **SONEDE Pumping & Outages** | *AllAfrica*, SONEDE Annual Press Releases, *Webdo Tunisie* | 4-hour scheduled daytime/evening cuts during peak summer stress (14:00 - 18:00) | **VERIFIED PHENOMENON**. Recurrent pressure deficits in Grand Tunis and Sfax during high-temperature spells due to grid load shedding and reservoir depletion. |
| **Sfax & Coastal Pressure Deficits** | *Webdo*, Local Municipal Reports | Minimum delivery threshold of 15 m head (1.5 bar) | **VERIFIED REGULATORY NORM**. Pressure often dips below 1 bar in multi-story residential neighborhoods during peak draw. |
| **Japan Pipe Aging & Renewal Rates** | Japan Ministry of Health, Labour and Welfare (MHLW / Ministry of Land, Infrastructure, Transport and Tourism), *Japan Water Works Association (JWWA)* | Aging pipe index, low physical leakage benchmark (3% - 7%) | **VERIFIED BENCHMARK**. Japanese municipal utilities achieve world-leading low leakage through systematic night acoustic surveys and high-density telemetry, despite aging ductile cast iron backbones. |
| **JICA-SONEDE Cooperation** | JICA Official Project Evaluation Reports (Greater Tunis water supply, Sfax desalination & efficiency enhancement) | Advisory bilateral twin structure, emphasis on energy efficiency and non-revenue water reduction | **VERIFIED INSTITUTIONAL RECORD**. JICA has co-financed water treatment, pipe rehabilitation, and capacity-building programs across Tunisia since the 1990s. |
| **STEG Electricity Tariffs** | Société Tunisienne de l'Electricité et du Gaz (STEG) Medium-Voltage TOU Schedule | Off-peak: 0.210 TND/kWh, Standard: 0.295 TND/kWh, Peak: 0.380 TND/kWh | **VERIFIED TARIFF STRUCTURE**. Reflects published 2023/2024 industrial medium-voltage multi-tier tariffs. |

---

## 2. Unverified, Estimated, or Synthetic Items (Marked Transparently)

| Item / Domain | Assumption Made in HydroTwin | Rationale & Disclaimer |
|---|---|---|
| **Real SONEDE Network Geometries** | Net3 standard benchmark topology (from EPANET / WNTR) mapped onto Tunis district names | **SYNTHETIC / UNVERIFIED**. Real municipal GIS pipe geometries and valve states are critical national infrastructure and are not publicly released. |
| **Japanese Water Utility Electricity Budgets** | Representative pumping power calculations based on physical head loss and flow | **ESTIMATED SIMULATION**. Real operational OPEX accounts vary across municipal prefectures (Nagoya, Tokyo, Osaka). |
| **Public Leak Challenge Datasets (BattLeDIM, LeakDB)** | Synthesized pressure-drop signatures inspired by BattLeDIM competition scenarios | **SYNTHETIC CALIBRATION**. Scenarios are programmatically generated using WNTR's pressure-dependent demand simulator with fixed random seed. |
| **Exact Hardware / Metering Costs** | Sensor telemetry costs are not claimed | **EXCLUDED**. Focus is purely on hydraulic efficiency and algorithmic detection. |

---

## 3. Core Advisory Guardrails
1. **Advisory Stance**: HydroTwin produces prioritized operator advisories, ranked inspection work orders, and suggested pumping schedules. It **never issues direct automated SCADA control signals**.
2. **Water Gap Nuance**: Water balance discrepancies between district inlets and billed meters reflect the sum of physical leakage, meter under-registration (aging mechanical meters), and unauthorized consumption. HydroTwin presents discrepancies as *anomalies requiring field verification*, never as proven physical cracks.
