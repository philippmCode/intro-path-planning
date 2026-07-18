import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as mlines
import numpy as np

class SamplerVisualizer:
    """
    Visualizes the sampling process. 
    It plots the origin edge and newly sampled nodes.
    It also retains previous edges and nodes in a different color 
    to show the evolution of the sampling process over time.
    """

    def __init__(self, x_lim=(0, 25), y_lim=(0, 25)):
        # Define the boundaries of the plot
        self.x_lim = x_lim
        self.y_lim = y_lim

    def plot_sampling(self, current_nodes, current_segment=None, past_history=None, title="Sampler Visualization"):
        """
        Creates a plot showing the edge and the resulting nodes, including historical data.
        
        :param current_nodes: List of [x, y] coordinates for the current step's nodes
        :param current_segment: Tuple of two [x, y] coordinates representing the current edge
        :param past_history: List of dictionaries from previous steps containing 'segment' and 'nodes'
        :param title: Title of the plot
        """
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_xlim(self.x_lim)
        ax.set_ylim(self.y_lim)
        ax.set_title(title)
        ax.grid(True, linestyle='--', alpha=0.6)

        # 1. Plot the historical edges and nodes first (background layer)
        if past_history is not None:
            for step_data in past_history:
                old_segment = step_data.get('segment')
                old_nodes = step_data.get('nodes')

                # Draw old segments (faint red)
                if old_segment is not None:
                    pos_a, pos_b = old_segment
                    ax.plot([pos_a[0], pos_b[0]], [pos_a[1], pos_b[1]], 
                            color='salmon', linewidth=1.5, alpha=0.4, zorder=2)
                    ax.scatter([pos_a[0], pos_b[0]], [pos_a[1], pos_b[1]], 
                               color='salmon', s=30, alpha=0.4, zorder=2)

                # Draw old nodes (faint grey-blue)
                if old_nodes:
                    old_x = [node[0] for node in old_nodes]
                    old_y = [node[1] for node in old_nodes]
                    ax.scatter(old_x, old_y, color='lightsteelblue', alpha=0.5, 
                               s=20, zorder=2)

        # 2. Plot the current origin edge if it exists (foreground layer)
        if current_segment is not None:
            pos_a, pos_b = current_segment
            
            # Draw the line segment
            ax.plot([pos_a[0], pos_b[0]], [pos_a[1], pos_b[1]], 
                    color='red', linewidth=3, label='Current Edge', zorder=4)
            
            # Highlight the endpoints of the segment
            ax.scatter([pos_a[0], pos_b[0]], [pos_a[1], pos_b[1]], 
                       color='darkred', s=60, zorder=5)

        # 3. Plot the current sampled nodes
        if current_nodes:
            x_coords = [node[0] for node in current_nodes]
            y_coords = [node[1] for node in current_nodes]
            
            # Scatter plot for the new nodes
            ax.scatter(x_coords, y_coords, color='blue', alpha=0.9, 
                       s=40, label='Current Nodes', zorder=6)

            # Optional: Draw faint dashed lines from the new nodes to the center 
            # of the collision segment to emphasize their relationship
            if current_segment is not None:
                center_x = (pos_a[0] + pos_b[0]) / 2.0
                center_y = (pos_a[1] + pos_b[1]) / 2.0
                
                for nx, ny in zip(x_coords, y_coords):
                    ax.plot([center_x, nx], [center_y, ny], 
                            color='gray', linestyle=':', alpha=0.4, zorder=3)

        # 4. Construct the legend dynamically
        handles, labels = ax.get_legend_handles_labels()
        if handles or past_history:
            # Add custom legend entries for the history so users know what the faint colors mean
            if past_history and len(past_history) > 0:
                hist_edge = mlines.Line2D([], [], color='salmon', linewidth=1.5, alpha=0.5, label='Past Edges')
                hist_node = mlines.Line2D([], [], color='lightsteelblue', marker='o', linestyle='None', markersize=5, alpha=0.5, label='Past Nodes')
                handles.extend([hist_edge, hist_node])
                labels.extend(['Past Edges', 'Past Nodes'])

            ax.legend(handles=handles, labels=labels, loc='upper right')

        ax.set_aspect('equal')
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.show()