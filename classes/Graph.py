import math
import random
from typing import List, Optional, Union, Tuple
from operator import attrgetter

from classes.Node import Node


class Graph:
    """
    *** Graph Class ***

    Contains all the nodes and edges in the graph along with mathematical analysis, loading and drawing methods.

    Attributes:
        - name (str): Each graph deserves a name.
        - nodes (List[Nodes]): Contains a list of all the nodes (of class Node) in the graph.
        - am (List[List[int]]): Adjacency matrix, a square matrix where rows and columns represent nodes, and
                                values represent if there is a connection between them: 1 for True, 0 for False.

    Methods:
        - load_from_file: Deletes current graph and loads in a new one.
        - open_graphical_interface: Opens a web-browser containing a canvas to draw the graph.

    """

    def __init__(self, name):
        self.name: str = name
        self.nodes: List[Node] = []

        # Analysis
        self.analyzed = False

        # Adjacency Matrix
        self.am: List[List[int]] = []

        # Degrees Analysis
        self.max_degree: int = 0
        self.min_degree = math.inf
        self.total_degree: int = 0
        self.average_degree: int = 0
        self.number_of_edges: int = 0
        self.density: int = 0

        # Advanced centrality

        # Node betweeness
        self.max_betweeness = None
        self.average_betweeness = None
        self.min_betweeness = None
        self.total_paths = None
        # Edge betweeness
        self.edge_bridges = {}
        self.edge_betweeness = {}
        self.max_edge_betweeness = 0
        self.avg_edge_betweeness = 0

        # Node Closeness
        self.max_closeness = None
        self.average_closeness = None
        self.min_closeness = None

        # Node Clustering Coefficient
        self.max_cluster_coefficient = None
        self.average_cluster_coefficient = None
        self.min_cluster_coefficient = None

        # Connectedness, partitioned, communities, subgraphs
        self.connected = None
        self.connectivity = None
        self.partitions = []

        self.subgraphs = []
        self.snips = []

        # Paths
        self.bipartite = None
        self.diameter = None
        self.average_path_length: float = math.inf

        self.hamilton_circuit = None
        self.hamilton_path = None

        self.euler_circuit = None
        self.euler_path = None

        self.odd_cycle = None

    def set_adjacency_matrix(self):
        # make an adjacency_matrix
        self.am = []  # Reset matrix

        n = len(self.nodes)
        for i in range(n):
            row = [int(self.nodes[j] in self.nodes[i].neighbors) for j in range(n)]  # I'm practicing list comprehension
            self.am.append(row)

    def set_node_degrees(self):
        # Update node degrees and save the maximum and sum total of degrees
        self.total_degree = 0
        self.max_degree = 0
        self.min_degree = math.inf

        for node in self.nodes:
            node.degree = len(node.neighbors)
            self.total_degree += node.degree
            if node.degree > self.max_degree:
                self.max_degree = node.degree
            if node.degree < self.min_degree:
                self.min_degree = node.degree

        if len(self.nodes) != 0:
            self.average_degree = self.total_degree / len(self.nodes)
        else:
            self.average_degree = 0

    def get_max_degree_nodes(self):
        # Return a list of nodes with degree == maximum degree in graph
        return [node for node in self.nodes if node.degree == self.max_degree]

    def set_number_of_connections_and_density(self):
        self.number_of_edges = self.total_degree // 2
        L_max = (len(self.nodes) * (len(self.nodes) - 1)) // 2
        if L_max != 0:
            self.density = self.number_of_edges / L_max
        else:
            self.density = None

    def set_diameter_avg_path_length(self):
        self.diameter = 0
        self.connected = True
        self.partitions = []
        path_lengths = []

        for node in self.nodes:
            if len(self.partitions) == 0 or not any(node in part for part in self.partitions):
                partition = {node}
                self.partitions.append(partition)
            else:
                partition = [part for part in self.partitions if node in part][0]

            for i in range(len(node.neighbors)):
                partition.add(node.neighbors[i])
                if self.diameter < 1:
                    self.diameter = 1
                path_lengths.append(1)

            for finish in node.paths:
                if node.paths[finish] is not None:
                    partition = partition.union(set(path for path in node.paths[finish]))
                    path_lengths.append(len(list(node.paths[finish])[0]) - 1)
                    if self.diameter < len(list(node.paths[finish])[0]) - 1:
                        self.diameter = len(list(node.paths[finish])[0]) - 1
                else:
                    self.connected = False

        if len(path_lengths) > 0:
            self.average_path_length = sum(path_lengths) / len(path_lengths)

    def get_path_from_final_node(self, node: Node):
        if node is None:
            return None
        path = [node]
        while node.parent:
            node = node.parent
            path.append(node)
        path.reverse()
        return path

    def calculate_shortest_paths_for_all_nodes(self):
        for i, start_node in enumerate(self.nodes):
            for j in range(i + 1, len(self.nodes)):  # paths are reversible, so we only need to search forwards
                finish_node = self.nodes[j]
                if finish_node in start_node.neighbors or finish_node in start_node.paths:
                    # Adjacent nodes or paths already found need no pathfinding
                    continue

                final = self.dijsktra(start=start_node, finish=finish_node)  # returns our finish node or None
                path = self.get_path_from_final_node(node=final)

                if path is None:
                    start_node.paths[finish_node] = None
                    finish_node.paths[start_node] = None
                    continue

                all_paths = self.depth_first_search(
                    current=start_node,
                    path=[start_node],
                    search_type="a",
                    max_depth=len(path),
                    finish=final,
                    paths={tuple(path)}
                )
                all_paths_reversed = {tuple(reversed(p)) for p in all_paths}

                start_node.paths[finish_node] = all_paths
                finish_node.paths[start_node] = all_paths_reversed

        # Sort them by path length
        self.set_diameter_avg_path_length()
        for node in self.nodes:
            node.paths = dict(
                sorted(node.paths.items(), key=lambda x: len(list(x[1])[0]) if x[1] is not None else math.inf))

    def analyze_betweeness_centrality(self):
        """
        Betweeness For Nodes and Edges

        For all paths between nodes j and k, count the number of times they pass through node i and edge e.
        Divide that number by all the paths.

        Since I save all the shortest paths from all nodes to all nodes that are not neighbors, I can
        loop through all the paths in a node and look for all that are between start and finish.
        """
        self.total_paths = 0

        for node in self.nodes:
            for finish in node.paths:
                if node.paths[finish] is None:
                    continue
                self.total_paths += len(node.paths[finish])
                for path in node.paths[finish]:
                    for bridge in path[1:-1]:
                        bridge.bridge_paths.add(path)

                    for i in range(len(path) - 1):
                        edge = (path[i], path[i + 1])
                        if edge not in self.edge_bridges and tuple(reversed(edge)) not in self.edge_bridges:
                            self.edge_bridges[edge] = set()

                        if edge in self.edge_bridges:
                            self.edge_bridges[edge].add(path)
                        else:
                            self.edge_bridges[tuple(reversed(edge))].add(path)

        if self.total_paths == 0:
            self.max_betweeness = self.min_betweeness = self.average_betweeness = 0
            return

        for node in self.nodes:
            node.betweeness = len(node.bridge_paths) / self.total_paths

        for edge in self.edge_bridges:
            self.edge_betweeness[edge] = len(self.edge_bridges[edge]) / self.total_paths
        self.edge_betweeness = {k: v for k, v in
                                sorted(self.edge_betweeness.items(), key=lambda item: item[1], reverse=True)}
        total_edge_between = [self.edge_betweeness[k] for k in self.edge_betweeness]
        if len(total_edge_between) == 0:
            self.avg_edge_betweeness = 0
        else:
            self.max_betweeness = max(total_edge_between)
            self.avg_edge_betweeness = sum(total_edge_between) / len(total_edge_between)

        list_of_betweenessness = [node.betweeness for node in self.nodes if node.betweeness is not None]
        if len(list_of_betweenessness) == 0:
            self.max_betweeness = self.min_betweeness = self.average_betweeness = 0
            return
        self.max_betweeness = max(list_of_betweenessness)
        self.min_betweeness = min(list_of_betweenessness)
        self.average_betweeness = sum(list_of_betweenessness) / len(list_of_betweenessness)

    def analyze_closessness(self):
        for node in self.nodes:
            node.set_closeness(num_nodes=len(self.nodes))
            if node.closeness is None:
                continue
            if self.max_closeness is None or self.max_closeness < node.closeness:
                self.max_closeness = node.closeness
            if self.min_closeness is None or self.min_closeness < node.closeness:
                self.min_closeness = node.closeness

        closer = [node.closeness for node in self.nodes if node.closeness is not None]
        if len(closer) == 0:
            self.min_closeness = self.max_closeness = self.average_closeness = 0
            return
        self.average_closeness = sum(closer) / len(closer)

    def analyze_cluster_coefficients(self):
        for node in self.nodes:
            node.set_clustering_coefficient()
            if node.clustering_coefficient is None:
                continue
            if self.max_cluster_coefficient is None or self.max_cluster_coefficient < node.clustering_coefficient:
                self.max_cluster_coefficient = node.clustering_coefficient
            if self.min_cluster_coefficient is None or self.min_cluster_coefficient < node.clustering_coefficient:
                self.min_cluster_coefficient = node.clustering_coefficient

        ccs = [node.clustering_coefficient for node in self.nodes if node.clustering_coefficient is not None]
        if len(ccs) == 0:
            self.max_cluster_coefficient = self.min_cluster_coefficient = self.average_cluster_coefficient = 0
            return
        self.average_cluster_coefficient = sum(ccs) / len(ccs)

    def analyze_bipartite(self):
        """
        First we will do a breath-first-search with dijsktra, to find the first node we can't color with only
        2 colors, then use that node to find the smallest odd cycle.

        Unconnected graphs complicate this a bit...
        """

        odd_colors_out = []
        for node in self.nodes:
            if len(node.neighbors) == 0:
                node.color = "yellow"
                continue

            odd_one = self.dijsktra(start=node, bipartite=True)
            if odd_one is not None:
                odd_colors_out.append(odd_one)

            if self.connected and len(odd_colors_out) == 0:
                # If the graph is connected and colored we have won
                self.bipartite = True
                return

            if self.connected and len(odd_colors_out) > 0:
                # it found an odd one, break but only if the graph is connected, I want to color all of them
                break

        if len(odd_colors_out) == 0:
            self.bipartite = True
            return

        for odd in odd_colors_out:
            self.odd_cycle = self.depth_first_search(current=odd, path=[odd], search_type="b")
            if self.odd_cycle is not None:
                self.bipartite = False
                return

    def hamilton_qn(self, path: List[str]):
        # Hamilton Circuit Finder for hypercube graph, to solve it taking too long above Q5
        good_path = ["0" + node for node in path[::]]  # Copy
        evil_path = ["1" + node for node in path[::-1]]  # Reversed copy
        return good_path + evil_path

    def analyze_hamilton(self):
        """
        An exhaustive search for a Hamilton path and cycle, as reading about it, no surefire way to find it seems to
        exist.

        However... hypercube graph Q6 or higher seem to cause trouble, so I will do them manually.
        """
        if not self.connected or len([node for node in self.nodes if node.degree == 1]) > 2:
            self.hamilton_path = None
            self.hamilton_circuit = None
            return

        # If Q graph
        if self.name[0] == "q" and self.name[1:].isdigit():
            n = int(self.name[1:])
            h_path = [""]
            for i in range(n):
                h_path = self.hamilton_qn(h_path)

            hp_nodes = [self.get_node_by_name(name) for name in h_path]
            self.hamilton_path = hp_nodes
            self.hamilton_circuit = hp_nodes[::] + [hp_nodes[0]]
            return

        # Search for path from every node until you find one
        for node in self.nodes:
            self.hamilton_path = self.depth_first_search(current=node, path=[node], search_type='hp')
            if self.hamilton_path is not None:
                break

        # If there is no path there is no circuit!
        if self.hamilton_path is None:
            self.hamilton_circuit = None
            return

        # In case the path already loops in on itself just make that the circuit and append the first node to end
        elif self.hamilton_path[0] in self.hamilton_path[-1].neighbors:
            self.hamilton_circuit = self.hamilton_path.copy()
            self.hamilton_circuit.append(self.hamilton_path[0])
            return

        # Search for Hamilton circuit, but don't if a node has a degree of 1
        if len([node for node in self.nodes if node.degree == 1]) > 0:
            self.hamilton_circuit = None
            return

        for node in self.nodes:
            self.hamilton_circuit = self.depth_first_search(current=node, path=[node], search_type='hc')
            if self.hamilton_circuit is not None:
                break

    def analyze_euler(self):
        """
        Definition:
         1. Euler path through the graph means to use every available edge, but only once.
         2. Euler circuit is an Euler path that starts and ends in the same vertex.

        First we will check if the paths are possible:
         0. If the graph is not fully connected, none of it is possible.
         1. Euler's path is possible if there are exactly 2 or none odd degree vertices.
         2. Euler's circuit requires all degrees to be even.

        If they are possible, we will use Depth-First-Search to find at least one way and save it.
        """
        if not self.connected:
            self.euler_path = None
            self.euler_circuit = None
            return

        odd_nodes = [node for node in self.nodes if node.degree % 2 == 1]

        if len(odd_nodes) == 0:
            ep_start = random.choice(self.nodes)
            ec_start = random.choice(self.nodes)
            self.euler_path = self.depth_first_search(current=ep_start, path=[ep_start], edges=[], search_type="ep")
            self.euler_circuit = self.depth_first_search(current=ec_start, path=[ec_start], edges=[], search_type="ec")
            return

        if len(odd_nodes) == 2:
            self.euler_circuit = None
            start = odd_nodes[random.choice([0, 1])]
            self.euler_path = self.depth_first_search(current=start, path=[start], edges=[], search_type="ep")

    def depth_first_search(self,
                           current: Node,
                           path: List[Node],
                           edges: Optional[List[set[Node, Node]]] = None,
                           search_type: Optional[str] = None,
                           max_depth: int = None,
                           paths: Optional[set[Tuple[Node]]] = None,
                           finish: Optional[Node] = None
                           ):
        """
        *** Depth First Search ***

        Recursive function to check all available possibilities, used primarily to find Euler/Hamilton paths/circuits.

        Parameters:
            - current (Node): current node we are at.
            - path (List of Nodes): The path we are returning.
            - edges (List of sets of Nodes) (Optional): For Euler we need to save the edges, so we don't use them again.
            - search_type (string): letter combinations, e for Euler, h for Hamilton, p for path, c for circuit,
                                    meaning if the search_type is ep we are looking for Euler's path,
                                    hc Hamilton's circuit.
            - max_depth (int) (optional): finding all shortest paths to node
            - paths (set of paths) (optional): All paths to the finish node
            - finish (Node) (optional): Node we are searching for

        Returns:
            - List[Nodes]: Our final path, should we find it successfully
            - set[Tuple[Nodes]]: set of all paths to the finish
            - None: if it fails miserably
        """

        # Win/Loose ending conditions Euler:
        if search_type == "ep" or search_type == "ec":
            if len(edges) == self.number_of_edges:
                if search_type == "ec" and not path[0] == path[-1]:  # Circuit needs to circuit back.
                    return
                return path

        # Win/Loose condition for Hamilton
        if search_type == "hp" or search_type == "hc":
            if len(path) == len(self.nodes):
                if search_type == "hc":
                    # Hamilton circuit is a bit easier to check
                    if path[0] not in current.neighbors:
                        return
                    path.append(path[0])
                return path

        # Win/Loose condition for all paths
        if search_type == "a":
            if len(path) >= max_depth:
                return paths

            # Winning neighbor for all paths, no need to check other neighbors
            if finish in current.neighbors:
                path_copy = path.copy()
                path_copy.append(finish)
                paths.add(tuple(path_copy))
                return paths

        # Continue your search
        for neighbor in current.neighbors:
            # Failed neighbors for Euler
            if search_type == "ep" or search_type == "ec":
                if {current, neighbor} in edges:  # Edge unusable
                    continue
                if len(edges) - self.number_of_edges > 1:  # If we are not on the last edge
                    # Don't use the neighbor if he should be last
                    if neighbor.degree - sum(neighbor in edge for edge in edges) == 1:
                        continue

            # Failed neighbors for Hamilton
            if search_type == "hp" or search_type == "hc":
                if neighbor in path:
                    continue

            # Winning/Loosing neighbor for Bipartite
            if search_type == "b" and neighbor in path:
                print(len(path), path.index(neighbor))
                if len(path) - path.index(neighbor) > 2 and (len(path) - path.index(neighbor)) % 2 == 1:
                    # If the cycle is odd return
                    return path[path.index(neighbor):] + [neighbor]
                else:
                    # Otherwise ignore the neighbor
                    continue

            # Should neighbor succeed!
            path_copy = path.copy()
            path_copy.append(neighbor)

            edges_copy = None
            if search_type == "ec" or search_type == "ep":
                edges_copy = edges.copy()
                edges_copy.append({current, neighbor})

            path_success = self.depth_first_search(current=neighbor,
                                                   path=path_copy,
                                                   edges=edges_copy,
                                                   search_type=search_type,
                                                   paths=paths,
                                                   max_depth=max_depth,
                                                   finish=finish
                                                   )
            # Stop recurring if successful
            if search_type != "a" and path_success is not None:
                return path_success
        return paths

    def dijsktra(self, start: Node,
                 finish: Optional[Node] = None,
                 max_distance: Union[int, float] = math.inf,
                 bipartite: bool = False):
        """
        *** Dijsktra or Breadth First Search ***

        Pathfinding implementation, trying to make it as general purpose as possible, to be used for
        finding path from A to B, finding all nodes at a max distance from start or to make a minimum spanning tree.

        Parameters:
            - start (Node): The Node from which we are finding a path.
            - finish (Node) (Optional): Node we are trying to reach, optional in case of unknown goal.
            - max_distance (int) (optional): Max distance to stop the search at, if not set it is infinite.
            - bipartite (boolean): Boolean indicating if we are trying to figure out bipartisanship


        return:
            - Node: If path is found return the finish Node and can backtrack with parents for the path
            - List[Node]: A list of nodes at a set distance
            - None: If pathfinding is unsuccessful return None
        """

        self.reset_pathfinding()

        open_list = [start]
        if bipartite and start.color is None:
            start.color = 'magenta'
        closed_list = []
        start.distance = 0
        current_distance = 0

        while len(open_list) > 0 and current_distance < max_distance:
            current_node = open_list.pop(0)
            current_distance += 1

            if current_node == finish:  # We found it... or it is None
                return current_node

            if current_distance == max_distance:  # Distance reached, return neighbours that were not yet found.
                return [node for node in current_node.neighbors if node.distance == math.inf]

            for neighbour in current_node.neighbors:  # Check all the connected nodes
                if bipartite and neighbour.color is not None and neighbour.color == current_node.color:
                    # If searching for bipartite end it if 2 connected nodes are the same color
                    return neighbour  # Going to return it because it is the ideal candidate to find a cycle

                elif bipartite and neighbour.color is None:
                    neighbour.color = "magenta" if current_node.color == "cyan" else "cyan"

                if neighbour.distance > current_distance:  # If they are closer than before set parent and distance
                    neighbour.distance = current_distance
                    neighbour.parent = current_node

                    if neighbour in closed_list:  # If they are in the closed list kick them out
                        closed_list.remove(neighbour)
                        open_list.append(neighbour)
                    if neighbour not in open_list:  # If they are not in the open list add them
                        open_list.append(neighbour)

    def reset_pathfinding(self):
        # Reset the nodes to their default pathfinding values
        for node in self.nodes:
            node.parent = None
            node.distance = math.inf

    def reset_color(self):
        for node in self.nodes:
            node.color = None

    def get_node_by_name(self, name: str):
        for node in self.nodes:
            if node.name == name:
                return node

    def sort_nodes_by_name(self):
        if all([node.name.isdigit() for node in self.nodes]):
            self.nodes.sort(key=lambda node: int(node.name))
        else:
            self.nodes.sort(key=attrgetter("name"))

    """
    Methods to create subgraphs with fewer and fewer connections to find out when it falls apart.
    """

    def check_if_snip(self, graph):
        """
        Check if all edge betweeness is the same within a partition.
        If we have a disconnected graph, we could still have communities inside the partitions.

        Parameters:
            - graph (Graph): the graph we are checking atm

        Returns:
             - True when it finds a missmatch in the particular partition
             - False if they are all the same
        """
        for partition in graph.partitions:
            betweeness = None
            for edge in graph.edge_betweeness:
                if edge[0] in partition and betweeness is None:
                    betweeness = round(graph.edge_betweeness[edge], 4)  # Afraid of float point error
                elif edge[0] in partition and round(graph.edge_betweeness[edge], 4) != betweeness:
                    return True
        return False

    def get_node_copies(self, nodes: List[Node]):
        """
        Need to create manual copies of nodes so that the original graph is untouched.

        Parameters:
            - nodes (list of Nodes): to avoid recursively making subgraphs of subgraphs I will just pass in the
                                     list of nodes I want to copy
        """
        new_nodes = [Node(name=node.name) for node in nodes]  # Create a list of Nodes

        for old_node in nodes:
            new_node = [n for n in new_nodes if n.name == old_node.name][0]
            for neighbor in old_node.neighbors:  # Add the connections
                new_neighbor = [n for n in new_nodes if n.name == neighbor.name][0]
                new_node.neighbors.append(new_neighbor)
        return new_nodes

    def delete_edge_from_copy(self, edge: Tuple[Node, Node], nodes_copy: List[Node]):
        evil_nodes = [node for node in nodes_copy if node.name in [en.name for en in edge]]
        evil_nodes[0].neighbors.remove(evil_nodes[1])
        evil_nodes[1].neighbors.remove(evil_nodes[0])

    def generate_subgraph(self, nodes: List[Node], name: str):
        subgraph = Graph(name=name)
        subgraph.nodes = nodes
        return subgraph

    def analyze_communities(self):
        """
        Finding communities and connectivity
        Here we can use some network analysis to consider when we should even bother:
            1. 'Math-Graphs' where all nodes have x degree, have no obvious communities and fall apart after x snips
            2. Bipartite graphs, if full, have no obvious communities, fall apart after lowest degree snips.

        With this in mind I will use betweeness as the main factor and consider the graph to be community-less,
        if all edges have the same betweeness in all partitions.

        Honestly let's just focus on the 'Girvan-Newman' algorithm and snip periodically with these rules:
            1. Get edge with the biggest 'betweeness' i.e. is in the most bridges
            2. Make a subgraph without that edge
            3. Repeat the process for the new subgraph
            4. Stop when 'betweeness' is the same for all nodes within a partition

        Parameters:
            - GM (GraphManager): Has the analyzer method
            - SM (StringManater): Needed by GM analyzer method

        Returns:
             - None
        """

        self.connectivity = None
        current_graph = self
        i = 1
        current_snips = []
        while self.check_if_snip(graph=current_graph):
            # Generate new graph
            new_nodes = self.get_node_copies(nodes=current_graph.nodes)
            edge_to_delete = max(current_graph.edge_betweeness, key=current_graph.edge_betweeness.get)
            self.delete_edge_from_copy(edge_to_delete, new_nodes)
            current_snips.append((self.get_node_by_name(edge_to_delete[0].name),
                                  self.get_node_by_name(edge_to_delete[1].name)))

            new_graph = Graph(str(i))
            new_graph.nodes = new_nodes

            # Analyze graph and save it if it has more partitions than the last one
            new_graph.set_node_degrees()
            new_graph.set_adjacency_matrix()
            new_graph.set_number_of_connections_and_density()
            new_graph.analyze_cluster_coefficients()
            new_graph.calculate_shortest_paths_for_all_nodes()
            new_graph.analyze_betweeness_centrality()
            new_graph.analyze_closessness()
            new_graph.analyze_euler()
            new_graph.analyze_hamilton()
            new_graph.analyze_bipartite()
            new_graph.analyzed = True

            if len(self.subgraphs) > 0 and len(new_graph.partitions) > len(self.subgraphs[-1].partitions):
                self.subgraphs.append(new_graph)
                self.snips.append(current_snips)
                current_snips = []

            else:
                if len(new_graph.partitions) > len(self.partitions):
                    self.subgraphs.append(new_graph)
                    self.snips.append(current_snips)
                    current_snips = []

            if self.connectivity is None and not new_graph.connected:
                self.connectivity = i

            current_graph = new_graph
            i += 1

        if self.connectivity is None:
            self.connectivity = self.min_degree if self.connected else 0

    # Overwrites for prints
    def __str__(self):
        return f"Graph: {self.name}; Nodes: {self.nodes}"

    def __repr__(self):
        return f"G: {self.name}"
