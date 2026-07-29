# coding: utf-8

"""
This code is part of the course "Introduction to robot path planning" (Author: Bjoern Hein). It is based on the slides given during the course, so please **read the information in theses slides first**

License is based on Creative Commons: Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) (pls. check: http://creativecommons.org/licenses/by-nc/4.0/)
"""

from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
import networkx as nx
from IPPerfMonitor import IPPerfMonitor

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _get_node_phase(node_id, initialRoadmapSize, updateRoadmapSize):
    """Calculates the sampling phase of a given node."""
    if not isinstance(node_id, int) or node_id < initialRoadmapSize:
        return 0
    return 1 + (node_id - initialRoadmapSize) // updateRoadmapSize

def _draw_evaluated_edges(planner, initialRoadmapSize, updateRoadmapSize, ax, max_phase=None):
    """Draws colliding (red) and non-colliding (yellow) edges based on phase."""
    collEdges = getattr(planner, 'collidingEdges', [])
    nonCollEdges = getattr(planner, 'nonCollidingEdges', [])
    
    def edge_in_phase(u, v):
        if max_phase is None: return True
        return max(_get_node_phase(u, initialRoadmapSize, updateRoadmapSize),
                   _get_node_phase(v, initialRoadmapSize, updateRoadmapSize)) <= max_phase

    if collEdges:
        collGraph = nx.Graph()
        for u, v in collEdges:
            if edge_in_phase(u, v):
                pos_u = planner.graph.nodes[u]['pos'] if u in planner.graph.nodes else planner._getRandomPosition()
                pos_v = planner.graph.nodes[v]['pos'] if v in planner.graph.nodes else planner._getRandomPosition()
                collGraph.add_node(u, pos=pos_u)
                collGraph.add_node(v, pos=pos_v)
                collGraph.add_edge(u, v)
        if collGraph.edges():
            pos = nx.get_node_attributes(collGraph, 'pos')
            nx.draw_networkx_edges(collGraph, pos, alpha=0.5, edge_color='r', width=3, ax=ax)

    if nonCollEdges:
        nonCollGraph = nx.Graph()
        for u, v in nonCollEdges:
            if edge_in_phase(u, v):
                nonCollGraph.add_node(u, pos=planner.graph.nodes[u]['pos'])
                nonCollGraph.add_node(v, pos=planner.graph.nodes[v]['pos'])
                nonCollGraph.add_edge(u, v)
        if nonCollGraph.edges():
            pos = nx.get_node_attributes(nonCollGraph, 'pos')
            nx.draw_networkx_edges(nonCollGraph, pos, alpha=0.8, edge_color='yellow', width=3, ax=ax)

def _draw_start_goal_solution(graph, pos, solution, ax):
    """Draws the start node, goal node, and the final solution path."""
    if "start" in graph.nodes():
        nx.draw_networkx_nodes(graph, pos, nodelist=["start"], node_size=300, node_color='#00dd00', ax=ax)
        nx.draw_networkx_labels(graph, pos, labels={"start": "S"}, ax=ax)
    if "goal" in graph.nodes():
        nx.draw_networkx_nodes(graph, pos, nodelist=["goal"], node_size=300, node_color='#DD0000', ax=ax)
        nx.draw_networkx_labels(graph, pos, labels={"goal": "G"}, ax=ax)
    if solution and all(n in graph.nodes() for n in solution):
        Gsp = nx.subgraph(graph, solution)
        nx.draw_networkx_edges(Gsp, pos, alpha=0.8, edge_color='g', width=8, ax=ax)

def _get_stats_text(planner):
    """Extracts performance monitoring stats into a formatted string."""
    try:
        df = IPPerfMonitor.dataFrame()
        node_checks = len(df[df['name'] == '_checkNodeForCollision']) if not df.empty else 0
        total_point_checks = len(df[df['name'] == 'pointInCollision']) if not df.empty else 0
        line_checks = len(df[df['name'] == 'lineInCollision']) if not df.empty else 0
        plan_path_row = df[df['name'] == 'planPath']
        planning_time = plan_path_row['time'].values[0] if not plan_path_row.empty else 0.0
    except Exception:
        total_point_checks, line_checks, node_checks, planning_time = 0, 0, 0, 0.0

    removed_nodes = len(getattr(planner, 'collidingNodes', []))
    removed_edges = len(getattr(planner, 'collidingEdges', []))
    free_edges = len(getattr(planner, 'nonCollidingEdges', []))
    
    return (
        f"Collision Check Stats:\n"
        f"Node Checks: {node_checks}\n"
        f"Line Checks: {line_checks}\n"
        f"Points on lines Checks: {total_point_checks - node_checks}\n"
        f"Discarded Nodes: {removed_nodes}\n"
        f"Removed Edges: {removed_edges}\n"
        f"Free Edges: {free_edges}\n"
        f"Planning Time: {planning_time:.4f}s"
    )

