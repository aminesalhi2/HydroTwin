"""Leak injection utilities using WNTR physical leak modeling."""

from typing import Optional, Tuple
import wntr
from wntr.morph import split_pipe

import config

def inject_node_leak(
    wn: wntr.network.WaterNetworkModel,
    node_name: str,
    area_m2: float = config.LEAK_AREA_MODERATE_M2,
    start_hour: int = 2,
    duration_hours: int = 20
) -> wntr.network.WaterNetworkModel:
    """Inject a pressure-dependent orifice leak at a specific junction node."""
    if node_name not in wn.junction_name_list:
        raise ValueError(f"Junction '{node_name}' not found in network.")
        
    junction = wn.get_node(node_name)
    start_sec = start_hour * 3600
    end_sec = (start_hour + duration_hours) * 3600
    junction.add_leak(wn, area=area_m2, start_time=start_sec, end_time=end_sec)
    return wn

def inject_pipe_leak(
    wn: wntr.network.WaterNetworkModel,
    pipe_name: str,
    area_m2: float = config.LEAK_AREA_MODERATE_M2,
    start_hour: int = 2,
    duration_hours: int = 20
) -> Tuple[wntr.network.WaterNetworkModel, str]:
    """Inject a leak along a pipe by splitting it with an intermediate junction.
    
    Returns: (modified_wn, leak_junction_name)
    """
    if pipe_name not in wn.pipe_name_list:
        raise ValueError(f"Pipe '{pipe_name}' not found in network.")
        
    leak_junction_name = f"leak_node_{pipe_name}"
    new_pipe_name = f"pipe_split_{pipe_name}"
    
    # Split pipe at midpoint (WNTR returns a modified copy by default)
    wn = split_pipe(
        wn=wn,
        pipe_name_to_split=pipe_name,
        new_pipe_name=new_pipe_name,
        new_junction_name=leak_junction_name,
        split_at_point=0.5
    )
    
    # Add leak to the newly created junction
    inject_node_leak(
        wn=wn,
        node_name=leak_junction_name,
        area_m2=area_m2,
        start_hour=start_hour,
        duration_hours=duration_hours
    )
    
    return wn, leak_junction_name

def classify_leak_severity(max_flow_m3h: float) -> Tuple[str, str]:
    """Classify simulated leak severity based on discharge rate and config thresholds.
    
    Returns: (severity_code, description_label)
    """
    if max_flow_m3h < config.LEAK_SEVERITY_THRESHOLDS["minor"]["max_flow_m3h"]:
        return "minor", config.LEAK_SEVERITY_THRESHOLDS["minor"]["label"]
    elif max_flow_m3h <= config.LEAK_SEVERITY_THRESHOLDS["moderate"]["max_flow_m3h"]:
        return "moderate", config.LEAK_SEVERITY_THRESHOLDS["moderate"]["label"]
    else:
        return "critical", config.LEAK_SEVERITY_THRESHOLDS["critical"]["label"]
