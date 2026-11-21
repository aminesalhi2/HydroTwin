"""Synthetic district demand generator and ML forecasting models.

All data is strictly synthetic and labeled as such.
Uses time-based train/test splitting and calculates MAE, MAPE, and prediction intervals.
"""

from pathlib import Path
from typing import Dict, Tuple, Optional
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error

import config

SYNTHETIC_DATA_PATH = config.DATA_DIR / "synthetic_demand_dataset.csv"
MODEL_RF_PATH = config.MODELS_DIR / "demand_forecast_rf.joblib"
MODEL_GB_PATH = config.MODELS_DIR / "demand_forecast_gb.joblib"

# Approximate representative population per district (Tunis metropolitan scale)
DISTRICT_POPULATION = {
    "District 1 - Centre-Ville": 65000,
    "District 2 - El Menzah": 85000,
    "District 3 - Medina & Hospital": 95000,
    "District 4 - Les Berges du Lac": 45000,
    "District 5 - Ennasr Plateau": 70000,
}

# Diurnal pattern multipliers per time of day
TIME_OF_DAY_MULTIPLIER = {
    "night": 0.45,       # 00:00 - 06:00
    "morning": 1.35,     # 06:00 - 12:00 (morning peak)
    "afternoon": 0.95,   # 12:00 - 18:00
    "evening": 1.25,     # 18:00 - 24:00 (evening peak)
}

SEASON_TEMP_RANGE = {
    "Winter": (8.0, 16.0),
    "Spring": (15.0, 24.0),
    "Summer": (26.0, 42.0),
    "Autumn": (18.0, 28.0),
}

SEASON_MULTIPLIER = {
    "Winter": 0.85,
    "Spring": 1.00,
    "Summer": 1.35,   # Summer peak water demand in Tunisia
    "Autumn": 0.95,
}

def get_time_of_day(hour: int) -> str:
    """Classify hour into night/morning/afternoon/evening."""
    if 0 <= hour < 6:
        return "night"
    elif 6 <= hour < 12:
        return "morning"
    elif 12 <= hour < 18:
        return "afternoon"
    else:
        return "evening"

def generate_synthetic_demand_dataset(
    days: int = 90,
    seed: int = config.RANDOM_SEED
) -> pd.DataFrame:
    """Generate a chronological multi-district synthetic demand dataset.
    
    Variables:
      - timestamp, district, temperature, season, month, weekday, hour,
        time_of_day, population, past_demand_1h, past_demand_24h,
        demand_target_m3h, is_synthetic_flag
    """
    np.random.seed(seed)
    records = []
    
    start_date = pd.Timestamp("2024-05-01 00:00:00")
    total_hours = days * 24
    
    # Base per-capita baseline in m3/person/hour (~150 L/capita/day)
    base_per_capita = 0.150 / 24.0
    
    for district, pop in DISTRICT_POPULATION.items():
        base_district_flow = pop * base_per_capita # m3/h
        
        # State tracking for past demand
        history = []
        
        for h in range(total_hours):
            current_time = start_date + pd.Timedelta(hours=h)
            hour = current_time.hour
            weekday = current_time.weekday()
            month = current_time.month
            
            # Determine season
            if month in [12, 1, 2]:
                season = "Winter"
            elif month in [3, 4, 5]:
                season = "Spring"
            elif month in [6, 7, 8]:
                season = "Summer"
            else:
                season = "Autumn"
                
            # Synthetic temperature with diurnal sine wave + random weather noise
            temp_min, temp_max = SEASON_TEMP_RANGE[season]
            diurnal_temp = np.sin((hour - 9) / 24.0 * 2 * np.pi) # peak at ~15:00
            temperature = ((temp_min + temp_max) / 2.0) + ((temp_max - temp_min) / 2.0) * diurnal_temp + np.random.normal(0, 1.2)
            
            time_of_day = get_time_of_day(hour)
            tod_mult = TIME_OF_DAY_MULTIPLIER[time_of_day]
            season_mult = SEASON_MULTIPLIER[season]
            weekend_mult = 1.08 if weekday in [5, 6] else 1.0 # slightly higher weekend demand
            
            # Heatwave surge: extra demand above 30°C
            heat_surge = max(0.0, (temperature - 28.0) * 0.015)
            
            # Calculate target demand with Gaussian noise
            demand_m3h = base_district_flow * tod_mult * season_mult * weekend_mult * (1.0 + heat_surge)
            demand_m3h += np.random.normal(0, base_district_flow * 0.04)
            demand_m3h = max(10.0, demand_m3h)
            
            # Lags
            past_1h = history[-1] if len(history) >= 1 else demand_m3h * 0.98
            past_24h = history[-24] if len(history) >= 24 else demand_m3h * 1.02
            history.append(demand_m3h)
            
            records.append({
                "timestamp": current_time,
                "district": district,
                "population": pop,
                "season": season,
                "month": month,
                "weekday": weekday,
                "hour": hour,
                "time_of_day": time_of_day,
                "temperature_c": round(temperature, 1),
                "past_demand_1h": round(past_1h, 2),
                "past_demand_24h": round(past_24h, 2),
                "demand_target_m3h": round(demand_m3h, 2),
                "data_nature": "SYNTHETIC_SIMULATED",
            })
            
    df = pd.DataFrame(records)
    df = df.sort_values(by=["timestamp", "district"]).reset_index(drop=True)
    df.to_csv(SYNTHETIC_DATA_PATH, index=False)
    return df

