"""HydroTwin Configuration and Assumptions.

All physical, economic, and simulation parameters are centralized here.
Every assumption is documented with units, rationale, and simulated context.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

# Base directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
DOCS_DIR = BASE_DIR / "docs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
DOCS_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------
# 1. Random Seeds & Reproducibility
# ---------------------------------------------------------
RANDOM_SEED: int = 42
SIMULATION_DURATION_HOURS: int = 24
TIMESTEP_SECONDS: int = 3600  # 1 hour steps

# ---------------------------------------------------------
# 2. Electricity Tariff Schedule (Calibrated on STEG industrial medium-voltage)
# ---------------------------------------------------------
# Time-of-use tariff in TND / kWh (Tunisian Dinar)
# Off-peak hours (Heures creuses): 22:00 - 06:00
# Day/Standard hours (Heures pleines): 06:00 - 18:00, 21:00 - 22:00
# Peak hours (Heures de pointe): 18:00 - 21:00 (summer high-load window)
TARIFF_OFF_PEAK_TND_PER_KWH: float = 0.210   # Off-peak (22h-06h)
TARIFF_DAY_TND_PER_KWH: float = 0.295        # Normal daytime
TARIFF_PEAK_TND_PER_KWH: float = 0.380       # Evening peak (18h-21h)

# Conversion / Reference in JPY (for bilateral hackathon context: ~48 JPY / TND)
TND_TO_JPY: float = 48.0

# ---------------------------------------------------------
# 3. Hydraulic Service Pressure Constraints (in meters of water head)
# ---------------------------------------------------------
# Minimum pressure required at any customer junction to maintain service
MIN_SERVICE_PRESSURE_M: float = 15.0  # ~1.5 bar (standard municipal distribution)
REQUIRED_PRESSURE_PDD_M: float = 20.0  # Pressure required for 100% demanded discharge
MINIMUM_PRESSURE_PDD_M: float = 0.0   # Below this, zero water can be withdrawn
PRESSURE_EXPONENT_PDD: float = 0.5    # Typical orifice / Wagner exponent

# Excess pressure penalty threshold (stressing aging pipes and accelerating bursts)
EXCESS_PRESSURE_THRESHOLD_M: float = 55.0  # > 5.5 bar increases leak rate and rupture risk

# ---------------------------------------------------------
# 4. Outage and Resilience Window
# ---------------------------------------------------------
# Emergency pump station power cut or grid shedding window
OUTAGE_START_HOUR: int = 14  # 14:00
OUTAGE_DURATION_HOURS: int = 4  # 14:00 to 18:00
OUTAGE_PUMP_ID: str = "10"    # Primary intake / transmission pump in Net3

# Priority zones that MUST maintain water service during grid crisis
PRIORITY_DISTRICTS: List[str] = ["District 3 - Medina & Hospital"]
PRIORITY_MIN_PRESSURE_M: float = 18.0  # Elevated minimum for critical infrastructure

# ---------------------------------------------------------
# 5. Leak Severity Thresholds & Modeling
# ---------------------------------------------------------
# Leak categories based on equivalent orifice area (m²) and estimated discharge (m³/h)
# Minor: Small fissure / packing leak (Area < 0.0005 m²; Flow < 10 m³/h)
# Moderate: Pipe joint shear or moderate crack (Area 0.0005 - 0.0020 m²; Flow 10 - 30 m³/h)
# Critical: Pipe burst / major rupture (Area > 0.0020 m²; Flow > 30 m³/h)
LEAK_AREA_MINOR_M2: float = 0.0003
LEAK_AREA_MODERATE_M2: float = 0.0012
LEAK_AREA_CRITICAL_M2: float = 0.0035

LEAK_SEVERITY_THRESHOLDS = {
    "minor": {"max_flow_m3h": 10.0, "area_m2": LEAK_AREA_MINOR_M2, "label": "Minor (Fissure)"},
    "moderate": {"max_flow_m3h": 30.0, "area_m2": LEAK_AREA_MODERATE_M2, "label": "Moderate (Joint failure)"},
    "critical": {"max_flow_m3h": 999.0, "area_m2": LEAK_AREA_CRITICAL_M2, "label": "Critical (Burst)"},
}

# ---------------------------------------------------------
# 6. Water Balance & NRW Benchmarks (Non-Revenue Water)
# ---------------------------------------------------------
# Note: Always reported as a realistic range for Tunisia, never a single number
TUNISIA_LOSS_RANGE_PCT: Tuple[float, float] = (25.0, 50.0)
JAPAN_LOSS_BENCHMARK_PCT: Tuple[float, float] = (3.0, 7.0)

# Unexplained water balance gap threshold for district anomaly detection
DISTRICT_UNEXPLAINED_GAP_THRESHOLD_PCT: float = 12.0

# ---------------------------------------------------------
# 7. Sensor Instrumentation Configurations
# ---------------------------------------------------------
# Rich Mode: High-density Japanese-style instrumentation (dense pressure + district flow meters)
# Sparse Mode: Emerging / resource-constrained setting (sparse telemetry, 1 faulty sensor)
RICH_PRESSURE_SENSOR_COUNT: int = 24
SPARSE_PRESSURE_SENSOR_COUNT: int = 6
SPARSE_FAILED_SENSOR_INDEX: int = 2  # One sensor transmits frozen or noisy garbage

SENSOR_NOISE_PRESSURE_STD_M: float = 0.4  # ±0.4m pressure measurement noise (~0.04 bar)
SENSOR_NOISE_FLOW_STD_M3S: float = 0.002  # ±2 L/s flow measurement noise

# ---------------------------------------------------------
# 8. District Partitioning for Net3
# ---------------------------------------------------------
# Net3 nodes grouped into 5 realistic municipal districts
# Coordinates in Net3 range from (0,0) to (100, 100) approx.
DISTRICT_NAMES: List[str] = [
    "District 1 - Centre-Ville",
    "District 2 - El Menzah",
    "District 3 - Medina & Hospital",
    "District 4 - Les Berges du Lac",
    "District 5 - Ennasr Plateau"
]

# ---------------------------------------------------------
# 9. UI & Mandatory Disclaimers
# ---------------------------------------------------------
DISCLAIMER_BANNER: str = (
    "SIMULATED DATA - NOT SONEDE OR OPERATOR DATA. "
    "Calibrated on published engineering and academic figures for demonstration purposes only."
)
HONESTY_BANNER_TEXT: str = DISCLAIMER_BANNER

DECISION_RULE_TEXT: str = (
    "The system ADVISES, humans DECIDE. "
    "No autonomous pump or valve control is performed. Recommendations require operator sign-off."
)
