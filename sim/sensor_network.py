"""Sensor network telemetry models: Rich (Dense) vs Sparse instrumentations."""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
import wntr

import config
from network.loader import partition_districts

_CACHED_LAYOUT = None

def get_sensor_layout(wn: wntr.network.WaterNetworkModel = None) -> Tuple[List[str], List[str]]:
    """Determine fixed pressure sensor sets for Rich (24) and Sparse (6) topologies."""
    global _CACHED_LAYOUT
    if _CACHED_LAYOUT is not None:
        return _CACHED_LAYOUT

    if wn is None:
        from network.loader import load_network
        wn = load_network(24)

    node_to_district, district_to_nodes = partition_districts(wn)
    
    rich_sensors: List[str] = []
    sparse_sensors: List[str] = []
    
    # Stratified selection across each of the 5 districts
    for d_name in config.DISTRICT_NAMES:
        nodes = sorted(district_to_nodes[d_name])
        # Pick 4-5 nodes per district for rich mode
        step = max(1, len(nodes) // 5)
        d_rich = nodes[::step][:5]
        rich_sensors.extend(d_rich)
        # Pick 1 central node per district for sparse mode
        if nodes:
            sparse_sensors.append(nodes[len(nodes) // 2])
            
    # Pad or trim to exact counts
    junctions = sorted(list(wn.junction_name_list))
    for j in junctions:
        if len(rich_sensors) >= config.RICH_PRESSURE_SENSOR_COUNT:
            break
        if j not in rich_sensors:
            rich_sensors.append(j)
            
    if len(sparse_sensors) < config.SPARSE_PRESSURE_SENSOR_COUNT:
        for j in junctions:
            if len(sparse_sensors) >= config.SPARSE_PRESSURE_SENSOR_COUNT:
                break
            if j not in sparse_sensors:
                sparse_sensors.append(j)
                
    _CACHED_LAYOUT = (rich_sensors[:config.RICH_PRESSURE_SENSOR_COUNT], sparse_sensors[:config.SPARSE_PRESSURE_SENSOR_COUNT])
    return _CACHED_LAYOUT

def sample_sensor_telemetry(
    pressures_df: pd.DataFrame,
    flowrates_df: pd.DataFrame,
    mode: str = "rich",
    add_noise: bool = True,
    seed: int = config.RANDOM_SEED
) -> Dict[str, pd.DataFrame]:
    """Sample telemetry data under Rich or Sparse sensor modes with measurement noise.
    
    In Sparse mode, sensor #SPARSE_FAILED_SENSOR_INDEX exhibits sensor failure.
    """
    rng = np.random.RandomState(seed)
    
    # Deterministic distributed sensors (cached layout)
    rich_sensors, sparse_sensors = get_sensor_layout()
    
    selected_sensors = rich_sensors if mode == "rich" else sparse_sensors
    available = [s for s in selected_sensors if s in pressures_df.columns]
    p_readings = pressures_df[available].copy()
        
    if add_noise:
        noise = rng.normal(0, config.SENSOR_NOISE_PRESSURE_STD_M, size=p_readings.shape)
        p_readings += noise
        
    # Simulate failed sensor in sparse mode
    if mode == "sparse" and len(available) > config.SPARSE_FAILED_SENSOR_INDEX:
        failed_col = available[config.SPARSE_FAILED_SENSOR_INDEX]
        # Stuck reading with high drift noise
        p_readings[failed_col] = float(pressures_df[failed_col].iloc[0]) + rng.normal(0, 5.0, size=len(p_readings))

    # Flow meters
    if mode == "rich":
        flow_readings = flowrates_df.copy()
    else:
        # Only trunk pipe flowmeter (first pump or main transmission link)
        trunk_pipes = [c for c in flowrates_df.columns if c in ["10", "335", "111"]]
        flow_readings = flowrates_df[trunk_pipes].copy() if trunk_pipes else flowrates_df.iloc[:, :1].copy()

    if add_noise:
        flow_noise = rng.normal(0, config.SENSOR_NOISE_FLOW_STD_M3S, size=flow_readings.shape)
        flow_readings += flow_noise

    return {
        "pressure": p_readings,
        "flow": flow_readings,
        "mode": mode,
        "sensors_count": len(available),
        "is_simulated_telemetry": True
    }
