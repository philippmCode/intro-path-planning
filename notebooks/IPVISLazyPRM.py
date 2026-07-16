# coding: utf-8

"""
This code is part of the course "Introduction to robot path planning" (Author: Bjoern Hein). It is based on the slides given during the course, so please **read the information in theses slides first**

License is based on Creative Commons: Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) (pls. check: http://creativecommons.org/licenses/by-nc/4.0/)
"""

from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
import networkx as nx
from IPPerfMonitor import IPPerfMonitor


def customPRMVisualize(planner, initialRoadmapSize, updateRoadmapSize, solution = [] , ax=None, nodeSize = 300):
    graph = planner.graph.copy()
    collChecker = planner._collisionChecker
    collEdges = planner.collidingEdges
    nonCollEdges = planner.nonCollidingEdges
    collNodes = planner.collidingNodes
    
    # Get a list of positions of all nodes by returning the content of the attribute 'pos'
    pos = nx.get_node_attributes(graph,'pos')
    color = nx.get_node_attributes(graph,'color')

    collChecker.drawObstacles(ax)
    
    # Draw graph edges
    nx.draw_networkx_edges(graph, pos, ax = ax)

    # Determine the phase of each node dynamically based on its integer ID
    nodelist = list(pos.keys())
    node_phases = []
    
    for node in nodelist:
        if isinstance(node, int):
            if node < initialRoadmapSize:
                node_phases.append(0)  # Initial roadmap phase
            else:
                # Calculate the update phase (1, 2, 3, etc.) using integer division
                phase = 1 + (node - initialRoadmapSize) // updateRoadmapSize
                node_phases.append(phase)
        else:
            # Assign start, goal, or other non-integer nodes to phase 0
            node_phases.append(0)
            
    # Draw graph nodes with color gradient representing the phases
    cmap = plt.get_cmap('viridis')
    
    # Explicitly calculate min and max phases to map colors accurately for both plot and legend
    vmin = min(node_phases) if node_phases else 0
    vmax = max(node_phases) if node_phases else 1
    
    nx.draw_networkx_nodes(
        graph, pos, ax=ax, 
        nodelist=nodelist, 
        node_color=node_phases, 
        cmap=cmap,
        vmin=vmin, 
        vmax=vmax,
        node_size=nodeSize
    )

    # Draw all connected components, emphasize the largest one
    Gcc=(graph.subgraph(c) for c in nx.connected_components(graph))
    G0=next(Gcc) # [0] = largest connected component
    
    if collEdges != []:
        collGraph = nx.Graph()
        collGraph.add_nodes_from(graph.nodes(data=True))

        for i in collEdges:
            collGraph.add_edge(i[0],i[1])
        nx.draw_networkx_edges(collGraph,pos,alpha=0.2,edge_color='r',width=5)

    if nonCollEdges != []:
        nonCollGraph = nx.Graph()
        nonCollGraph.add_nodes_from(graph.nodes(data=True))

        for i in nonCollEdges:
            nonCollGraph.add_edge(i[0],i[1])
        nx.draw_networkx_edges(nonCollGraph,pos,alpha=0.8,edge_color='yellow',width=5)
    
    # Draw start and goal
    if "start" in graph.nodes(): 
        nx.draw_networkx_nodes(graph,pos,nodelist=["start"],
                                   node_size=300,
                                   node_color='#00dd00',  ax = ax)
        nx.draw_networkx_labels(graph,pos,labels={"start": "S"},  ax = ax)

    if "goal" in graph.nodes():
        nx.draw_networkx_nodes(graph,pos,nodelist=["goal"],
                                   node_size=300,
                                   node_color='#DD0000',  ax = ax)
        nx.draw_networkx_labels(graph,pos,labels={"goal": "G"},  ax = ax)

    if solution != []:
        # Draw nodes based on solution path
        Gsp = nx.subgraph(graph,solution)
        # Draw edges based on solution path
        nx.draw_networkx_edges(Gsp,pos,alpha=0.8,edge_color='g',width=10)
    
    try:
        df = IPPerfMonitor.dataFrame()
        
        # Count calls based on function names inside the data frame
        node_checks = len(df[df['name'] == '_checkNodeForCollision']) if not df.empty else 0
        total_point_checks = len(df[df['name'] == 'pointInCollision']) if not df.empty else 0
        line_checks = len(df[df['name'] == 'lineInCollision']) if not df.empty else 0
        
        # Read the calculated planning time directly from the planPath execution entry
        plan_path_row = df[df['name'] == 'planPath']
        planning_time = plan_path_row['time'].values[0] if not plan_path_row.empty else 0.0
    except Exception:
        # Fallback values if the data frame is empty or not accessible
        total_point_checks, line_checks, planning_time = 0, 0, 0.0

    # Get counts of discarded nodes/edges from internal lists
    removed_nodes = len(collNodes)
    removed_edges = len(collEdges)
    free_edges = len(nonCollEdges)
    points_on_lines = total_point_checks - node_checks  # Calculate the number of point checks on lines

    # Combine stats and legend title into one string
    legend_title_text = (
        f"Collision Check Stats (Monitor):\n"
        f"Node Checks: {node_checks}\n"
        f"Line Checks: {line_checks}\n"
        f"Points on lines Checks: {points_on_lines}\n"
        f"Discarded Nodes: {removed_nodes}\n"
        f"Removed Edges: {removed_edges}\n"
        f"Free Edges: {free_edges}\n"
        f"Planning Time: {planning_time:.4f}s\n"
        f"----------------------------------------\n"
        f"Phases"
    )
            
    # --- COMBINED LEGEND AND STATS BOX ---
    # Extract unique phases present in the graph
    unique_phases = sorted(list(set(node_phases)))
    
    legend_elements = []
    # Create a normalizer to fetch the exact same color NetworkX used for drawing
    norm = plt.Normalize(vmin=vmin, vmax=vmax)
    
    for phase in unique_phases:
        # Generate the appropriate label
        label = "Initial Phase" if phase == 0 else f"Update Phase {phase}"
        # Fetch the exact color from the colormap using the normalized phase value
        phase_color = cmap(norm(phase))
        
        # Add a placeholder marker for the legend
        legend_elements.append(
            Line2D([0], [0], marker='o', color='w', label=label, 
                   markerfacecolor=phase_color, markersize=10)
        )
        
    # Place the combined box outside the plot on the left side
    if legend_elements:
        leg = ax.legend(
            handles=legend_elements, 
            loc='center right', 
            bbox_to_anchor=(-0.05, 0.5), 
            title=legend_title_text
        )
        
        # Ensure the multi-line title is aligned neatly to the left
        leg.get_title().set_multialignment('left')
    
    return


