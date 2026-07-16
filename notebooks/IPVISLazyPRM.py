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
    
    # get a list of positions of all nodes by returning the content of the attribute 'pos'
    pos = nx.get_node_attributes(graph,'pos')
    color = nx.get_node_attributes(graph,'color')

    collChecker.drawObstacles(ax)
    
    # draw graph
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
            # (Note: Start/Goal nodes are drawn separately later with fixed colors)
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

    # draw all connected components, emphasize the largest one
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

    # Build the updated statistics block text
    stats_text = (
        f"Collision Check Stats (Monitor):\n"
        f"Node Checks: {node_checks}\n"
        f"Line Checks: {line_checks}\n"
        f"Points on lines Checks: {points_on_lines}\n"
        f"Discarded Nodes: {removed_nodes}\n"
        f"Removed Edges: {removed_edges}\n"
        f"Free Edges: {free_edges}\n"
        f"Planning Time: {planning_time:.4f}s"
    )
    
    # Place the text box neatly next to the plot axes
    ax.text(-0.05, 0.0, stats_text, 
            transform=ax.transAxes, 
            fontsize=12,            
            horizontalalignment='right',
            verticalalignment='bottom',
            multialignment='left',
            bbox=dict(
                facecolor="white",
                edgecolor="none"
            ))
            
    # --- ADD DYNAMIC LEGEND FOR CUSTOM PRM ---
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
        
    # Add legend to the axis
    if legend_elements:
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(-0.05, 1.0), title="Phases")
    
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
