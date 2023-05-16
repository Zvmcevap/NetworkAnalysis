# Network Analysis Program

Made for a seminar work at UNI.

***

#### How to run:

- run ```python3 main.py``` or equivalent in terminal

#### How to use?

The program runs in a terminal and has listed available options to follow.

#### Loading in a graph

- You can load in a new graph from a text file
- Or load a previously loaded graph

Each line of the text file has to have either 1 or 2 node names seperated by a space:

```
a b
1 2
1 b
d
...
```

Each new line represents either a connection between 2 nodes or a single node.

#### Generating a graph

There are a number of options for generating simple graph for any number of nodes **n**:

- **Kn** complete graphs
- **Kn,m** bipartite complete graph
- **Cn** cycles
- **Qn** hypercubes

### Analysis

So, lets breakdown what this program can find out.

#### Graph Level

On the bigger scale the program checks for:

- **Connectivity:** If the graph is completely connected.
- **Partitions:** If it is not, how many connected parts there are.
- **Communities:** Recursively erases edges and saves a subgraph if it has more partitions than before. Ends when all
  edges have the same betweeness.
- **Euler/Hamilton path/circuit:** If they are possible it finds them and saves them for display, if not tells you
  why they are not.
- **Bipartite:** Checks if the graph is bipartite, if yes colors the nodes, if not finds an odd cycle and displays it.
- **Min / Max / Avg:** For all node and edge specific data (like, density, diameter and so on).
- **Subgraphs:** Made for communities can be loaded from the main graph to see the same information as for main graph
- ...other's I forgot to mention...

#### Node / Edge Level

On the node and edge level the program analyses and saves:

- **Degree:** Number of edges connecting the node.
- **Clustering Coefficient:** At a social distance of 1.
- **Betweeness:** How many shortest paths go through a node or edge compared to all shortest paths.
- **Closeness:** Average path length from this node to all other nodes.
- **Social Distances:** All nodes at a specific away from this node.
- **Bridges:** All paths where this node or edge where it acts as a bridge.
- ...
