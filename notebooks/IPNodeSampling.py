# coding: utf-8
import random


class UniformSampler:
    """
    Implements standard uniform sampling.
    Generates random nodes uniformly across the configuration space.
    Collision checking is performed later by the PRM.
    """

    def enhance(self, prm, numNodes):
        positions = []

        for _ in range(numNodes):
            pos = prm._getRandomPosition()
            positions.append(pos)

        return positions


class PathLocalSampler:
    """
    Samples new nodes near the last colliding edge to improve the
    probability of finding a path around an obstacle.
    Includes a history log for visualization.
    """

    def __init__(self, sigma=3.5):
        self.sigma = sigma
        self.history = [] 

    def enhance(self, prm, numNodes, collision_segment=None):
        positions = []

        # If no explicit segment is provided, extract the latest colliding edge
        if collision_segment is None and hasattr(prm, 'collidingEdges') and len(prm.collidingEdges) > 0:
            last_edge = prm.collidingEdges[-1]
            pos_a = prm.graph.nodes[last_edge[0]]['pos']
            pos_b = prm.graph.nodes[last_edge[1]]['pos']
            collision_segment = (pos_a, pos_b)

        # Fallback: Generate uniformly distributed samples
        if collision_segment is None:
            for _ in range(numNodes):
                positions.append(prm._getRandomPosition())
            
            # Log uniform generation (no segment)
            self.history.append({'segment': None, 'nodes': positions})
            return positions

        pos_a, pos_b = collision_segment

        for _ in range(numNodes):
            # 1. Interpolate a random point along the colliding edge
            t = random.random()
            interp_pos = [
                pos_a[0] + t * (pos_b[0] - pos_a[0]),
                pos_a[1] + t * (pos_b[1] - pos_a[1]),
            ]

            # 2. Add Gaussian noise
            final_pos = [
                coord + random.gauss(0, self.sigma)
                for coord in interp_pos
            ]
            positions.append(final_pos)

        # NEW: Log the segment and generated positions for the benchmark slider
        self.history.append({'segment': collision_segment, 'nodes': positions})
        
        return positions