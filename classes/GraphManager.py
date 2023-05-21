import random
import time
from typing import List, Optional, Union

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

        nodes = []
        for name in range(n):
            nodes.append(Node(name=str(name + 1)))

        for node in nodes:
            node.neighbors = [n for n in nodes if n != node]

        new_graph = Graph(name="k" + str(n))
        new_graph.nodes = nodes
        return new_graph

    def generate_knm_graph(self, n: int, m: int):
        """
        Full bipartite graph.
        All nodes of 'x' get connected to all nodes of 'y'.
        """

        left_nodes = []
        for name in range(n):
            left_nodes.append(Node(name=str(name + 1)))

        right_nodes = []
        for name in range(n, m + n):
            right_node = Node(name=str(name + 1))
            right_node.neighbors = left_nodes.copy()
            right_nodes.append(right_node)

        for left_node in left_nodes:
            left_node.neighbors = right_nodes.copy()

        new_graph = Graph(name=f"k{n},{m}")
        new_graph.nodes = left_nodes + right_nodes

        return new_graph

    def generate_c_graph(self, n):
        """
        Vertices connected by one in front and one in back, cyclical like.
        """
        nodes = []
        for name in range(n):
            nodes.append(Node(name=str(name + 1)))

        for i, node in enumerate(nodes):
            node.neighbors = [nodes[(i + 1) % len(nodes)], nodes[i - 1]]

        new_graph = Graph(name="c" + str(n))
        new_graph.nodes = nodes

        return new_graph

    def generate_q_graph(self, n) -> Graph:
        """
        So...
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

        return new_graph

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

    def generate_petersen_graph(self):
        k5 = self.generate_kn_graph(n=5)
        c5 = self.generate_c_graph(n=5)
        new_graph = Graph(name="petersen")

        for i in range(5):
            k_node = k5.nodes[i]
            k_node.neighbors.remove(k5.nodes[i - 1])
            k_node.neighbors.remove(k5.nodes[(i + 1) % 5])
            c_node = c5.nodes[i]
            k_node.name = f"k{i}"
            c_node.name = f"c{i}"
            k_node.neighbors.append(c_node)
            c_node.neighbors.append(k_node)

            new_graph.nodes.append(k_node)
            new_graph.nodes.append(c_node)
        return new_graph

    def generate_kmecki_random_graph(self, n: int, e: int):
        """
        Generate an Erdos-Renyi random graph, take a number of nodes and edges and
        randomly throw them in the graph. The "Kmecki"-way

        Parameters:
            - n (int): number of nodes
            - e (int): number of edges

        Returns:
             - Graph
        """
        new_graph = Graph(name=f"random-{len([g for g in self.graphs if g.name[:7] == 'random'])}")

        for node_name in range(n):
            new_node = Node(name=str(node_name))
            new_graph.nodes.append(new_node)

        edges = []
        if e > (n ** 2 - n) // 2:
            e = (n ** 2 - n) // 2

        for edge in range(e):
            new_edge = random.sample(new_graph.nodes, k=2)
            while set(new_edge) in edges:
                new_edge = random.sample(new_graph.nodes, k=2)
            edges.append(set(new_edge))
            new_edge[0].neighbors.append(new_edge[1])
            new_edge[1].neighbors.append(new_edge[0])
        return new_graph

    def generate_math_random_graph(self, n: int, p: int):
        """
        Generate an Erdos-Renyi random graph, take a number of nodes and probability of an edge between another node
        for pairs between all nodes. The "mathematical"-way.

        Parameters:
            - n (int): number of nodes
            - p (int): probability of an edge, compared to a random integer between 0 and 100

        Returns:
             - Graph
        """
        new_graph = Graph(name=f"random-{len([g for g in self.graphs if g.name[:7] == 'random'])}")

        for node_name in range(n):
            new_node = Node(name=str(node_name))
            new_graph.nodes.append(new_node)

        for i, first_node in enumerate(new_graph.nodes):
            for j in range(i + 1, len(new_graph.nodes)):
                second_node = new_graph.nodes[j]
                if random.randint(0, 100) >= p:
                    first_node.neighbors.append(second_node)
                    second_node.neighbors.append(first_node)
        return new_graph

    def generate_graph(self, g_type: str, numeric_args: Union[int, List[int], None] = None) -> bool:
        """
        Saves the graph we are generating as the current graph, if successful

        Parameters:
            - g_type (string): the type of graph we are making (hypercube, cycle, complete, petersen, natural)
            - numeric_args (int) (List of ints): integer or list of integers, needed to successfully generate a graph

        Returns:
             - True: if successful
             - False: if graph is already in memory
        """
        new_graph = None

        if g_type == "q":
            if "q" + str(numeric_args) in [g.name for g in self.graphs]:
                return False
            new_graph = self.generate_q_graph(n=numeric_args)
        if g_type == "c":
            if "c" + str(numeric_args) in [g.name for g in self.graphs]:
                return False
            new_graph = self.generate_c_graph(n=numeric_args)
        if g_type == "kn":
            if "k" + str(numeric_args) in [g.name for g in self.graphs]:
                return False
            new_graph = self.generate_kn_graph(n=numeric_args)
        if g_type == "knm":
            if f"k{numeric_args[0]},{numeric_args[1]}" in [g.name for g in self.graphs]:
                return False
            new_graph = self.generate_knm_graph(n=numeric_args[0], m=numeric_args[1])
        if g_type == "p":
            if "petersen" in [g.name for g in self.graphs]:
                return False
            new_graph = self.generate_petersen_graph()

        if g_type == "kr":
            new_graph = self.generate_kmecki_random_graph(n=numeric_args[0], e=numeric_args[1])

        if g_type == "mr":
            new_graph = self.generate_math_random_graph(n=numeric_args[0], p=numeric_args[1])

        if g_type == "n":
            pass

        if new_graph is None:
            return False

        self.graphs.append(new_graph)
        self.current_graph = new_graph
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
