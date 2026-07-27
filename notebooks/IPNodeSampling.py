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


class CollidingEdgeSampler:
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


class BridgeSampler:
    """
    Implements Bridge Sampling to find nodes in narrow passages.
    Generates a point in an obstacle, takes a Gaussian step to find a second point
    in an obstacle, and checks if the midpoint between them is collision-free.
    Includes a history log for visualization.
    """

    def __init__(self, sigma=2.0, max_attempts_per_node=150):
        self.sigma = sigma
        self.max_attempts = max_attempts_per_node
        self.history = []

    def enhance(self, prm, numNodes, collision_segment=None):
        positions = []
        anchors = [] # <-- NEU: Speichert (p1, p2) für die Brücke
        
        for _ in range(numNodes):
            found_bridge = False
            
            for _ in range(self.max_attempts):
                # 1. Sample p1 uniform
                p1 = prm._getRandomPosition()
                
                # 2. Prüfe, ob p1 im Hindernis liegt
                if prm._collisionChecker.pointInCollision(p1):
                    # 3. Sample p2 mit Gauß-Verteilung um p1
                    p2 = [c + random.gauss(0, self.sigma) for c in p1]
                    
                    # 4. Prüfe, ob p2 ebenfalls im Hindernis liegt
                    if prm._collisionChecker.pointInCollision(p2):
                        # 5. Berechne den Mittelpunkt pm
                        pm = [(c1 + c2) / 2.0 for c1, c2 in zip(p1, p2)]
                        
                        # 6. Prüfe, ob der Mittelpunkt frei ist
                        if not prm._collisionChecker.pointInCollision(pm):
                            positions.append(pm)
                            anchors.append((p1, p2)) # <-- NEU: Ankerpunkte speichern
                            found_bridge = True
                            break
            
            # Fallback
            if not found_bridge:
                positions.append(prm._getRandomPosition())
                anchors.append(None) # Kein Anker für uniforme Punkte

        # Speichere die Ankerpunkte in der History
        self.history.append({
            'segment': collision_segment, 
            'nodes': positions,
            'bridge_anchors': anchors # <-- NEU
        })
        
        return positions