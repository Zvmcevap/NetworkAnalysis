import time
from typing import List, Optional

from classes.Graph import Graph
from classes.Node import Node


class GraphManager:
    def __init__(self):
        self.graphs: List[Graph] = []
        self.current_graph: Optional[Graph] = None

    def load_from_file(self, filename: str):
        """
        *** load_from_file ***

        Loads the graph from a file where each line in file contains either the name of 1 node (if no connection)
        or 2 connected nodes seperated by a space. The name of the graph is set to the filename automatically.

        Connections are unweighted and undirected.

        Parameter:
            - filename (str): path/to/file/filename.extension

        return (bool):
            - True if loading was successful.
            - False if it is not.
        """

        name = filename.split("/")[-1]
        if "." in name:
            name = name[: name.index(".")]
        new_graph = Graph(name)

        try:
            with open(filename) as f:
                for line in f.readlines():
                    nodes = line.strip().split()
                    if len(nodes) > 2 or len(nodes) < 1 or nodes[0] == any(
                            ["", " "]):  # If file is not properly formatted, return False
                        return False

                    node_1 = new_graph.get_node_by_name(nodes[0])
                    if node_1 is None:
                        node_1 = Node(name=nodes[0])
                        new_graph.nodes.append(node_1)

                    if len(nodes) == 1:  # In case it's a single node without a connection skip rest of the code
                        continue

                    node_2 = new_graph.get_node_by_name(nodes[1])
                    if node_2 is None:
                        node_2 = Node(name=nodes[1])
                        new_graph.nodes.append(node_2)

                    # Add neighbours to both nodes
                    if node_2 not in node_1.neighbors:
                        node_1.neighbors.append(node_2)
                    if node_1 not in node_2.neighbors:
                        node_2.neighbors.append(node_1)

        except FileNotFoundError:
            return False

        # If successful, set the new graph to current graphs and save it to the list
        self.current_graph = new_graph
        self.graphs.append(new_graph)
        return True

    def generate_kn_graph(self, n: int):
        """
        Full K-Graph

        All nodes connected to all nodes.
        """
        if "k" + str(n) in [g.name for g in self.graphs]:
            return False

        nodes = []
        for name in range(n):
            nodes.append(Node(name=str(name + 1)))

        for node in nodes:
            node.neighbors = [n for n in nodes if n != node]

        new_graph = Graph(name="k" + str(n))
        new_graph.nodes = nodes

        self.graphs.append(new_graph)
        self.current_graph = new_graph
        return True

    def generate_kxy_graph(self, x: int, y: int):
        """
        Full bipartite graph.
        All nodes of 'x' get connected to all nodes of 'y'.
        """
        if f"k{x},{y}" in [g.name for g in self.graphs]:
            return False

        left_nodes = []
        for name in range(x):
            left_nodes.append(Node(name=str(name + 1)))

        right_nodes = []
        for name in range(x, y + x):
            right_node = Node(name=str(name + 1))
            right_node.neighbors = left_nodes.copy()
            right_nodes.append(right_node)

        for left_node in left_nodes:
            left_node.neighbors = right_nodes.copy()

        new_graph = Graph(name=f"k{x},{y}")
        new_graph.nodes = left_nodes + right_nodes

        self.graphs.append(new_graph)
        self.current_graph = new_graph
        return True

    def generate_c_graph(self, n):
        """
        Vertices connected by one in front and one in back, cyclical like.
        """
        if "c" + str(n) in [g.name for g in self.graphs]:
            return False

        nodes = []
        for name in range(n):
            nodes.append(Node(name=str(name + 1)))

        for i, node in enumerate(nodes):
            node.neighbors = [nodes[(i + 1) % len(nodes)], nodes[i - 1]]

        new_graph = Graph(name="c" + str(n))
        new_graph.nodes = nodes

        self.graphs.append(new_graph)
        self.current_graph = new_graph
        return True

    def generate_q_graph(self, n):
        if "q" + str(n) in [g.name for g in self.graphs]:
            return False

        """
        So..
        The Qn graph has 2^n vertices and n * 2^(n-1) edges. Each vertex in the graph represents 
        a binary string of length n, where each digit is either 0 or 1, and two vertices are adjacent if 
        and only if their binary strings differ in exactly one position.
        """
        nodes = []
        num_vertices = 2 ** n

        for i in range(num_vertices):
            name = bin(i)[2:]
            name = "0" * (n - len(name)) + name
            nodes.append(Node(name=str(name)))

        for i in range(num_vertices):
            for j in range(i + 1, num_vertices):
                node_1 = nodes[i]
                node_2 = nodes[j]
                if node_2 in node_1.neighbors:
                    continue
                if self.q_has_connection(node_1, node_2):
                    node_1.neighbors.append(node_2)
                    node_2.neighbors.append(node_1)

        new_graph = Graph(name="q" + str(n))
        new_graph.nodes = nodes

        self.graphs.append(new_graph)
        self.current_graph = new_graph
        return True

    def q_has_connection(self, node_1, node_2):
        """
        Helper function for creating Q-hypercube graph, returns true if names of both nodes only differ by 1
        bit.
        """
        diff_count = 0
        for letter in range(len(node_1.name)):
            if node_1.name[letter] != node_2.name[letter]:
                diff_count += 1
            if diff_count > 1:
                return False
        return True

    def analyze_graph(self, sm, graph: Graph = None):
        """
        After loading or generating a new graph, perform all analysis possible on it.

        Parameter:
            - sm (StringManager): passed in to help with the printing to terminal
            - graph (Graph) (optional): if passed in use it instead of the current graph

        Returns:
            - None
        """

        analyze_recursively = False
        if graph is None:
            analyze_recursively = True
            graph = self.current_graph

        what_to_do = ["Calculating Degrees of Node: ",
                      "Creating Adjacency Matrix",
                      "Counting Connections",
                      "Declustering Clustering Coefficients",
                      "Calculating Paths",
                      "Building Bridges In Between",
                      "Keeping Friends Close",
                      "Is Euler?",
                      "Is Hamiltion?",
                      "To bipartite or not to bipartite"]

        if analyze_recursively:
            what_to_do.append("Community matters")

        total = len(what_to_do)

        graph.sort_nodes_by_name()
        for i, analysis in enumerate(what_to_do):
            if i == 0:
                sm.print_progress(current=i, total=total, flavour_text=analysis)
                graph.set_node_degrees()

            if i == 1:
                sm.print_progress(current=i, total=total, flavour_text=analysis)
                graph.set_adjacency_matrix()

            elif i == 2:
                sm.print_progress(current=i, total=total, flavour_text=analysis)
                graph.set_number_of_connections_and_density()

            elif i == 3:
                sm.print_progress(current=i, total=total, flavour_text=analysis)
                graph.analyze_cluster_coefficients()

            elif i == 4:
                sm.print_progress(current=i, total=total, flavour_text=analysis)
                graph.calculate_shortest_paths_for_all_nodes()

            elif i == 5:
                sm.print_progress(current=i, total=total, flavour_text=analysis)
                graph.analyze_betweeness_centrality()

            elif i == 6:
                sm.print_progress(current=i, total=total, flavour_text=analysis)
                graph.analyze_closessness()

            elif i == 7:
                sm.print_progress(current=i, total=total, flavour_text=analysis)
                graph.analyze_euler()

            elif i == 8:
                sm.print_progress(current=i, total=total, flavour_text=analysis)
                graph.analyze_hamilton()

            elif i == 9:
                sm.print_progress(current=i, total=total, flavour_text=analysis)
                graph.analyze_bipartite()

            elif i == 10:
                sm.print_progress(current=i, total=total, flavour_text=analysis)
                graph.analyze_communities()

        graph.analyzed = True


gm = GraphManager()
