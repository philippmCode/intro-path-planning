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

    def __init__(self, _collChecker):
        super(EarlyPRM, self).__init__(_collChecker)
        
        
    @IPPerfMonitor
    def _buildRoadmap(self, sampler, numNodes, kNearest):
        
        # generate #numNodes nodes
        addedNodes = []

        for i in range(numNodes):
            pos = self._getRandomPosition()

            if not self._checkNodeForCollision(pos):
                self.graph.add_node(self.lastGeneratedNodeNumber, pos=pos)
                addedNodes.append(self.lastGeneratedNodeNumber)
                self.lastGeneratedNodeNumber += 1
            else:
                self.collidingNodes.append(pos)

        self._connect_nearest_neighbors(addedNodes, kNearest)


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
    