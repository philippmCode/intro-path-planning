# coding: utf-8
"""
Task 4
"""

from IPPRMBase import PRMBase
from scipy.spatial import cKDTree
import networkx as nx
import random
import time

from IPPerfMonitor import IPPerfMonitor

class EarlyPRM(PRMBase):

    def __init__(self, _collChecker):
        super(EarlyPRM, self).__init__(_collChecker)
        
        self.graph = nx.Graph()
        self.lastGeneratedNodeNumber = 0
        self.collidingEdges = []
        self.nonCollidingEdges =[]
        self.collidingNodes = []
        
    @IPPerfMonitor
    def _buildRoadmap(self, numNodes, kNearest):
        
        # generate #numNodes nodes
        addedNodes = []

        for i in range(numNodes):
            pos = self._getRandomPosition()

            if not self._checkNodeForCollisionAndUpdate(pos):
                self.graph.add_node(self.lastGeneratedNodeNumber, pos=pos)
                addedNodes.append(self.lastGeneratedNodeNumber)
                self.lastGeneratedNodeNumber += 1
            else:
                self.collidingNodes.append(pos)

        # for every node in graph find nearest neigbhours
        posList = list(nx.get_node_attributes(self.graph,'pos').values())
        #print posList
        kdTree = cKDTree(posList)
        
        # to see when _buildRoadmap has to be called again
        #print addedNodes
        for node in addedNodes:
        #for node in self.graph.nodes():
        # Find set of candidates to connect to sorted by distance
            result = kdTree.query(self.graph.nodes[node]['pos'],k=kNearest)
            for data in result[1]:
                c_node = [x for x, y in self.graph.nodes(data=True) if (y['pos']==posList[data])][0]
                if node!=c_node:
                    if (node, c_node) not in self.collidingEdges:
                        self.graph.add_edge(node,c_node)
                    else:
                        continue
                        #print "not adding already checked colliding edge"

    @IPPerfMonitor
    def _checkNodeForCollisionAndUpdate(self, pos):

        if self._collisionChecker.pointInCollision(pos):
            return True
            #print "Colliding Node"
        return False
    
    @IPPerfMonitor
    def _checkEdgesForCollisionAndUpdate(self,path):
        
        # check all path segments
        for elem in zip(path,path[1:]):
            #print elem
            x = elem[0]
            y = elem[1]
            if self._collisionChecker.lineInCollision(self.graph.nodes()[x]['pos'],self.graph.nodes()[y]['pos']):
                self.graph.remove_edge(x,y)
                self.collidingEdges.append((x,y))
                return True
            else:
                self.nonCollidingEdges.append((x,y))
                                                                            
        return False
        
    @IPPerfMonitor   
    def planPath(self, startList, goalList, config):
        """
        
        Args:
            startList (array): start position in planning space
            goalList (array) : goal position in planning space
            config (dict): dictionary with the needed information about the configuration options
            
        Example:
        
            config["initialRoadmapSize"] = 40 # number of nodes of first roadmap
            config["updateRoadmapSize"]  = 20 # number of nodes to add if there is no connection from start to end
            config["kNearest"] = 5 # number of nodes to connect to during setup
            config["maxIterations"] = 40 # number of iterations trying to refine the roadmap
            
        """

        # 0. reset
        self.graph.clear()
        self.lastGeneratedNodeNumber = 0
        self.collidingEdges = []
        
        # 1. check start and goal whether collision free (s. BaseClass)
        checkedStartList, checkedGoalList = self._checkStartGoal(startList,goalList)
        
        # 2. add start and goal to graph
        self.graph.add_node("start", pos=checkedStartList[0])
        self.graph.add_node("goal", pos=checkedGoalList[0])
        
        # 3. build initial roadmap
        self._buildRoadmap(config["initialRoadmapSize"], config["kNearest"])
        
        maxTry = 0
        while maxTry < config["maxIterations"]: 
            try:
                path = nx.shortest_path(self.graph,"start","goal")
            except:
                self._buildRoadmap(config["updateRoadmapSize"], config["kNearest"])
                maxTry += 1
                continue
              
            if self._checkEdgesForCollisionAndUpdate(path):
                continue
            else:
                #print "Found solution"
                return path
            

        return []

    