# Efficient, Analyzed Ride-Sharing Simulator

This project is a Python-based ride-sharing simulation developed for the
Introduction to Python and Algorithms course. It uses object-oriented design
and custom data structures to model cars, riders, and a city road network.

## Current Features

- `Car` class for storing car identification, location, and availability
- `Rider` class for storing pickup and destination information
- `Graph` class implemented with an adjacency list
- File-driven city map loaded from a CSV file
- `Simulation` class that initializes and stores the city graph
- Test script that verifies the map loads correctly

## Project Files

```text
assignment_3_2_graph_project/
├── car.py
├── graph.py
├── map.csv
├── README.md
├── rider.py
├── simulation.py
└── test_graph.py
```

## Map Data Format

The city map is stored in `map.csv`. Each row represents one directed road and
contains three comma-separated values:

```text
start_node,end_node,travel_time
```

- `start_node` is the location where the road begins.
- `end_node` is the location where the road ends.
- `travel_time` is the integer number of minutes required to travel along the
  road.

Example:

```text
A,B,5
B,A,5
A,C,3
```

The graph is directed. A two-way street must therefore be represented by two
separate rows. For example, `A,B,5` creates a road from A to B, while `B,A,5`
creates the return road from B to A.

## Graph Implementation

The `Graph` class stores the map in an adjacency-list dictionary. Each key is a
node, and its value is a list of `(neighbor, weight)` tuples.

Example:

```python
{
    "A": [("B", 5), ("C", 3)],
    "B": [("A", 5), ("D", 4)]
}
```

This structure is efficient for a sparse city map because it stores only roads
that actually exist.

## How to Run

1. Open the project folder in Codio, VS Code, or another Python editor.
2. Make sure all files are in the same folder.
3. Open a terminal in that folder.
4. Run:

```bash
python test_graph.py
```

On some computers, use:

```bash
python3 test_graph.py
```

The program initializes the `Simulation` object, loads `map.csv`, and prints
the graph's adjacency list.

## Expected Output

```text
Simulation initialized successfully.

City Map Adjacency List:
A -> B (5 min), C (3 min)
B -> A (5 min), D (4 min), E (6 min)
C -> A (3 min), D (1 min)
D -> B (4 min), C (1 min), E (2 min)
E -> B (6 min), D (2 min)
```

## Complexity Analysis

- Adding one edge takes approximately **O(1)** average time.
- Loading a file containing E roads takes **O(E)** time.
- The adjacency-list storage requirement is **O(V + E)**, where V is the
  number of nodes and E is the number of directed roads.
- Printing the complete graph takes **O(V + E)** time.
