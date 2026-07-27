from IPPRMBase import PRMBase
from scipy.spatial import cKDTree
import networkx as nx

from IPPerfMonitor import IPPerfMonitor
from IPNodeSampling import UniformSampler


class AbstractGraphPRM(PRMBase):

    def __init__(self, _collChecker, enhancer=None):
        super(AbstractGraphPRM, self).__init__(_collChecker)

        self.graph = nx.Graph()
        self.lastGeneratedNodeNumber = 0
        self.collidingEdges = []
        self.nonCollidingEdges = []
        self.collidingNodes = []
        self.enhancer = enhancer if enhancer is not None else UniformSampler()
        self.enhancementRounds = 0
        self.enhancementNodesAdded = 0
        self.enhancementStrategyName = self.enhancer.__class__.__name__

    @IPPerfMonitor
    def _connect_nearest_neighbors(self, addedNodes, kNearest):
        """
        Connects a list of newly added nodes to their nearest neighbors using a KDTree.
        This logic is shared between EarlyPRM and LazyPRM.
        """
        # Get all positions currently in the graph
        posList = list(nx.get_node_attributes(self.graph, 'pos').values())

        # Safeguard: If the graph is empty, there is nothing to connect
        if not posList:
            return

        kdTree = cKDTree(posList)

        # Iterate over only the newly added nodes
        for node in addedNodes:
            # Find set of candidates to connect to sorted by distance
            result = kdTree.query(self.graph.nodes[node]['pos'], k=kNearest)
            for data in result[1]:
                # Find the corresponding node ID in the graph
                c_node = [x for x, y in self.graph.nodes(
                    data=True) if (y['pos'] == posList[data])][0]

                # Connect if it's not the same node and the edge is not known to collide
                if node != c_node:
                    if (node, c_node) not in self.collidingEdges:
                        self.graph.add_edge(node, c_node)

    @IPPerfMonitor
    def _checkPathSegmentsForCollision(self, path):
        """
        Iterates over the path and checks edges for collision.
        Returns True if a collision is found, False otherwise.
        """
        # Check all path segments
        for elem in zip(path, path[1:]):
            x = elem[0]
            y = elem[1]
            if self._collisionChecker.lineInCollision(self.graph.nodes()[x]['pos'], self.graph.nodes()[y]['pos']):
                self.graph.remove_edge(x, y)
                self.collidingEdges.append((x, y))
                return True
            else:
                self.nonCollidingEdges.append((x, y))

        return False

    @IPPerfMonitor
    def _lazyCollisionCheck(self, path):
        raise NotImplementedError(
            "This method should be implemented in a subclass of LazyPRM.")

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
        self.nonCollidingEdges = []
        self.collidingNodes = []
        self.enhancementRounds = 0
        self.enhancementNodesAdded = 0
        self.enhancementStrategyName = self.enhancer.__class__.__name__

        # 1. check start and goal whether collision free (s. BaseClass)
        checkedStartList, checkedGoalList = self._checkStartGoal(
            startList, goalList)

        # 2. add start and goal to graph
        self.graph.add_node("start", pos=checkedStartList[0])
        self.graph.add_node("goal", pos=checkedGoalList[0])

        # 3. build initial roadmap, using the UniformSampler
        uniformSampler = UniformSampler()
        self._buildRoadmap(
            uniformSampler, config["initialRoadmapSize"], config["kNearest"])

        maxTry = 0
        while maxTry < config["maxIterations"]:
            try:
                path = nx.shortest_path(self.graph, "start", "goal")
            except:
                added_nodes = self._buildRoadmap(
                    self.enhancer, config["updateRoadmapSize"], config["kNearest"])
                self.enhancementRounds += 1
                self.enhancementNodesAdded += added_nodes
                maxTry += 1
                continue

            if self._lazyCollisionCheck(path):
                continue
            else:
                return path

        return []
