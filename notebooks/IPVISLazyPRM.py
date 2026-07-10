# coding: utf-8

"""
This code is part of the course "Introduction to robot path planning" (Author: Bjoern Hein). It is based on the slides given during the course, so please **read the information in theses slides first**

License is based on Creative Commons: Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) (pls. check: http://creativecommons.org/licenses/by-nc/4.0/)
"""

import networkx as nx


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
    

    if hasattr(planner, 'stats'):
        # Format the statistics vertically (alle untereinander)
        stats_text = (
            f"Collision Check Stats:\n"
            f"Point Checks: {planner.stats.get('point_in_collision_calls', 0)}\n"
            f"Line Checks: {planner.stats.get('line_in_collision_calls', 0)}\n"
            f"Removed Nodes: {planner.stats.get('removed_colliding_nodes', 0)}\n"
            f"Removed Edges: {planner.stats.get('removed_colliding_edges', 0)}\n"
            f"Free Edges: {planner.stats.get('confirmed_free_edges', 0)}\n"
            f"Planning Time: {planner.stats.get('planning_time_seconds', 0.0):.4f}s"
        )
        
        # Place the text to the left of the axes
        ax.text(-0.05, 0.5, stats_text, 
                transform=ax.transAxes, 
                fontsize=12,            
                horizontalalignment='right',
                verticalalignment='center',
                multialignment='left',
                bbox=dict(
                    facecolor="white",
                    edgecolor="none"
                ))
    
    return