def animatePRMVisualize(planner, initialRoadmapSize, updateRoadmapSize, solution=[], ax=None, nodeSize=300, max_phase=None):
    """
    Dedicated visualization method for step-by-step animation of the PRM generation.
    Accurately shows the chronological checking of edges based on their node IDs.
    """
    base_graph = planner.graph

    # Helper function to determine the sampling phase of a node based on its ID.
    def get_node_phase(node_id):
        if not isinstance(node_id, int):
            return 0  # Start/goal nodes
        if node_id < initialRoadmapSize:
            return 0
        return 1 + (node_id - initialRoadmapSize) // updateRoadmapSize

    # Precompute the sampling phase for all nodes in the final roadmap.
    all_nodes = list(base_graph.nodes())
    all_phases = [get_node_phase(n) for n in all_nodes]

    if max_phase is not None:
        allowed_nodes = [node for node, phase in zip(all_nodes, all_phases) if phase <= max_phase]
    else:
        allowed_nodes = all_nodes

    graph = base_graph.subgraph(allowed_nodes).copy()
    nodelist = list(graph.nodes())
    node_phases = [get_node_phase(n) for n in nodelist]

    collChecker = planner._collisionChecker
    collEdges = planner.collidingEdges
    nonCollEdges = planner.nonCollidingEdges
    collNodes = planner.collidingNodes

    pos = nx.get_node_attributes(graph, 'pos')

    collChecker.drawObstacles(ax)

    # Draw all unchecked roadmap edges as a faint background.
    nx.draw_networkx_edges(graph, pos, ax=ax, edge_color='gray', alpha=0.15, width=1.0)

    cmap = plt.get_cmap('viridis')

    # Use fixed color limits so that node colors remain consistent
    # when navigating through the animation.
    vmin = min([get_node_phase(n) for n in planner.graph.nodes() if isinstance(n, int)], default=0)
    vmax = max([get_node_phase(n) for n in planner.graph.nodes() if isinstance(n, int)], default=1)

    nx.draw_networkx_nodes(
        graph, pos, ax=ax,
        nodelist=nodelist,
        node_color=node_phases,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        node_size=nodeSize
    )

    # Draw checked edges in chronological order.
    # An edge becomes visible as soon as both of its incident nodes
    # have been generated.
    if collEdges != []:
        collGraph = nx.Graph()

        for edge in collEdges:
            u, v = edge[0], edge[1]
            phase_u = get_node_phase(u)
            phase_v = get_node_phase(v)

            # Draw the edge only after its sampling phase has been reached.
            # The edge history is preserved even if one of its nodes
            # was removed later.
            if (max_phase is None) or (max(phase_u, phase_v) <= max_phase):
                collGraph.add_node(
                    u,
                    pos=planner.graph.nodes[u]['pos']
                    if u in planner.graph.nodes
                    else planner._getRandomPosition()
                )
                collGraph.add_node(
                    v,
                    pos=planner.graph.nodes[v]['pos']
                    if v in planner.graph.nodes
                    else planner._getRandomPosition()
                )
                collGraph.add_edge(u, v)

        if len(collGraph.edges()) > 0:
            edge_pos = nx.get_node_attributes(collGraph, 'pos')
            nx.draw_networkx_edges(
                collGraph,
                edge_pos,
                alpha=0.5,
                edge_color='r',
                width=3,
                ax=ax
            )

    if nonCollEdges != []:
        nonCollGraph = nx.Graph()

        for edge in nonCollEdges:
            u, v = edge[0], edge[1]
            phase_u = get_node_phase(u)
            phase_v = get_node_phase(v)

            if (max_phase is None) or (max(phase_u, phase_v) <= max_phase):
                nonCollGraph.add_node(u, pos=planner.graph.nodes[u]['pos'])
                nonCollGraph.add_node(v, pos=planner.graph.nodes[v]['pos'])
                nonCollGraph.add_edge(u, v)

        if len(nonCollGraph.edges()) > 0:
            edge_pos = nx.get_node_attributes(nonCollGraph, 'pos')
            nx.draw_networkx_edges(
                nonCollGraph,
                edge_pos,
                alpha=0.8,
                edge_color='yellow',
                width=3,
                ax=ax
            )

    # Draw all rejected nodes as black crosses.
    # Since their IDs are no longer available, they are shown
    # permanently to indicate where sampling attempts failed.
    if collNodes != []:
        xs = [p[0] for p in collNodes]
        ys = [p[1] for p in collNodes]
        ax.scatter(xs, ys, c='black', marker='x', s=80, linewidths=2, zorder=5)

    # Draw start and goal nodes.
    if "start" in graph.nodes():
        nx.draw_networkx_nodes(graph, pos, nodelist=["start"], node_size=300, node_color='#00dd00', ax=ax)
        nx.draw_networkx_labels(graph, pos, labels={"start": "S"}, ax=ax)

    if "goal" in graph.nodes():
        nx.draw_networkx_nodes(graph, pos, nodelist=["goal"], node_size=300, node_color='#DD0000', ax=ax)
        nx.draw_networkx_labels(graph, pos, labels={"goal": "G"}, ax=ax)

    # Draw the final solution path if available.
    if solution != [] and all(n in graph.nodes() for n in solution):
        Gsp = nx.subgraph(graph, solution)
        nx.draw_networkx_edges(Gsp, pos, alpha=0.8, edge_color='g', width=8, ax=ax)

    # Build the legend.
    unique_phases = sorted(list(set(all_phases)))
    legend_elements = []
    norm = plt.Normalize(vmin=vmin, vmax=vmax)

    legend_elements.append(
        Line2D([0], [0], color='gray', lw=1, alpha=0.5, label='Unchecked Edge')
    )
    legend_elements.append(
        Line2D(
            [0], [0],
            marker='x',
            color='w',
            label='Destroyed Node',
            markeredgecolor='black',
            markersize=8,
            markeredgewidth=2
        )
    )

    for phase in unique_phases:
        label = "Initial Phase" if phase == 0 else f"Update Phase {phase}"
        phase_color = cmap(norm(phase))
        alpha_val = 1.0 if (max_phase is None or phase <= max_phase) else 0.2

        legend_elements.append(
            Line2D(
                [0], [0],
                marker='o',
                color='w',
                label=label,
                markerfacecolor=phase_color,
                markersize=10,
                alpha=alpha_val
            )
        )

    if legend_elements:
        leg = ax.legend(
            handles=legend_elements,
            loc='center right',
            bbox_to_anchor=(-0.05, 0.5),
            title="Animation Phases"
        )
        leg.get_title().set_multialignment('left')

    return


