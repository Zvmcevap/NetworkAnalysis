from operator import attrgetter
import os
import time
from typing import Dict, List, Optional

from classes.GraphManager import GraphManager
from classes.Node import Node


class StringManager:
    """
    *** String Manager Class ***

    This class bundles up all the code used to print the data to the terminal.

    Inspired mainly by the "tqdm" library and by what I find easy on the eye, the terminal gets cleared between each
    writes.

    Attributes:
        - graph (graph) (Optional): current graph being displayed, if one is loaded.
        - colors (Dict[str, str]): Dictionary of different colors available in the terminal.

    Methods:
        - print: takes a string and prints it to the terminal after clearing it
        - clear_terminal: clears the terminal, hopefully successfully...

        - *_string methods: these methods return a specific string, so it can be used elsewhere.
        - print_* methods: print a specific string or a combination of strings to the terminal.
    """

    def __init__(self, GraphManager: GraphManager):
        self.GM: GraphManager = GraphManager
        self.colors = {
            "default": "\033[0m",
            "black": "\033[30m",
            "red": "\033[31m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "blue": "\033[34m",
            "magenta": "\033[35m",
            "cyan": "\033[36m",
            "white": "\033[37m"
        }

    def progress_string(self, current: int, total: int, flavour_text=None):
        """
        *** progress_string ***

        Create and return a loading style progress string based on current/total percent value with optional text above.

        Parameters:
            - current (int): of the current iteration of a loop, or an equivalent int representation of completed progress.
            - total (int): the full amount of tasks needed for completion.
            - flavour_text (str) (optional): adds optional text on top of the progress bar.

        return:
            - string
        """
        cp = current * 100 // total
        color = "red" if cp < 33 else "yellow" if cp < 66 else "green"

        flavour_text = self.color(color, " " * (25 - 3 - len(flavour_text) // 2) + "*** " + flavour_text + " ***")
        perc_string = self.color(color, f"|" + "#" * (cp // 2))
        perc_string += f'{"-" * (51 + 4 - len(perc_string))}| {str(cp)}% - {current}/{total}'

        return f"{flavour_text}\n" + perc_string

    def print_progress(self, current, total, flavour_text=None):
        # Prints the progress_string to terminal.
        self.print(self.progress_string(current, total, flavour_text))

    """
    Adjacency Matrix
    """

    def get_am_string(self):
        if self.GM.current_graph is None:
            return ""

        am = self.GM.current_graph.am
        nodes = self.GM.current_graph.nodes

        # Get string representation of the adjacency matrix to print to terminal
        if len(am) == 0:
            return "There is no adjacency matrix."

        # This will get complicated, I am trying to make it pretty
        su = "\033[4m"  # start underscore
        eu = "\033[0m"  # end underscore

        node_names = [node.name for node in nodes]
        biggest_name = max([len(name) for name in node_names])
        node_names = [" " * (biggest_name - len(name)) + name for name in node_names]  # Getting better at it

        first_row = su + " " * (biggest_name - 1) + "V|" + " " + " ".join(node_names) + eu + "\n"
        center_it = " " * (40 - len(first_row) // 2)
        first_row = center_it + first_row

        for i, row in enumerate(am):
            row_values = []
            for col in row:
                if col == 0:
                    row_values.append(self.color("blue", str(col)))
                else:
                    row_values.append(self.color("yellow", str(col)))

            row_string = center_it + node_names[i] + "| " + " ".join(
                [" " * (biggest_name - 1) + col for col in row_values]) + "\n"
            first_row += row_string
        first_row = " " * 23 + "*** ADJACENCY MATRIX ***" + "\n\n" + first_row
        return first_row

    def print_am(self):
        self.print(sentence=self.get_am_string())

    def print_euler_string(self):
        odd_nodes = [node for node in self.GM.current_graph.nodes if node.degree % 2 == 1]

        if self.GM.current_graph.euler_path is None:
            if not self.GM.current_graph.connected:
                string_to_print = f"    Euler Path and Circuit impossible because the graph is unconnected!"
            else:
                string_to_print = f"    Euler Path and Circuit impossible because {len(odd_nodes)} have odd degrees!"
            string_to_print = self.color("red", string_to_print)

            if self.GM.current_graph.connected:
                blah = f"\n\n    Nodes to blame!\n{self.get_nodes_list_string(odd_nodes, 'red')}"
                string_to_print += self.color("red", blah)

        elif self.GM.current_graph.euler_circuit is None:
            string_to_print = f"\n            {self.color('cyan', '*** Euler Path ***')}\n\n"
            string_to_print += self.get_path_string(path=self.GM.current_graph.euler_path) + "\n\n"
            string_to_print += self.color("red",
                                          f"       Euler Circuit impossible because {len(odd_nodes)} have odd degrees!")
            string_to_print += f"\n\n    Criminal Nodes = {self.get_nodes_list_string(odd_nodes, 'red')}"

        else:
            string_to_print = f"\n                {self.color('cyan', '************* Euler Path *************')}\n\n"
            string_to_print += self.get_path_string(path=self.GM.current_graph.euler_path) + "\n\n"
            string_to_print += f"\n               {self.color('cyan', '************* Euler Circuit *************')}\n\n"
            string_to_print += self.get_path_string(path=self.GM.current_graph.euler_circuit)

        self.print(sentence=string_to_print)

    def print_hamilton_string(self):
        if self.GM.current_graph.hamilton_path is None:
            if not self.GM.current_graph.connected:
                string_to_print = f"  Hamilton Path and Circuit impossible because the graph is unconnected!"
            else:
                string_to_print = f"           Hamilton Path and Circuit impossible because reasons!"
            string_to_print = self.color("red", string_to_print)

        elif self.GM.current_graph.hamilton_circuit is None:
            string_to_print = f"\n         {self.color('cyan', '*** Hamilton Path ***')}\n\n"
            string_to_print += self.get_path_string(path=self.GM.current_graph.hamilton_path) + "\n\n"
            string_to_print += self.color("red", f"          Hamilton Circuit impossible because I can't find it...")
        else:
            string_to_print = f"\n             {self.color('cyan', '************* Hamilton Path *************')}\n\n"
            string_to_print += self.get_path_string(path=self.GM.current_graph.hamilton_path) + "\n\n"
            string_to_print += f"\n            {self.color('cyan', '************* Hamilton Circuit *************')}\n\n"
            string_to_print += self.get_path_string(path=self.GM.current_graph.hamilton_circuit)

        self.print(sentence=string_to_print)

    def print_bipartite_string(self):
        if not self.GM.current_graph.bipartite:
            string_to_print = f"\n         {self.color('red', '*** Graph is NOT Bipartite ***')}\n\n"
            string_to_print += f"\n        {self.color('blue', 'Odd cycle to blame:')}\n\n"
            string_to_print += self.get_path_string(path=self.GM.current_graph.odd_cycle) + "\n\n"
        else:
            magenta_nodes = self.get_nodes_list_string(
                [node for node in self.GM.current_graph.nodes if node.color == "magenta"], 'magenta')
            cyan_nodes = self.get_nodes_list_string(
                [node for node in self.GM.current_graph.nodes if node.color == "cyan"], 'cyan')

            string_to_print = f"\n         {self.color('blue', '************* Bipartite Graph *************')}\n"
            string_to_print += f"\n     {self.color('magenta', 'Magenta Nodes:')}"
            string_to_print += f"         {self.color('magenta', magenta_nodes)}\n\n"

            string_to_print += f"\n     {self.color('cyan', 'Cyan Nodes:')}"
            string_to_print += f"         {self.color('cyan', cyan_nodes)}\n"

        self.print(sentence=string_to_print)

    def print_partitions(self):
        string_to_print = self.get_partition_string()
        self.print(sentence=string_to_print)

    def get_partition_string(self, communities: bool = False, graph=None):
        if graph is None:
            graph = self.GM.current_graph

        x = "partitions" if not communities else "communities"
        y = "Partition" if not communities else "Community"
        colors = ['cyan', 'magenta']
        if not communities:
            string_to_print = f"\n         {self.color('blue', f'************* Graph has {len(graph.partitions)} {x} *************')}\n"
        else:
            string_to_print = "\n"
        for i, partition in enumerate(graph.partitions):
            nodes = self.get_nodes_list_string(list(partition), colors[i % 2])
            string_to_print += f"\n     {self.color(color=colors[i % 2], text=f'{y} {i + 1}:')}"
            string_to_print += nodes + "\n"

        return string_to_print

    def get_community_string(self):
        subs = self.GM.current_graph.subgraphs
        snips = self.GM.current_graph.snips

        total_subs = len(subs)

        if total_subs == 0:
            if self.GM.current_graph.connected:
                return f"\n         {self.color('red', f'************* Graph has NO Communities *************')}\n"

        main_string = self.get_partition_string(communities=True) + "\n"

        for i in range(total_subs):
            new_snips = snips[i]
            snips_string = "    Connections Broken: "
            for j in range(len(new_snips)):
                if j % 3 == 0:
                    snips_string += "\n"
                a_snip = self.get_edge_string(new_snips[j])
                snips_string += "    " + a_snip

            sub_graph = subs[i]
            main_string += f"\n         {self.color('blue', f'************* SUBGRAPH {i + 1} *************')}\n"
            main_string += snips_string
            main_string += self.get_partition_string(communities=True, graph=sub_graph) + "\n"
        return main_string

    def print_social_distances(self, node: Node):
        colors = ['cyan', 'magenta']
        string_to_print = f"\n         {self.color('blue', f'***** Nodes {node.name} Social Distances *****')}\n"

        all_paths = []
        unavailables = set()
        max_steps = 0 if len(node.neighbors) == 0 else 1

        for n in node.paths:
            if node.paths[n] is None:
                unavailables.add(n)
                continue
            for path in node.paths[n]:
                all_paths.append(path)
                if len(path) > max_steps:
                    max_steps = len(path)

        for i in range(1, max_steps):
            nodes = set()
            if i == 1:
                nodes = set(node.neighbors)
            else:
                for path in all_paths:
                    if len(path) > i:
                        nodes.add(path[i])

            nodes_string = self.get_nodes_list_string(list(nodes), colors[i % 2])
            string_to_print += f"\n     {self.color(color=colors[i % 2], text=f'Social Distance: {i}:')}"
            string_to_print += nodes_string + "\n"

        if len(unavailables) > 0:
            nodes_string = self.get_nodes_list_string(list(unavailables), "red")
            string_to_print += f"\n     {self.color('red', text=f'---- Unreachable Nodes! ----')}"
            string_to_print += nodes_string + "\n"

        self.print(sentence=string_to_print)

    """
    Strings that are always on the terminal
    """

    def get_title_string(self):
        graph_name = "NO GRAPH LOADED" if self.GM.current_graph is None else self.GM.current_graph.name.upper()
        color = "yellow" if self.GM.current_graph is None else "green"

        top = "*" * 70 + "\n"
        mid = " " * (70 // 2 - len(graph_name) // 2 - 4) + "*** " + graph_name + " ***" + "\n"
        bot = "*" * 70 + "\n"

        return self.color(color, top + mid + bot)

    def get_graph_details(self):
        if self.GM.current_graph is None or not self.GM.current_graph.analyzed:
            return ""

        graph = self.GM.current_graph

        data = {}
        data["Nodes: "] = str(len(graph.nodes))
        data["Min Degree: "] = str(graph.min_degree)

        data["Edges: "] = str(graph.number_of_edges)
        data["Max Degree: "] = str(graph.max_degree)

        data["Density: "] = f"{graph.density:.2f}"
        data["Avg Degree: "] = f"{graph.average_degree:.2f}"

        data["-----------*"] = "*------------"
        data["-------------*"] = "*------------"

        data["Max Cluster Coef: "] = f'{graph.max_cluster_coefficient:.2f}'
        data["Max Betweeness: "] = f'{graph.max_betweeness:.2f}'

        data["Min Cluster Coef: "] = f"{graph.min_cluster_coefficient:.2f}"
        data["Min Betweeness: "] = f'{graph.min_betweeness:.2f}'

        data["Avg Cluster Doef: "] = f"{graph.average_cluster_coefficient:.2f}"
        data["Avg Betweeness: "] = f'{graph.average_betweeness:.2f}'

        data["-----------"] = "------------"
        data["-------------"] = "------------"

        data["Partitions: "] = str(len(self.GM.current_graph.partitions))
        data["Max Communities: "] = "0" if len(graph.subgraphs) == 0 else f'{len(graph.subgraphs[-1].partitions)}'

        data["Connected: "] = "YES" if graph.connected else "NO"
        data["Avg Edge Betweeness"] = f"{graph.avg_edge_betweeness:.2f}"

        data["Connectivity: "] = f"{graph.connectivity}"
        data["Bipartite: "] = "YES" if graph.bipartite else "NO"

        data["Diameter: "] = str(graph.diameter)
        data["Avg Path Length: "] = f"{graph.average_path_length:.2f}"

        data["Euler Path: "] = "NO" if graph.euler_path is None else "YES"
        data["Hamilton Path: "] = "NO" if graph.hamilton_path is None else "YES"

        data["Euler Circuit: "] = "NO" if graph.euler_circuit is None else "YES"
        data["Hamilton Circuit: "] = "NO" if graph.hamilton_circuit is None else "YES"

        lines = []
        line = ""
        for i, info in enumerate(data):
            if i % 2 == 0:
                line += " " * (20 - len(info)) + self.color("blue", info) + data[info]
            else:
                line += " " * (60 - len(info) - len(line)) + self.color("blue", info) + data[info]
                lines.append(line)
                line = ""

        stars = self.color("green", "\n" + "*" * 70)
        lines.append(stars)

        return "\n".join(lines)

    def get_options_string(self, options: List[str], optional_text=None):
        if options is None:
            return ""

        # Options title
        options_title = "*** OPTIONS ***" if optional_text == "" else f"***  {optional_text.upper()}  ***"
        options_title = " " * (35 - len(options_title) // 2) + options_title
        options_title = self.color("green", options_title) + "\n"

        # List Options
        biggest_option = max(len(opt) for opt in options)

        options_string = ""
        for i, opt in enumerate(options):
            option = "        " + opt + " " * (biggest_option - len(opt))
            if opt == "b-back":
                option = "" + self.color("yellow", option)
            if opt == "q-quit":
                option = "" + self.color("red", option)

            if i % 3 == 0:
                options_string += "\n"
            options_string += option

        return options_title + options_string

    """
    Node specific strings
    """

    def get_path_string(self, path: List[Node]):
        biggest_name = max([len(node.name) for node in path])
        names_per_line = 60 // (biggest_name + 4)

        arrow = " -> "
        path_list = []
        path_string = " " * 4
        for i, node in enumerate(path):
            name = " " * (biggest_name - len(node.name)) + node.name
            if i != 0 and i % names_per_line == 0:
                path_list.append(path_string + arrow + "\n")
                path_string = " " * 4
            if i == 0:
                path_string += "    " + self.color("green", name)
            elif i == len(path) - 1:
                col = "green" if node == path[0] else "blue"
                path_string += arrow + self.color(col, name)

            else:
                path_string += arrow + self.color("yellow", name)

        path_list.append(path_string)
        finished_string = "".join(path_list)
        return finished_string

    def get_all_paths_of_node_string(self, node, empties_only=False, bridges=False, finish: Optional[Node] = None):
        main_string = ""
        main_string += "\n\n     " + self.color("green", f"********** NODE: {node.name} **********") + "\n"

        if not empties_only and not bridges:
            for neighbor in node.neighbors:
                if finish is None or neighbor == finish:
                    main_string += self.get_path_string(path=[node, neighbor]) + "\n"

        if bridges:
            for path in node.bridge_paths:
                main_string += self.get_path_string(path) + "\n"

        else:
            for n in node.paths:
                if finish is not None and n != finish:
                    continue
                if node.paths[n] is not None and not empties_only:
                    for path in node.paths[n]:
                        main_string += self.get_path_string(path) + "\n"
                else:
                    start_name = "        " + self.color("green", node.name)
                    goal_name = self.color("blue", n.name)
                    main_string += start_name + self.color("red", " - no path to - ") + goal_name + "\n"

        return main_string

    def get_nodes_list_string(self, nodes: List[Node], color: str = "default"):
        spaces = "    "
        if len(nodes) == 0:
            return ""
        biggest_name = max([len(n.name) for n in nodes])
        nodes_per_line = 60 // biggest_name

        main_string = ""
        for i, node in enumerate(nodes):
            if i % nodes_per_line == 0:
                main_string += "\n" + spaces
            else:
                main_string += ", "
            main_string += " " * (biggest_name - len(node.name) + 1) + node.name
        return self.color(color, main_string)

    def print_all_paths(self, bridges=False):
        main_string = ""
        for node in self.GM.current_graph.nodes:
            main_string += self.get_all_paths_of_node_string(node=node, bridges=bridges)
        self.print(sentence=main_string)

    def get_edge_string(self, edge):
        main_string = ""
        for i, node in enumerate(edge):
            main_string += self.color("green", node.name)
            if i == 0:
                main_string += self.color("blue", " <<====>> ")
        return main_string

    def print_edge_bridges(self, bridges=False):
        main_string = "    "
        for edge in self.GM.current_graph.edge_bridges:
            main_string += "\n" + self.color("blue", "EDGE: ")
            for i, node in enumerate(edge):
                main_string += self.color("green", node.name)
                if i == 0:
                    main_string += self.color("blue", " <<====>> ")
            main_string += "\n"
            for path in self.GM.current_graph.edge_bridges[edge]:
                main_string += "\n" + self.get_path_string(path)
            main_string += "\n"
        self.print(sentence=main_string)

    def print_edge_betweeness(self):
        main_string = ""
        for edge in self.GM.current_graph.edge_betweeness:
            main_string += "\n     " + self.color("blue", "EDGE: ")
            for i, node in enumerate(edge):
                main_string += self.color("green", node.name)
                if i == 0:
                    main_string += self.color("blue", " <<====>> ")
            betweeness = f"{self.GM.current_graph.edge_betweeness[edge]:.2f}"

            main_string += "\n           Betweeness: " + self.color("yellow", betweeness) + "\n"
        self.print(sentence=main_string)

    def get_node_string(self, node):
        graph = self.GM.current_graph
        col = ["red", "yellow"]
        name_string = " " * (8 - len(node.name)) + self.color("green", node.name)

        degree_col = col[1]
        degree_string = " " * (8 - len(str(node.degree))) + self.color(degree_col, str(node.degree))

        ccol = col[0] if node.clustering_coefficient is None else col[1]
        cluster = "NONE" if node.clustering_coefficient is None else f"{node.clustering_coefficient:.2f}"
        cluster_string = " " * (8 - len(cluster)) + self.color(ccol, cluster)

        betw_col = col[0] if node.betweeness is None else col[1]
        betw = "NONE" if node.betweeness is None else f"{node.betweeness:.2f}"
        between_string = " " * (8 - len(betw)) + self.color(betw_col, betw)

        bridge_col = col[0] if node.bridge_paths is None else col[1]
        bridge = "NONE" if node.bridge_paths is None else f"{len(node.bridge_paths)}"
        bridge_string = " " * (8 - len(bridge)) + self.color(bridge_col, bridge)

        close_col = col[0] if node.closeness is None else col[1]
        close = "NONE" if node.closeness is None else f"{node.closeness:.2f}"
        close_string = " " * (8 - len(close)) + self.color(close_col, close)

        neighbors = "    " + ", ".join([n.name for n in node.neighbors])
        neighbors = self.color("green", neighbors)

        return name_string + degree_string + cluster_string + between_string + bridge_string + close_string + neighbors

    def get_nodes_table_string(self, nodes: List[Node], sorter: str = "name"):
        main_string = "\n    NODE     DGR    CLST    BETW    BRIDG    CLOS    NEIGHBORS\n"  # 8, 4
        main_string = self.color("blue", main_string)
        nodes_copy = nodes.copy()
        nodes_copy.sort(key=attrgetter(sorter), reverse=True)
        for node in nodes_copy:
            main_string += "\n" + self.get_node_string(node)

        return main_string

    def get_specific_node_string(self, node: Node):
        main_string = f"**** NODE: {node.name} ****"
        main_string = "\n" + " " * (35 - len(main_string) // 2) + self.color("blue", main_string) + "\n\n"

        data = {"Degree: ": str(node.degree),
                "Betweeness: ": f"{node.betweeness:.2f}",
                "Closeness: ": f"{node.closeness:.2f}",
                "Parts of a Bridge: ": f"{len(node.bridge_paths)} times",
                "Clustering Coefficient: ": f"{node.clustering_coefficient:.2f}",
                }

        lines = [main_string]
        line = ""
        for i, info in enumerate(data):
            if i % 2 == 0:
                line += " " * (20 - len(info)) + self.color("blue", info) + self.color("yellow", data[info])
            else:
                line += " " * (65 - len(info) - len(line)) + self.color("blue", info) + self.color("yellow", data[info])
                lines.append(line)
                line = ""

        neighbors = "\n" + self.color("green", "    Neighboring nodes: \n")
        neighbors += self.get_nodes_list_string(node.neighbors, "green") + "\n"
        lines.append(neighbors)
        stars = self.color("blue", "\n" + "*" * 70)
        lines.append(stars)
        return "\n".join(lines)

    """
    Helper strings to pretty up the rest of the app
    """

    def color(self, color: str, text: str):
        return self.colors[color] + text + self.colors["default"]

    def clear_terminal(self):
        # To have it looking like an app, the terminal will get cleared before writing something new to it
        if 'TERM' not in os.environ:  # Trying to fix a weird Pycharm bug here, but it doesn't work too well
            os.environ['TERM'] = 'xterm'
            print(os.environ['TERM'])

        os.system('cls' if os.name == 'nt' else 'clear')
        print("\033[2J")  # Clear the entire screen

    def print(self,
              sentence: str,
              options: List[str] = None,
              wrong_command: bool = False,
              opt_text: str = ""
              ):
        self.clear_terminal()

        title = self.get_title_string()
        graph_details = self.get_graph_details()
        opt_str = self.get_options_string(options=options, optional_text=opt_text)
        sentence = " " * (35 - len(sentence) // 2) + sentence

        wrong_str = "\n" + self.color("red", "                        *** WRONG INPUT ***")
        wrong_str = wrong_str if wrong_command else ""

        print(f"{title}\n{graph_details}\n\n\n{sentence}\n\n\n{opt_str}\n{wrong_str}")

    """
    
    
    
    
    #####################################################################################################
    USER INTERFACE - Putting them here to free up main.py
    #####################################################################################################
    
    Couple of main groups of methods:
        - helper methods: get integer from user, may find others
        - loading and generating graphs
        - analyzing graphs and subgraphs
    """

    """
    Helper methods
    """

    def get_integer(self, optional_text: str = ""):
        n = None
        wrong_command = False
        while n is None:
            self.print(sentence=optional_text, wrong_command=wrong_command)
            command = input("Enter an integer or b for back: ")
            if command == "b":
                return None
            elif command.isdigit():
                return int(command)
            else:
                wrong_command = True

    """
    Loading and generating
    """

    def load_graph(self):
        wrong_command = False
        while True:
            self.print(sentence="",
                       options=['f-file', f'm-memory [{len(self.GM.graphs)}]', 'b-back'],
                       wrong_command=wrong_command,
                       opt_text='Load graph from: '
                       )
            command = input("Enter command: ")
            if command == "b":
                return False

            elif command == "m":
                wrong_command = False
                while True:
                    if len(self.GM.graphs) == 0:
                        self.print(sentence="",
                                   opt_text="No graph in memory",
                                   options=[""])
                        input("Press Enter")
                        wrong_command = False
                        break

                    options = [g.name for g in self.GM.graphs]
                    self.print(sentence="Select graph by name",
                               options=options,
                               opt_text="available graph names",
                               wrong_command=wrong_command
                               )
                    command = input("Enter graph name or b for back: ")
                    if command == "b":
                        wrong_command = False
                        break
                    elif command in options:
                        self.GM.current_graph = [g for g in self.GM.graphs if g.name == command][0]
                        return True
                    else:
                        wrong_command = True

            elif command == "f":
                wrong_command = False
                while True:
                    opt_text = "Enter filename" if not wrong_command else "Enter a filename that exists on your drive"
                    sentence = "    Available: " + self.color('green', 'test.txt, quiz.txt, star.txt')
                    sentence += "\n    Plus others you might have on your hard drive."
                    self.print(sentence=sentence,
                               wrong_command=wrong_command,
                               options=[''],
                               opt_text=opt_text
                               )
                    filename = input("Enter filename or b for back: ")

                    if filename == "b":
                        wrong_command = False
                        break
                    elif self.GM.load_from_file(filename=filename):
                        self.GM.analyze_graph(sm=self)
                        return True
                    else:
                        wrong_command = True
            else:
                wrong_command = True

    def generate_graph(self):
        wrong_command = False
        while True:
            self.print(sentence="Generate a famous graph!",
                       options=["kn-full", "kxy-full bipartite", "c-cycle", "q-hypercube", "b-back"],
                       wrong_command=wrong_command
                       )
            command = input("Enter: ")
            if command == "b":
                return False

            elif command == "kn":
                n = self.get_integer(f"Complete Graph Kn; Enter number of vertices.")
                if n is None:
                    wrong_command = False
                    continue
                if not self.GM.generate_kn_graph(n=n):
                    self.print(sentence="This graph was already generated",
                               opt_text="load it from memory",
                               options=[""])
                    input("Press Enter")
                    return False
                self.GM.analyze_graph(sm=self)
                return True

            elif command == "kxy":
                x = self.get_integer(f"Full Bipartite Graph Kx,y; Enter a value for x.")
                if x is None:
                    wrong_command = False
                    continue
                y = self.get_integer(f"Full Bipartite Graph Kx,y; x = {x}, enter value for y.")
                if y is None:
                    wrong_command = False
                    continue
                if not self.GM.generate_kxy_graph(x=x, y=y):
                    self.print(sentence="This graph was already generated",
                               opt_text="load it from memory",
                               options=[""])
                    input("Press Enter")
                    return False
                self.GM.analyze_graph(sm=self)
                return True

            elif command == "c":
                n = self.get_integer("Cycle Graph Cn, enter number of vertices.")
                if n is None:
                    wrong_command = False
                    continue
                if not self.GM.generate_c_graph(n=n):
                    self.print(sentence="This graph was already generated",
                               opt_text="load it from memory",
                               options=[""])
                    input("Press Enter")
                    return False
                self.GM.analyze_graph(sm=self)
                return True

            elif command == "q":
                n = self.get_integer("Hypercube Graph Qn, enter the number of dimensions n.")
                if n is None:
                    wrong_command = False
                    continue
                if not self.GM.generate_q_graph(n=n):
                    self.print(sentence="This graph was already generated",
                               opt_text="load it from memory",
                               options=[""])
                    input("Press Enter")
                    return False
                self.GM.analyze_graph(sm=self)
                return True
            else:
                wrong_command = True

    """
    Analyzing graphs and nodes
    """

    def graph_analysis(self):
        wrong_command = False
        while True:
            self.print(sentence="",
                       options=[
                           "n-node details",
                           "cm-communities and subgraphs",
                           "am-adjacency matrix",
                           "e-euler",
                           "h-hamilton",
                           "bp-bipartite",
                           "p-partitions",
                           "b-back"
                       ],
                       wrong_command=wrong_command
                       )
            command = input("Enter: ")

            if command == "b":
                return

            elif command == "cm":
                wrong_command = False
                self.communities_analysis()

            elif command == "am":
                wrong_command = False
                self.print_am()
                input("Enter for back")

            elif command == "e":
                wrong_command = False
                self.print_euler_string()
                input("Enter for back")

            elif command == "h":
                wrong_command = False
                self.print_hamilton_string()
                input("Enter for back")

            elif command == "bp":
                wrong_command = False
                self.print_bipartite_string()
                input("Enter for back")

            elif command == "p":
                wrong_command = False
                self.print_partitions()
                input("Enter for back")

            elif command == "n":
                wrong_command = False
                self.node_analysis()

            else:
                wrong_command = True

    def communities_analysis(self):
        wrong_command = False
        comm_string = self.get_community_string()
        option = ["b-back"]
        if len(self.GM.current_graph.subgraphs) + len(self.GM.current_graph.partitions) > 0:
            option.insert(0, "n-to load a specific n-subgraph for analysis")

        while True:
            self.print(sentence=comm_string,
                       options=option,
                       wrong_command=wrong_command
                       )
            command = input("Enter: ")
            if command == "b":
                return

            elif command.isdigit() and len(self.GM.current_graph.subgraphs) > int(command):
                wrong_command = False
                main_graph = self.GM.current_graph
                self.GM.current_graph = main_graph.subgraphs[int(command)]
                self.graph_analysis()
                self.GM.current_graph = main_graph

            elif command == "e":
                wrong_command = False
                self.print_euler_string()
                input("Enter for back")

    def node_analysis(self):
        wrong_command = False
        sorter = "name"
        while True:
            nodes_string = self.get_nodes_table_string(self.GM.current_graph.nodes, sorter)
            self.print(sentence=nodes_string,
                       options=["s-sort nodes",
                                "node_name-access specific node",
                                "ap-all paths from all nodes",
                                "nb-all bridges for all nodes",
                                "eb-edge betweeness",
                                "b-back"],
                       wrong_command=wrong_command
                       )
            command = input("Enter: ")

            if command == "b":
                return

            elif command == "s":
                sorting = True
                while sorting:
                    self.print(sentence=nodes_string,
                               opt_text="Sort nodes by",
                               options=["n-name",
                                        "d-degree",
                                        "cc-clustering coefficient",
                                        "bt-betweeness",
                                        "cl-closeness",
                                        "b-back"],
                               wrong_command=wrong_command
                               )
                    command = input("Enter Command: ")
                    if command == "n":
                        wrong_command = False
                        sorter = "name"
                        sorting = False
                    elif command == "d":
                        wrong_command = False
                        sorter = "degree"
                        sorting = False
                    elif command == "cc":
                        wrong_command = False
                        sorter = "clustering_coefficient"
                        sorting = False
                    elif command == "bt":
                        wrong_command = False
                        sorter = "betweeness"
                        sorting = False
                    elif command == "cl":
                        wrong_command = False
                        sorter = "closeness"
                        sorting = False
                    elif command == "b":
                        sorting = False
                    else:
                        wrong_command = True

            elif command == "nb":
                wrong_command = False
                self.print_all_paths(bridges=True)
                input("Enter for back")

            elif command == "bp":
                wrong_command = False
                self.print_bipartite_string()
                input("Enter for back")

            elif command == "eb":
                wrong_command = False
                self.print_edge_betweeness()
                input("Enter for back")

            elif command == "ap":
                wrong_command = False
                self.print_all_paths()
                input("Enter for back")

            else:
                if command in [node.name for node in self.GM.current_graph.nodes]:
                    node = self.GM.current_graph.get_node_by_name(command)
                    self.node_ui(node)

                else:
                    wrong_command = True

    def node_ui(self, node: Node):
        wrong_command = False

        while True:
            node_string = self.get_specific_node_string(node)
            self.print(sentence=node_string,
                       options=["f-find path to another node",
                                "s-social distances",
                                "ap-all paths from all nodes",
                                "nb-all bridges for all nodes",
                                "eb-edge betweeness",
                                "b-back"],
                       wrong_command=wrong_command
                       )
            command = input("Enter: ")

            if command == "b":
                return

            elif command == "s":
                wrong_command = False
                self.print_social_distances(node)
                input("Press Enter for back")

            elif command == "f":
                wrong_command = False
                walking = True
                while walking:
                    sentence = self.get_nodes_list_string([n for n in self.GM.current_graph.nodes if n != node])
                    self.print(sentence=sentence,
                               opt_text="Enter another node name",
                               options=[""],
                               wrong_command=wrong_command
                               )
                    command = input("Enter other node name or b for back: ")
                    if command == "b":
                        wrong_command = False
                        break
                    elif command in [n.name for n in self.GM.current_graph.nodes]:
                        finish = self.GM.current_graph.get_node_by_name(command)
                        paths_strings = self.get_all_paths_of_node_string(node=node, finish=finish)
                        self.print(sentence=paths_strings)
                        input("Press Enter for back")
                        break
                    else:
                        wrong_command = True
