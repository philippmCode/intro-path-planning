import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as mlines

class SamplerVisualizer:
    def __init__(self, x_lim=(0, 25), y_lim=(0, 25)):
        self.x_lim = x_lim
        self.y_lim = y_lim

    def plot_sampling(self, current_nodes, current_segment=None, past_history=None, 
                      checker=None, free_segments=None, title="Sampler Visualization",
                      current_anchors=None): # <-- NEU: Argument hinzugefügt
        
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_xlim(self.x_lim)
        ax.set_ylim(self.y_lim)
        ax.set_title(title)
        ax.grid(True, linestyle='--', alpha=0.6)

        # 1. Plot the obstacles
        if checker:
            checker.drawObstacles(ax)

        # 2. Plot the verified free segments
        if free_segments:
            for seg in free_segments:
                pos_a, pos_b = seg
                ax.plot([pos_a[0], pos_b[0]], [pos_a[1], pos_b[1]], 
                        color='gold', linewidth=1.5, zorder=2)

        # 3. Plot historical edges and nodes
        if past_history is not None:
            for step_data in past_history:
                old_segment = step_data.get('segment')
                old_nodes = step_data.get('nodes')

                if old_segment is not None:
                    pos_a, pos_b = old_segment
                    ax.plot([pos_a[0], pos_b[0]], [pos_a[1], pos_b[1]], 
                            color='salmon', linewidth=1.5, alpha=0.4, zorder=3)
                    ax.scatter([pos_a[0], pos_b[0]], [pos_a[1], pos_b[1]], 
                               color='salmon', s=30, alpha=0.4, zorder=3)

                if old_nodes:
                    old_x = [node[0] for node in old_nodes]
                    old_y = [node[1] for node in old_nodes]
                    ax.scatter(old_x, old_y, color='lightsteelblue', alpha=0.5, 
                               s=20, zorder=3)

        # 4. Plot current origin edge
        if current_segment is not None:
            pos_a, pos_b = current_segment
            ax.plot([pos_a[0], pos_b[0]], [pos_a[1], pos_b[1]], 
                    color='red', linewidth=3, label='Current Collision Edge', zorder=4)
            ax.scatter([pos_a[0], pos_b[0]], [pos_a[1], pos_b[1]], 
                       color='darkred', s=60, zorder=5)

        # 5. NEW: Plot Bridge Anchors (p1 and p2)
        if current_anchors:
            for anchor in current_anchors:
                if anchor is not None:
                    p1, p2 = anchor
                    # Draw dashed line between the two obstacle points
                    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='magenta', linestyle='--', linewidth=1.5, zorder=5)
                    # Draw the obstacle points as 'X'
                    ax.scatter([p1[0], p2[0]], [p1[1], p2[1]], color='magenta', marker='x', s=60, zorder=6)

        # 6. Plot current sampled nodes (pm)
        if current_nodes:
            x_coords = [node[0] for node in current_nodes]
            y_coords = [node[1] for node in current_nodes]
            ax.scatter(x_coords, y_coords, color='blue', alpha=0.9, 
                       s=40, label='New Sampled Nodes', zorder=7)

        # Build legend
        handles, labels = ax.get_legend_handles_labels()
        
        obs_patch = patches.Patch(color='dimgray', alpha=0.4, label='Obstacle')
        free_line = mlines.Line2D([], [], color='gold', linewidth=1.5, label='Free Segments')
        handles.extend([obs_patch, free_line])
        labels.extend(['Obstacle', 'Free Segments'])
        
        if past_history and len(past_history) > 0:
            hist_edge = mlines.Line2D([], [], color='salmon', linewidth=1.5, alpha=0.5, label='Past Edges')
            hist_node = mlines.Line2D([], [], color='lightsteelblue', marker='o', linestyle='None', markersize=5, alpha=0.5, label='Past Nodes')
            handles.extend([hist_edge, hist_node])
            labels.extend(['Past Edges', 'Past Nodes'])
            
        # Add Bridge legend if active
        if current_anchors and any(a is not None for a in current_anchors):
            bridge_line = mlines.Line2D([], [], color='magenta', linestyle='--', marker='x', markersize=8, label='Bridge Anchors (p1, p2)')
            handles.append(bridge_line)
            labels.append('Bridge Anchors (p1, p2)')

        ax.legend(handles=handles, labels=labels, loc='upper right', bbox_to_anchor=(1.45, 1))
        ax.set_aspect('equal')
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.show()