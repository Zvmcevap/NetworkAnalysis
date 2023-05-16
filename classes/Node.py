import math
from typing import Set, Optional, List, Dict


class Node:
    """
    *** Node Class ***

    Represents vertices of a graph, named "Node" because it is shorter and hopefully also correct.

    Attributes:
        - name (str): name of the node.
        - neighbors (set[Node]): a set of nodes that are connected to this node.
        - degree (int): Number of connections to other nodes.
        - parent (Node): temporary attribute to remember the previous Node Dijsktra used to get to this node.

    Methods:
        - set_degree: calculate the degree of the node once it's we are done changing connections.

    """

    def __init__(self, name: str):
        # Elementary stats
        self.name: str = name
        self.neighbors: List[Node] = []

        # Centrality
        self.degree: int = 0
        self.clustering_coefficient: int = 0
        self.betweeness: int = 0
        self.bridge_paths = set()
        self.closeness: int = 0

        # If bipartite graph, it should have color:
        self.color = None

        # Pathfinding
        self.parent: Optional[Node] = None
        self.distance = math.inf

        self.paths = {}  # Dictionary containing all paths to nonadjacent nodes

    def set_degree(self):
        self.degree = len(self.neighbors)

    def set_closeness(self, num_nodes):
        """
        Average amount of steps needed to other nodes
        Should be easy to calculate now that I have all the other graph analysis done.

        Should the graph not be connected, I will ignore unreachable nodes.
        Should the Node be completely disconnected, closeness is 0.
        """

        total_length = len(self.neighbors)
        # If no neighbors, Node is done
        if total_length == 0:
            self.closeness = 0
            return

        for node in self.paths:
            if self.paths[node] is None:
                continue
            for path in self.paths[node]:
                total_length += len(path) - 1
                break  # Only one path is needed

        average_length = total_length / (num_nodes - 1)
        self.closeness = 1 / average_length

    def set_clustering_coefficient(self):
        """
        Number of edges between neighbours to other neighbors/maximum possible edges between neighbours.

        returns:
            - float: if neighbors
            - None: if no or one neighbor.
        """
        if self.degree == 0:
            return None

        connections_between_neighbours = 0

        for n in self.neighbors:
            for n_of_n in n.neighbors:  # XD
                if n_of_n in self.neighbors:
                    connections_between_neighbours += 1

        connections_between_neighbours /= 2
        max_possible = (self.degree * (self.degree - 1)) / 2

        if max_possible != 0:
            self.clustering_coefficient = connections_between_neighbours / max_possible
        else:
            self.clustering_coefficient = 0

    # Overwritten the __str__ and __repr__ methods for more useful printing to terminal
    def __str__(self):
        return f"{self.name=}; {self.degree=}; {self.clustering_coefficient=}; {self.betweeness=}"

    def __repr__(self):
        return f'{self.name}'
