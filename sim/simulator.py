"""Hydraulic simulation engine using WNTRSimulator with PDD."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import wntr

import config
from network.loader import partition_districts, get_district_pipes

@dataclass
class SimulationResults:
    """Encapsulates structured hydraulic results from a 24h PDD simulation."""
    pressures: pd.DataFrame        # (25, num_nodes) in meters
    demands: pd.DataFrame          # (25, num_nodes) in m3/s
    flowrates: pd.DataFrame        # (25, num_links) in m3/s
    tank_levels: pd.DataFrame      # (25, num_tanks) in meters
    pump_power_kw: pd.DataFrame    # (25, num_pumps) in kW
    pump_energy_kwh: pd.DataFrame  # (25, num_pumps) in kWh
    pump_status: pd.DataFrame      # (25, num_pumps) binary 0/1
    leak_demand_m3h: pd.DataFrame  # (25, num_nodes) in m3/h
    total_water_loss_m3: float     # sum of all leak water lost over 24h
    total_energy_kwh: float        # total pump electricity consumed
    total_energy_cost_tnd: float   # total cost according to TOU tariff
    node_to_district: Dict[str, str]
    district_to_nodes: Dict[str, List[str]]
    district_balances: pd.DataFrame # summary per district: inflow, consumption, loss, gap %

def get_tariff_for_hour(hour: int) -> float:
    """Return the STEG medium-voltage electricity tariff (TND/kWh) for a given hour."""
    # Peak: 18:00 - 21:00 (hours 18, 19, 20)
    if 18 <= hour < 21:
        return config.TARIFF_PEAK_TND_PER_KWH
    # Off-peak: 22:00 - 06:00 (hours 22, 23, 0, 1, 2, 3, 4, 5)
    elif hour >= 22 or hour < 6:
        return config.TARIFF_OFF_PEAK_TND_PER_KWH
    # Day / standard: 06:00 - 18:00, 21:00 - 22:00
    else:
        return config.TARIFF_DAY_TND_PER_KWH

def compute_pump_power_kw(
    flow_m3s: float,
    head_gain_m: float,
    efficiency: float = 0.75
) -> float:
    """Compute pump electrical power in kW: P = (rho * g * Q * H) / (eta * 1000)."""
    if flow_m3s <= 0 or head_gain_m <= 0:
        return 0.0
    rho = 1000.0  # kg/m3
    g = 9.81      # m/s2
    hydraulic_power_w = (rho * g * flow_m3s * head_gain_m) / efficiency
    return hydraulic_power_w / 1000.0

def run_simulation(wn: wntr.network.WaterNetworkModel) -> SimulationResults:
    """Execute a 24-hour PDD simulation using WNTRSimulator and extract structured metrics."""
    node_to_district, district_to_nodes = partition_districts(wn)
    
    # Run WNTRSimulator (Pressure-Dependent Demand)
    sim = wntr.sim.WNTRSimulator(wn)
    raw = sim.run_sim()
    
    pressures = raw.node["pressure"]
    demands = raw.node["demand"]
    flowrates = raw.link["flowrate"]
    
    # Tank levels
    tank_names = list(wn.tank_name_list)
    tank_levels = pd.DataFrame(index=pressures.index)
    for t in tank_names:
        if t in pressures.columns:
            tank_levels[t] = pressures[t]
            
    # Leak demand if present
    if "leak_demand" in raw.node:
        leak_demand_m3s = raw.node["leak_demand"]
        leak_demand_m3h = leak_demand_m3s * 3600.0
        # Total volume in m3 over the 24 hours (integral over 1-hr timesteps)
        total_water_loss_m3 = float((leak_demand_m3s.sum(axis=1) * config.TIMESTEP_SECONDS).sum())
    else:
        leak_demand_m3h = pd.DataFrame(0.0, index=pressures.index, columns=pressures.columns)
        total_water_loss_m3 = 0.0
        
    # Pump status, power (kW), and energy (kWh)
    pump_names = list(wn.pump_name_list)
    pump_power_kw = pd.DataFrame(0.0, index=pressures.index, columns=pump_names)
    pump_energy_kwh = pd.DataFrame(0.0, index=pressures.index, columns=pump_names)
    pump_status = pd.DataFrame(0, index=pressures.index, columns=pump_names)
    
    time_step_h = config.TIMESTEP_SECONDS / 3600.0
    
    for p_name in pump_names:
        pump = wn.get_link(p_name)
        start_node = pump.start_node_name
        end_node = pump.end_node_name
        
        for t_idx in pressures.index:
            flow_m3s = abs(flowrates.loc[t_idx, p_name]) if p_name in flowrates.columns else 0.0
            p_start = pressures.loc[t_idx, start_node] if start_node in pressures.columns else 0.0
            p_end = pressures.loc[t_idx, end_node] if end_node in pressures.columns else 0.0
            
            # Head gain = discharge head - suction head + elevation difference
            elev_diff = getattr(wn.get_node(end_node), "elevation", 0.0) - getattr(wn.get_node(start_node), "elevation", 0.0)
            head_gain = max(0.0, (p_end - p_start) + elev_diff)
            
            p_kw = compute_pump_power_kw(flow_m3s, head_gain)
            pump_power_kw.loc[t_idx, p_name] = p_kw
            pump_energy_kwh.loc[t_idx, p_name] = p_kw * time_step_h
            pump_status.loc[t_idx, p_name] = 1 if flow_m3s > 0.001 else 0

    total_energy_kwh = float(pump_energy_kwh.sum().sum())
    
    # Calculate energy cost under TOU tariff
    total_cost_tnd = 0.0
    for hour, t_idx in enumerate(pressures.index):
        tariff = get_tariff_for_hour(hour % 24)
        hourly_kwh = float(pump_energy_kwh.loc[t_idx].sum())
        total_cost_tnd += hourly_kwh * tariff

    # Calculate district water balances
    district_balance_rows = []
    internal_pipes, boundary_pipes = get_district_pipes(wn, node_to_district)
    
    for district, nodes in district_to_nodes.items():
        # Delivered consumption in m3 over 24h
        district_demand_m3 = float((demands[nodes].sum(axis=1) * config.TIMESTEP_SECONDS).sum())
        district_leak_m3 = float((leak_demand_m3h[nodes].sum(axis=1)).sum()) if nodes else 0.0
        
        # Inflows through boundary pipes into this district
        inflow_m3 = 0.0
        outflow_m3 = 0.0
        for p_name in boundary_pipes:
            pipe = wn.get_link(p_name)
            if p_name not in flowrates.columns:
                continue
            # Check orientation
            start_d = node_to_district.get(pipe.start_node_name)
            end_d = node_to_district.get(pipe.end_node_name)
            
            avg_flow = flowrates[p_name].mean() # m3/s
            vol_m3 = avg_flow * (24 * 3600)
            if end_d == district and vol_m3 > 0:
                inflow_m3 += vol_m3
            elif start_d == district and vol_m3 < 0:
                inflow_m3 += abs(vol_m3)
            elif start_d == district and vol_m3 > 0:
                outflow_m3 += vol_m3
            elif end_d == district and vol_m3 < 0:
                outflow_m3 += abs(vol_m3)
                
        net_inflow_m3 = max(district_demand_m3 + district_leak_m3, inflow_m3 - outflow_m3)
        unexplained_gap_m3 = max(0.0, net_inflow_m3 - district_demand_m3)
        gap_pct = (unexplained_gap_m3 / net_inflow_m3 * 100.0) if net_inflow_m3 > 0 else 0.0
        
        district_balance_rows.append({
            "district": district,
            "consumption_m3": round(district_demand_m3, 1),
            "physical_leak_m3": round(district_leak_m3, 1),
            "net_input_m3": round(net_inflow_m3, 1),
            "unexplained_gap_m3": round(unexplained_gap_m3, 1),
            "gap_percentage": round(gap_pct, 2)
        })
        
    district_balances = pd.DataFrame(district_balance_rows)

    return SimulationResults(
        pressures=pressures,
        demands=demands,
        flowrates=flowrates,
        tank_levels=tank_levels,
        pump_power_kw=pump_power_kw,
        pump_energy_kwh=pump_energy_kwh,
        pump_status=pump_status,
        leak_demand_m3h=leak_demand_m3h,
        total_water_loss_m3=round(total_water_loss_m3, 2),
        total_energy_kwh=round(total_energy_kwh, 2),
        total_energy_cost_tnd=round(total_cost_tnd, 2),
        node_to_district=node_to_district,
        district_to_nodes=district_to_nodes,
        district_balances=district_balances
    )
