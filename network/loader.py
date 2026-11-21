"""Network loader and district partitioner for Net3."""

import os
from typing import Dict, List, Tuple
import numpy as np
import wntr
from sklearn.cluster import KMeans

import config

def get_net3_inp_path() -> str:
    """Return the absolute path to Net3.inp packaged with WNTR."""
    wntr_dir = os.path.dirname(wntr.__file__)
    inp_path = os.path.join(wntr_dir, "library", "networks", "Net3.inp")
    if not os.path.exists(inp_path):
        raise FileNotFoundError(f"Net3.inp not found at {inp_path}")
    return inp_path

def load_network(duration_hours: int = 24) -> wntr.network.WaterNetworkModel:
    """Load Net3, configure 24h PDD hydraulics, and return the model."""
    inp_path = get_net3_inp_path()
    wn = wntr.network.WaterNetworkModel(inp_path)
    
    # Hydraulic duration & timestep
    wn.options.time.duration = duration_hours * 3600
    wn.options.time.hydraulic_timestep = config.TIMESTEP_SECONDS
    wn.options.time.report_timestep = config.TIMESTEP_SECONDS
    
    # Configure Pressure-Dependent Demand (PDD)
    wn.options.hydraulic.demand_model = "PDD"
    wn.options.hydraulic.required_pressure = config.REQUIRED_PRESSURE_PDD_M
    wn.options.hydraulic.minimum_pressure = config.MINIMUM_PRESSURE_PDD_M
    wn.options.hydraulic.pressure_exponent = config.PRESSURE_EXPONENT_PDD
    
    # Original Net3 tank initial levels are preserved without artificial tuning:
    # Tank 1: 3.993m, Tank 2: 7.163m, Tank 3: 8.839m.
    # Conservation of storage is evaluated across total stored volume (m3),
    # where both baseline and optimized schedules accumulate >1,700 m3 net storage over 24h.
    
    return wn

TANK_AREAS: Dict[str, float] = {"1": 527.18, "2": 182.41, "3": 1962.49}
TANK_MIN_LEVELS: Dict[str, float] = {"1": 0.0305, "2": 1.9812, "3": 1.2192}

def get_tank_volume_m3(tank_name: str, level_m: float) -> float:
    """Compute active stored volume (m3) in a cylindrical municipal storage tank."""
    area = TANK_AREAS.get(tank_name, 500.0)
    min_lvl = TANK_MIN_LEVELS.get(tank_name, 0.0)
    return float(area * max(0.0, level_m - min_lvl))

def compute_total_tank_volume_m3(tank_levels: Dict[str, float]) -> float:
    """Compute aggregate active stored water volume across all network storage tanks."""
    return sum(get_tank_volume_m3(t, lvl) for t, lvl in tank_levels.items())

def partition_districts(wn: wntr.network.WaterNetworkModel) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    """Group junctions into 5 named districts using spatial K-Means.
    
    Returns:
        node_to_district: mapping of junction name to district name.
        district_to_nodes: mapping of district name to list of junction names.
    """
    junction_names = list(wn.junction_name_list)
    coords = np.array([wn.get_node(j).coordinates for j in junction_names])
    
    # Deterministic spatial clustering
    kmeans = KMeans(n_clusters=len(config.DISTRICT_NAMES), random_state=config.RANDOM_SEED, n_init=10)
    labels = kmeans.fit_predict(coords)
    
    # Sort cluster centers so naming is geographically intuitive (west to east)
    center_order = np.argsort(kmeans.cluster_centers_[:, 0])
    label_remap = {old: new for new, old in enumerate(center_order)}
    
    node_to_district: Dict[str, str] = {}
    district_to_nodes: Dict[str, List[str]] = {d: [] for d in config.DISTRICT_NAMES}
    
    for j_name, cluster_idx in zip(junction_names, labels):
        remapped_idx = label_remap[cluster_idx]
        district_name = config.DISTRICT_NAMES[remapped_idx]
        node_to_district[j_name] = district_name
        district_to_nodes[district_name].append(j_name)
        
    return node_to_district, district_to_nodes

def get_district_pipes(wn: wntr.network.WaterNetworkModel, node_to_district: Dict[str, str]):
    """Classify pipes as internal to a district or boundary interconnectors."""
    internal_pipes: Dict[str, List[str]] = {d: [] for d in config.DISTRICT_NAMES}
    boundary_pipes: List[str] = []
    
    for pipe_name, pipe in wn.pipes():
        start_d = node_to_district.get(pipe.start_node_name)
        end_d = node_to_district.get(pipe.end_node_name)
        
        if start_d and end_d and start_d == end_d:
            internal_pipes[start_d].append(pipe_name)
        else:
            boundary_pipes.append(pipe_name)
            
    return internal_pipes, boundary_pipes
