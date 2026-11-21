"""Graph representation and topological utilities using NetworkX."""

from typing import Dict, List, Optional
import networkx as nx
import numpy as np
import wntr

def build_networkx_graph(wn: wntr.network.WaterNetworkModel) -> nx.Graph:
    """Build a NetworkX undirected graph from the WNTR network model.
    
    Nodes have coordinates, elevation, and type.
    Edges have pipe length, diameter, and roughness.
    """
    G = nx.Graph()
    
    for name, node in wn.nodes():
        G.add_node(
            name,
            pos=node.coordinates,
            elevation=getattr(node, "elevation", 0.0),
            node_type=node.node_type
        )
        
    for name, link in wn.links():
        length = getattr(link, "length", 100.0)
        diameter = getattr(link, "diameter", 0.3)
        G.add_edge(
            link.start_node_name,
            link.end_node_name,
            name=name,
            weight=length,
            diameter=diameter,
            link_type=link.link_type
        )
        
    return G

def get_node_hop_distance(G: nx.Graph, source: str, target: str) -> int:
    """Return topological shortest path hop count between two nodes."""
    try:
        return nx.shortest_path_length(G, source, target)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return 999

def get_pipe_hop_distance(G: nx.Graph, wn: wntr.network.WaterNetworkModel, pipe1: str, pipe2: str) -> int:
    """Return topological hop count between two pipes (via incident nodes)."""
    if pipe1 == pipe2:
        return 0
    p1 = wn.get_link(pipe1)
    p2 = wn.get_link(pipe2)
    
    nodes1 = [p1.start_node_name, p1.end_node_name]
    nodes2 = [p2.start_node_name, p2.end_node_name]
    
    min_dist = 999
    for n1 in nodes1:
        for n2 in nodes2:
            d = get_node_hop_distance(G, n1, n2)
            if d < min_dist:
                min_dist = d
    return min_dist

def smooth_pressure_residuals(
    residuals: Dict[str, float],
    G: nx.Graph,
    alpha: float = 0.65
) -> Dict[str, float]:
    """Smooth pressure drop residuals across topological graph neighbors.
    
    residual_smooth[i] = alpha * residual[i] + (1 - alpha) * mean(residual[neighbors])
    """
    smoothed = {}
    for node, val in residuals.items():
        if node not in G:
            smoothed[node] = val
            continue
        neighbors = list(G.neighbors(node))
        if not neighbors:
            smoothed[node] = val
            continue
        neighbor_vals = [residuals.get(nbr, 0.0) for nbr in neighbors if nbr in residuals]
        if neighbor_vals:
            smoothed[node] = alpha * val + (1.0 - alpha) * float(np.mean(neighbor_vals))
        else:
            smoothed[node] = val
            
    return smoothed