def prepare_feature_matrix(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """Encode categorical features and prepare design matrix X, y."""
    features = [
        "population", "month", "weekday", "hour", "temperature_c",
        "past_demand_1h", "past_demand_24h"
    ]
    # One-hot encode district, season, time_of_day
    df_encoded = pd.get_dummies(df[features + ["district", "season", "time_of_day"]], drop_first=False)
    target = df["demand_target_m3h"]
    return df_encoded, target

def train_demand_forecast_model() -> Dict[str, any]:
    """Train Random Forest and Gradient Boosting models using a TIME-BASED split.
    
    Evaluates MAE, MAPE, and calculates 90% prediction intervals based on residuals.
    Saves models to models/ directory.
    """
    if not SYNTHETIC_DATA_PATH.exists():
        df = generate_synthetic_demand_dataset()
    else:
        df = pd.read_csv(SYNTHETIC_DATA_PATH, parse_dates=["timestamp"])
        
    X, y = prepare_feature_matrix(df)
    
    # TIME-BASED split: 80% train (chronologically early), 20% test (chronologically late)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    # 1. Random Forest Regressor (Baseline)
    rf = RandomForestRegressor(
        n_estimators=100,
        max_depth=14,
        random_state=config.RANDOM_SEED,
        n_jobs=-1
    )
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    mae_rf = float(mean_absolute_error(y_test, y_pred_rf))
    mape_rf = float(mean_absolute_percentage_error(y_test, y_pred_rf))
    
    # Residual-based 90% prediction interval half-width: 90th percentile of absolute residuals
    residuals_rf = np.abs(y_test - y_pred_rf)
    interval_half_width_90 = float(np.percentile(residuals_rf, 90))
    
    # 2. Gradient Boosting Regressor (Alternative comparator)
    gb = GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.08,
        max_depth=6,
        random_state=config.RANDOM_SEED
    )
    gb.fit(X_train, y_train)
    y_pred_gb = gb.predict(X_test)
    mae_gb = float(mean_absolute_error(y_test, y_pred_gb))
    mape_gb = float(mean_absolute_percentage_error(y_test, y_pred_gb))
    
    # Save artifacts
    feature_columns = list(X.columns)
    model_payload_rf = {
        "model": rf,
        "feature_columns": feature_columns,
        "mae": mae_rf,
        "mape": mape_rf,
        "interval_90_m3h": interval_half_width_90,
        "training_nature": "SYNTHETIC_DATA_TIME_SPLIT"
    }
    model_payload_gb = {
        "model": gb,
        "feature_columns": feature_columns,
        "mae": mae_gb,
        "mape": mape_gb,
        "training_nature": "SYNTHETIC_DATA_TIME_SPLIT"
    }
    
    joblib.dump(model_payload_rf, MODEL_RF_PATH)
    joblib.dump(model_payload_gb, MODEL_GB_PATH)
    
    return {
        "mae_rf": mae_rf,
        "mape_rf": mape_rf,
        "interval_90_m3h": interval_half_width_90,
        "mae_gb": mae_gb,
        "mape_gb": mape_gb,
        "test_samples": len(y_test),
        "train_samples": len(y_train),
    }

def predict_district_demand(
    district: str,
    season: str,
    time_of_day: str,
    hour: int = 12,
    temperature_c: Optional[float] = None
) -> Tuple[float, float, float]:
    """Predict demand (m3/h) for a district with lower and upper 90% prediction intervals.
    
    Returns: (forecast_mean, lower_bound, upper_bound)
    """
    if not MODEL_RF_PATH.exists():
        train_demand_forecast_model()
        
    payload = joblib.load(MODEL_RF_PATH)
    model = payload["model"]
    feature_columns = payload["feature_columns"]
    interval_hw = payload["interval_90_m3h"]
    
    pop = DISTRICT_POPULATION.get(district, 60000)
    month = 7 if season == "Summer" else 1 if season == "Winter" else 4 if season == "Spring" else 10
    weekday = 2 # Wednesday
    
    if temperature_c is None:
        temp_min, temp_max = SEASON_TEMP_RANGE[season]
        temperature_c = (temp_min + temp_max) / 2.0
        
    base_flow = pop * (0.150 / 24.0) * TIME_OF_DAY_MULTIPLIER[time_of_day] * SEASON_MULTIPLIER[season]
    past_1h = base_flow * 0.98
    past_24h = base_flow * 1.01
    
    # Construct feature row
    row_dict = {col: 0 for col in feature_columns}
    row_dict["population"] = pop
    row_dict["month"] = month
    row_dict["weekday"] = weekday
    row_dict["hour"] = hour
    row_dict["temperature_c"] = temperature_c
    row_dict["past_demand_1h"] = past_1h
    row_dict["past_demand_24h"] = past_24h
    
    if f"district_{district}" in row_dict:
        row_dict[f"district_{district}"] = 1
    if f"season_{season}" in row_dict:
        row_dict[f"season_{season}"] = 1
    if f"time_of_day_{time_of_day}" in row_dict:
        row_dict[f"time_of_day_{time_of_day}"] = 1
        
    X_input = pd.DataFrame([row_dict])[feature_columns]
    pred = float(model.predict(X_input)[0])
    lower = max(0.0, pred - interval_hw)
    upper = pred + interval_hw
    
    return pred, lower, upper