def _create_legend(ax, unique_phases, cmap, norm, title, extra_elements=None):
    """Builds the dynamic legend (List vs. Colorbar) and adds it to the plot."""
    legend_elements = list(extra_elements) if extra_elements else []
    MAX_LEGEND_ENTRIES = 30

    if len(unique_phases) <= MAX_LEGEND_ENTRIES:
        if "Stats" in title:
            title += "\n----------------------------------------\nPhases"
        for phase in unique_phases:
            label = "Initial Phase" if phase == 0 else f"Update Phase {phase}"
            legend_elements.append(
                Line2D([0], [0], marker='o', color='w', label=label, 
                       markerfacecolor=cmap(norm(phase)), markersize=10, alpha=1.0)
            )
        if legend_elements:
            leg = ax.legend(handles=legend_elements, loc='center right', bbox_to_anchor=(-0.05, 0.5), title=title)
            leg.get_title().set_multialignment('left')
    else:
        leg = ax.legend(handles=legend_elements, loc='lower right', bbox_to_anchor=(-0.05, 0.5), title=title)
        leg.get_title().set_multialignment('left')
        
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cb_ax = ax.inset_axes([-0.23, 0.1, 0.02, 0.35]) 
        cbar = ax.figure.colorbar(sm, cax=cb_ax, orientation='vertical')
        cbar.ax.invert_yaxis()  # Achse umdrehen (von oben nach unten)
        cbar.set_label('Phases (0 = Initial)')

# =============================================================================
# MAIN VISUALIZATION FUNCTIONS
# =============================================================================

def customPRMVisualize(planner, initialRoadmapSize, updateRoadmapSize, solution=[], ax=None, nodeSize=300):
    if ax is None: ax = plt.gca()
        
    graph = planner.graph.copy()
    pos = nx.get_node_attributes(graph, 'pos')
    
    planner._collisionChecker.drawObstacles(ax)
    nx.draw_networkx_edges(graph, pos, ax=ax)

    all_nodes = list(graph.nodes())
    node_phases = [_get_node_phase(n, initialRoadmapSize, updateRoadmapSize) for n in all_nodes]
            
    cmap = plt.get_cmap('viridis')
    vmin, vmax = min(node_phases, default=0), max(node_phases, default=1)
    norm = plt.Normalize(vmin=vmin, vmax=vmax)
    
    nx.draw_networkx_nodes(graph, pos, ax=ax, nodelist=all_nodes, node_color=node_phases, 
                           cmap=cmap, vmin=vmin, vmax=vmax, node_size=nodeSize, alpha=1.0)

    _draw_evaluated_edges(planner, initialRoadmapSize, updateRoadmapSize, ax)
    _draw_start_goal_solution(graph, pos, solution, ax)
    
    stats_text = _get_stats_text(planner)
    _create_legend(ax, sorted(list(set(node_phases))), cmap, norm, stats_text)
    
    return


def animatePRMVisualize(planner, initialRoadmapSize, updateRoadmapSize, solution=[], ax=None, nodeSize=300, max_phase=None):
    if ax is None: ax = plt.gca()

    base_graph = planner.graph
    all_nodes = list(base_graph.nodes())
    all_phases = [_get_node_phase(n, initialRoadmapSize, updateRoadmapSize) for n in all_nodes]

    if max_phase is not None:
        allowed_nodes = [node for node, phase in zip(all_nodes, all_phases) if phase <= max_phase]
    else:
        allowed_nodes = all_nodes

    graph = base_graph.subgraph(allowed_nodes).copy()
    pos = nx.get_node_attributes(graph, 'pos')
    nodelist = list(graph.nodes())
    node_phases = [_get_node_phase(n, initialRoadmapSize, updateRoadmapSize) for n in nodelist]

    planner._collisionChecker.drawObstacles(ax)
    nx.draw_networkx_edges(graph, pos, ax=ax, edge_color='gray', alpha=0.15, width=1.0)

    cmap = plt.get_cmap('viridis')
    int_phases = [p for n, p in zip(all_nodes, all_phases) if isinstance(n, int)]
    vmin, vmax = min(int_phases, default=0), max(int_phases, default=1)
    norm = plt.Normalize(vmin=vmin, vmax=vmax)

    nx.draw_networkx_nodes(graph, pos, ax=ax, nodelist=nodelist, node_color=node_phases, 
                           cmap=cmap, vmin=vmin, vmax=vmax, node_size=nodeSize, alpha=1.0)

    _draw_evaluated_edges(planner, initialRoadmapSize, updateRoadmapSize, ax, max_phase)

    collNodes = getattr(planner, 'collidingNodes', [])
    if collNodes:
        xs, ys = zip(*collNodes)
        ax.scatter(xs, ys, c='black', marker='x', s=80, linewidths=2, zorder=5)

    _draw_start_goal_solution(graph, pos, solution, ax)

    extra_elements = [
        Line2D([0], [0], color='gray', lw=1, alpha=0.5, label='Unchecked Edge'),
        Line2D([0], [0], marker='x', color='w', label='Destroyed Node', markeredgecolor='black', markersize=8, markeredgewidth=2)
    ]
    
    _create_legend(ax, sorted(list(set(all_phases))), cmap, norm, "Animation Phases", extra_elements)

    return


def lazyPRMVisualize(planner, solution=[], ax=None, nodeSize=300):
    if ax is None: ax = plt.gca()
        
    graph = planner.graph.copy()
    pos = nx.get_node_attributes(graph, 'pos')
    color = nx.get_node_attributes(graph, 'color')

    planner._collisionChecker.drawObstacles(ax)
    
    nx.draw_networkx_nodes(graph, pos, ax=ax, nodelist=list(color.keys()), node_color=list(color.values()), node_size=nodeSize)
    nx.draw_networkx_edges(graph, pos, ax=ax)

    try:
        Gcc = (graph.subgraph(c) for c in nx.connected_components(graph))
        G0 = next(Gcc)
        nx.draw_networkx_edges(G0, pos, edge_color='b', width=3.0, style='dashed', alpha=0.5, ax=ax)
    except StopIteration:
        pass

    _draw_evaluated_edges(planner, 0, 1, ax) # Dummy phase values, lazyPRM doesn't use phases
    _draw_start_goal_solution(graph, pos, solution, ax)
    
    return