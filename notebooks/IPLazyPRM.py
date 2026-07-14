# coding: utf-8
"""
This code is part of the course "Introduction to robot path planning" (Author: Bjoern Hein). It is based on the slides given during the course, so please **read the information in theses slides first**

License is based on Creative Commons: Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) (pls. check: http://creativecommons.org/licenses/by-nc/4.0/)
"""

from scipy.spatial import cKDTree
import networkx as nx
import random
import time

from IPPerfMonitor import IPPerfMonitor
from IPNodeSampling import UniformSampler
from AbstractGraphPRM import AbstractGraphPRM

class LazyPRM(AbstractGraphPRM):

    def __init__(self, _collChecker, enhancer=None):
        super(LazyPRM, self).__init__(_collChecker)
    

        
    @IPPerfMonitor
    def _buildRoadmap(self, sampler, numNodes, kNearest):
        
        # generate #numNodes nodes
        addedNodes = []
        positions = sampler.enhance(self, numNodes)
        for pos in positions:
            self.graph.add_node(self.lastGeneratedNodeNumber, pos=pos)
            addedNodes.append(self.lastGeneratedNodeNumber)
            self.lastGeneratedNodeNumber += 1

        
        self._connect_nearest_neighbors(addedNodes, kNearest)

    
    @IPPerfMonitor
    def _checkForCollisionAndUpdate(self,path):
        # first check all nodes
        for nodeNumber in path:
            if self._collisionChecker.pointInCollision(self.graph.nodes[nodeNumber]['pos']):
                self.collidingNodes.append(self.graph.nodes[nodeNumber]['pos'])
                self.graph.remove_node(nodeNumber)
                #print "Colliding Node"
                return True
                                                                            
        return self._checkPathSegmentsForCollision(path)
    

    def _lazyCollisionCheck(self, path):
        """
        This method checks the edges of the path for collision and updates the graph accordingly.
        Returns True if a collision is found, False otherwise.
        """
        return self._checkForCollisionAndUpdate(path)

    