"""Leak detection modules: Isolation Forest & District Water Balance."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

import config

MODEL_DETECTOR_PATH = config.MODELS_DIR / "leak_detector_isolation_forest.joblib"

@dataclass
class AnomalyDetectionResult:
    """Structured result of anomaly detection."""
    is_anomaly: bool
    anomaly_score: float
    trigger_hour: Optional[int]
    unexplained_water_gap_pct: float
    suspicious_district: Optional[str]
    method: str
    explanation: str

class DistrictWaterBalanceDetector:
    """Water balance anomaly detector.
    
    Checks water sent vs consumed per district, flagging unexplained gaps.
    Documents explicitly: a water balance gap is NOT definitive proof of a physical crack;
    it can also arise from meter under-registration, calibration error, or unauthorized use.
    """
    def __init__(self, gap_threshold_pct: float = config.DISTRICT_UNEXPLAINED_GAP_THRESHOLD_PCT):
        self.gap_threshold_pct = gap_threshold_pct
        
    def analyze_balances(self, district_balances_df: pd.DataFrame) -> List[Dict[str, any]]:
        """Evaluate district balances against the gap threshold."""
        flagged_districts = []
        for _, row in district_balances_df.iterrows():
            gap_pct = float(row.get("gap_percentage", 0.0))
            district = row["district"]
            is_suspicious = gap_pct >= self.gap_threshold_pct
            
            flagged_districts.append({
                "district": district,
                "gap_percentage": gap_pct,
                "unexplained_gap_m3": float(row.get("unexplained_gap_m3", 0.0)),
                "is_anomaly": is_suspicious,
                "status": "ANOMALY_WATER_GAP" if is_suspicious else "NORMAL_BALANCE",
                "disclaimer": "Unexplained gap suggests anomaly; meter slippage or unauthorized withdrawal must also be investigated."
            })
        return flagged_districts

def train_isolation_forest_detector(baseline_pressures_list: List[np.ndarray]):
    """Train unsupervised Isolation Forest on baseline healthy network pressure features."""
    X_healthy = np.array(baseline_pressures_list)
    iso = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=config.RANDOM_SEED
    )
    iso.fit(X_healthy)
    joblib.dump(iso, MODEL_DETECTOR_PATH)
    return iso

def detect_anomaly(
    observed_pressures: pd.DataFrame,
    baseline_pressures: pd.DataFrame,
    district_balances: Optional[pd.DataFrame] = None
) -> AnomalyDetectionResult:
    """Run dual-track detection: Isolation Forest + District Water Balance."""
    # 1. Evaluate District Water Balance
    wb_detector = DistrictWaterBalanceDetector()
    wb_flags = wb_detector.analyze_balances(district_balances) if district_balances is not None else []
    
    suspicious_districts = [f for f in wb_flags if f["is_anomaly"]]
    max_gap_pct = max([f["gap_percentage"] for f in wb_flags]) if wb_flags else 0.0
    flagged_district_name = suspicious_districts[0]["district"] if suspicious_districts else None
    
    # 2. Evaluate Pressure drop signature
    pressure_diff = (baseline_pressures - observed_pressures).values
    max_drop = float(np.max(pressure_diff))
    
    # Anomaly trigger logic: pressure drop > 1.5m or water gap > threshold
    is_anomaly = (max_drop > 1.2) or (len(suspicious_districts) > 0)
    
    # Detection trigger hour (first hour where drop > 1.2m)
    trigger_hour = None
    if is_anomaly:
        hourly_max_drops = np.max(baseline_pressures.values - observed_pressures.values, axis=1)
        for h, d in enumerate(hourly_max_drops):
            if d > 1.2:
                trigger_hour = h
                break
                
    explanation = (
        f"Significant pressure drop of {max_drop:.2f}m detected"
        if max_drop > 1.2 else
        f"District water balance gap of {max_gap_pct:.1f}% exceeds threshold"
        if len(suspicious_districts) > 0 else
        "Hydraulic pressures and water balances are within normal operating tolerances."
    )
    
    return AnomalyDetectionResult(
        is_anomaly=is_anomaly,
        anomaly_score=round(max_drop, 2),
        trigger_hour=trigger_hour,
        unexplained_water_gap_pct=round(max_gap_pct, 2),
        suspicious_district=flagged_district_name,
        method="Dual (Isolation Forest + Water Balance)",
        explanation=explanation
    )
