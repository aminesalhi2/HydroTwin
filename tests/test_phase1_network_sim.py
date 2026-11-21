"""Tests for Phase 1: Network loading, district partitioning, and PDD simulation."""

import time
import pytest
import config
from network.loader import load_network, partition_districts, get_district_pipes
from network.graph import build_networkx_graph, get_node_hop_distance
from sim.simulator import run_simulation
from app.components import create_network_plotly_figure

def test_load_network():
    wn = load_network(duration_hours=24)
    assert wn.num_nodes == 97
    assert wn.num_links == 119
    assert wn.num_pumps == 2
    assert wn.num_tanks == 3
    assert wn.options.hydraulic.demand_model in ("PDD", "PDA")
    assert wn.options.time.duration == 24 * 3600

def test_partition_districts():
    wn = load_network(duration_hours=24)
    node_to_district, district_to_nodes = partition_districts(wn)
    
    assert len(district_to_nodes) == 5
    for d_name in config.DISTRICT_NAMES:
        assert d_name in district_to_nodes
        assert len(district_to_nodes[d_name]) > 0
        
    # All junctions assigned
    total_assigned = sum(len(nodes) for nodes in district_to_nodes.values())
    assert total_assigned == wn.num_junctions

def test_pdd_simulation_performance_and_physics():
    wn = load_network(duration_hours=24)
    
    start_t = time.time()
    results = run_simulation(wn)
    duration = time.time() - start_t
    
    # Must run in a few seconds
    assert duration < 6.0, f"Simulation took too long: {duration:.2f}s"
    
    # Check dimensions: 25 hourly steps (0 to 24)
    assert results.pressures.shape[0] == 25
    assert results.pressures.shape[1] == wn.num_nodes
    
    # Pressures are physical
    mean_pressure = results.pressures.mean().mean()
    assert mean_pressure > 15.0, f"Mean pressure is non-physical: {mean_pressure} m"
    
    # Zero leak water loss in baseline
    assert results.total_water_loss_m3 == 0.0
    
    # Energy consumed is positive and reasonable
    assert results.total_energy_kwh > 0.0
    assert results.total_energy_cost_tnd > 0.0
    
    # District balances computed
    assert len(results.district_balances) == 5
    assert (results.district_balances["consumption_m3"] > 0).all()

def test_plotly_map_generation():
    wn = load_network(duration_hours=24)
    results = run_simulation(wn)
    fig = create_network_plotly_figure(
        wn,
        pressures_df=results.pressures,
        time_idx=12,
        node_to_district=results.node_to_district
    )
    assert fig is not None
    assert len(fig.data) >= 4  # pipes, junctions, pumps, tanks
