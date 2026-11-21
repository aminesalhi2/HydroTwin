"""Tests for Phase 2: Demand generation and time-based forecasting."""

from pathlib import Path
import pytest
import config
from ml.demand_forecasting import (
    generate_synthetic_demand_dataset,
    train_demand_forecast_model,
    predict_district_demand,
    SYNTHETIC_DATA_PATH,
    MODEL_RF_PATH,
    MODEL_GB_PATH,
)

def test_generate_synthetic_demand():
    df = generate_synthetic_demand_dataset(days=15)
    assert len(df) == 15 * 24 * 5
    assert "demand_target_m3h" in df.columns
    assert "data_nature" in df.columns
    assert (df["data_nature"] == "SYNTHETIC_SIMULATED").all()
    assert (df["demand_target_m3h"] > 0).all()
    assert set(df["district"].unique()) == set(config.DISTRICT_NAMES)
    assert SYNTHETIC_DATA_PATH.exists()

def test_train_demand_models():
    metrics = train_demand_forecast_model()
    assert "mae_rf" in metrics
    assert "mape_rf" in metrics
    assert "interval_90_m3h" in metrics
    assert "mae_gb" in metrics
    assert "mape_gb" in metrics
    
    # Models must achieve solid fit on synthetic data
    assert metrics["mape_rf"] < 0.15, f"MAPE too high: {metrics['mape_rf']}"
    assert metrics["mape_gb"] < 0.15, f"MAPE too high: {metrics['mape_gb']}"
    assert metrics["interval_90_m3h"] > 0
    assert MODEL_RF_PATH.exists()
    assert MODEL_GB_PATH.exists()

def test_predict_district_demand_intervals():
    district = config.DISTRICT_NAMES[0]
    mean_val, lower, upper = predict_district_demand(
        district=district,
        season="Summer",
        time_of_day="morning",
        hour=9
    )
    assert mean_val > 0
    assert lower <= mean_val <= upper
    assert upper - lower > 0
