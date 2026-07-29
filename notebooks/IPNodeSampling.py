# coding: utf-8
import random

class BaseSampler:
    """
    Base class for all node enhancement samplers.
    Defines the common interface and shared utilities.
    """
    def __init__(self):
        self.history = []

    def enhance(self, prm, numNodes, collision_segment=None):
        """
        Generates new nodes to enhance the PRM graph.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement the enhance method.")

    def _is_in_limits(self, prm, pos):
        """
        Return whether a sample belongs to the planner's configuration domain.

        ``pointInCollision`` deliberately reports points outside the environment as
        invalid. Sampling strategies must distinguish an actual obstacle from the
        artificial boundary of the configuration domain.
        """
        return prm._collisionChecker.isInLimits(pos)


class UniformSampler(BaseSampler):
    """
    Implements standard uniform sampling.
    Generates random nodes uniformly across the configuration space.
    Collision checking is performed later by the PRM.
    """
    def __init__(self):
        super().__init__()

    def enhance(self, prm, numNodes, collision_segment=None):
        positions = []

        for _ in range(numNodes):
            pos = prm._getRandomPosition()
            positions.append(pos)
            
        self.history.append({'segment': collision_segment, 'nodes': positions})
        return positions




class CollidingEdgeSampler(BaseSampler):
    """
    Samples new nodes near the last colliding edge to improve the
    probability of finding a path around an obstacle.
    Samples are rejected when they lie outside the configuration domain.
    Includes a history log for visualization.
    This corresponds to the colliding edge sampling strategy.
    """

    def __init__(self, sigma=3.5, max_attempts_per_node=30):
        super().__init__()
        self.sigma = sigma
        self.max_attempts = max_attempts_per_node

    def enhance(self, prm, numNodes, collision_segment=None):
        positions = []

        if collision_segment is None and hasattr(prm, 'collidingEdges') and len(prm.collidingEdges) > 0:
            last_edge = prm.collidingEdges[-1]
            pos_a = prm.graph.nodes[last_edge[0]]['pos']
            pos_b = prm.graph.nodes[last_edge[1]]['pos']
            collision_segment = (pos_a, pos_b)

        if collision_segment is None:
            for _ in range(numNodes):
                positions.append(prm._getRandomPosition())

            self.history.append({'segment': None, 'nodes': positions})
            return positions

        pos_a, pos_b = collision_segment

        for _ in range(numNodes):
            for _ in range(self.max_attempts):
                t = random.random()
                interp_pos = [a + t * (b - a) for a, b in zip(pos_a, pos_b)]
                final_pos = [coord + random.gauss(0, self.sigma) for coord in interp_pos]

                if self._is_in_limits(prm, final_pos):
                    positions.append(final_pos)
                    break
            else:
                positions.append(prm._getRandomPosition())

        self.history.append({'segment': collision_segment, 'nodes': positions})

        return positions


class BridgeSampler(BaseSampler):
    """
    Implements Bridge Sampling to find nodes in narrow passages.
    Generates a point in an obstacle, takes a Gaussian step to find a second
    in-domain point in an obstacle, and checks whether the midpoint is free.
    Points outside the configuration domain are invalid, but are not treated as
    obstacle samples for the bridge test.
    Includes a history log for visualization.
    """


    def __init__(self, sigma=2.0, max_attempts_per_node=150):
        super().__init__()
        self.sigma = sigma
        self.max_attempts = max_attempts_per_node

    def enhance(self, prm, numNodes, collision_segment=None):
        positions = []
        anchors = []

        for _ in range(numNodes):
            found_bridge = False

            for _ in range(self.max_attempts):
                p1 = prm._getRandomPosition()

                if prm._collisionChecker.pointInCollision(p1):
                    p2 = [c + random.gauss(0, self.sigma) for c in p1]

                    if (self._is_in_limits(prm, p2)
                            and prm._collisionChecker.pointInCollision(p2)):

                        pm = [(c1 + c2) / 2.0 for c1, c2 in zip(p1, p2)]

                        if (self._is_in_limits(prm, pm)
                                and not prm._collisionChecker.pointInCollision(pm)):
                            positions.append(pm)
                            anchors.append((p1, p2))
                            found_bridge = True
                            break

            if not found_bridge:
                positions.append(prm._getRandomPosition())
                anchors.append(None)

        self.history.append({
            'segment': collision_segment,
            'nodes': positions,
            'bridge_anchors': anchors
        })

        return positions