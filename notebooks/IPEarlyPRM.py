# coding: utf-8
"""
Task 4
"""

from IPPRMBase import PRMBase
from scipy.spatial import cKDTree
import networkx as nx
import random
import time

from AbstractGraphPRM import AbstractGraphPRM
from IPPerfMonitor import IPPerfMonitor


class EarlyPRM(AbstractGraphPRM):

    def __init__(self, _collChecker, enhancer=None):
        super(EarlyPRM, self).__init__(_collChecker, enhancer=enhancer)

    @IPPerfMonitor
    def _buildRoadmap(self, sampler, numNodes, kNearest):

        addedNodes = []
        max_attempts = numNodes * 100  # Failsafe against infinite loops
        attempts = 0

        # While-Schleife: Samplen bis die geforderte Anzahl freier Knoten erreicht ist
        while len(addedNodes) < numNodes and attempts < max_attempts:
            # Fordere nur so viele neue Samples an, wie noch fehlen
            needed_nodes = numNodes - len(addedNodes)
            positions = sampler.enhance(self, needed_nodes)

            for pos in positions:
                attempts += 1
                if not self._checkNodeForCollision(pos):
                    self.graph.add_node(self.lastGeneratedNodeNumber, pos=pos)
                    addedNodes.append(self.lastGeneratedNodeNumber)
                    self.lastGeneratedNodeNumber += 1
                    
                    # Abbrechen, wenn wir innerhalb der for-Schleife das Ziel erreichen
                    if len(addedNodes) == numNodes:
                        break
                else:
                    self.collidingNodes.append(pos)

        self._connect_nearest_neighbors(addedNodes, kNearest)
        return len(addedNodes)

    @IPPerfMonitor
    def _checkNodeForCollision(self, pos):
        if self._collisionChecker.pointInCollision(pos):
            return True
        return False

    def _lazyCollisionCheck(self, path):
        """
        This method checks the edges of the path for collision and updates the graph accordingly.
        Returns True if a collision is found, False otherwise.
        """
        return self._checkPathSegmentsForCollision(path)