def lazyPRMVisualize(planner, solution = [] , ax=None, nodeSize = 300):
    graph = planner.graph.copy()
    collChecker = planner._collisionChecker
    collEdges = planner.collidingEdges
    nonCollEdges = planner.nonCollidingEdges
    # get a list of positions of all nodes by returning the content of the attribute 'pos'
    pos = nx.get_node_attributes(graph,'pos')
    color = nx.get_node_attributes(graph,'color')

    collChecker.drawObstacles(ax)
    

    # get a list of degrees of all nodes
    #degree = nx.degree_centrality(graph)
    
    # draw graph
    nx.draw_networkx_nodes(graph, pos, ax = ax, nodelist=list(color.keys()), node_color=list(color.values()), node_size=nodeSize)
    nx.draw_networkx_edges(graph, pos, ax = ax)


    
    # draw all connected components, emphasize the largest one
    Gcc=(graph.subgraph(c) for c in nx.connected_components(graph))
    G0=next(Gcc) # [0] = largest connected component
    
    # how largest connected component
    nx.draw_networkx_edges(G0,pos,
                               edge_color='b',
                               width=3.0, style='dashed',
                               alpha=0.5,
                            )
    if collEdges != []:
        collGraph = nx.Graph()
        collGraph.add_nodes_from(graph.nodes(data=True))

        #collGraph
        for i in collEdges:
            collGraph.add_edge(i[0],i[1])
        nx.draw_networkx_edges(collGraph,pos,alpha=0.2,edge_color='r',width=5)


    
    if nonCollEdges != []:
        nonCollGraph = nx.Graph()
        nonCollGraph.add_nodes_from(graph.nodes(data=True))

        #collGraph
        for i in nonCollEdges:
            nonCollGraph.add_edge(i[0],i[1])
        nx.draw_networkx_edges(nonCollGraph,pos,alpha=0.8,edge_color='yellow',width=5)
    


    # draw start and goal
    if "start" in graph.nodes(): 
        nx.draw_networkx_nodes(graph,pos,nodelist=["start"],
                                   node_size=300,
                                   node_color='#00dd00',  ax = ax)
        nx.draw_networkx_labels(graph,pos,labels={"start": "S"},  ax = ax)


    if "goal" in graph.nodes():
        nx.draw_networkx_nodes(graph,pos,nodelist=["goal"],
                                   node_size=300,
                                   node_color='#DD0000',  ax = ax)
        nx.draw_networkx_labels(graph,pos,labels={"goal": "G"},  ax = ax)



    if solution != []:
        # draw nodes based on solution path
        Gsp = nx.subgraph(graph,solution)
        # draw edges based on solution path
        nx.draw_networkx_edges(Gsp,pos,alpha=0.8,edge_color='g',width=10)
    

    
    return
