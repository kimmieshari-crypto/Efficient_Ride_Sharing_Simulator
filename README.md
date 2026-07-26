# Efficient Ride-Sharing Simulator

## Project Overview

This project models the core parts of a ride-sharing system using Python and
object-oriented programming. Cars and map locations are represented as Python
objects, while roads are stored in a weighted graph.

## Pathfinding with Dijkstra's Algorithm

The project uses Dijkstra's shortest-path algorithm to calculate the fastest
route between two locations in the map.

The algorithm uses Python's `heapq` module as a min-heap priority queue. Each
heap entry is a tuple containing:

```python
(distance_from_start, node)
```

The node with the smallest known distance is processed first. A `distances`
dictionary stores the best travel time found for each node, and a
`predecessors` dictionary records which node came before each node in the
optimal route. After reaching the destination, the predecessor information is
used to reconstruct the complete path.

Dijkstra's algorithm requires all edge weights to be non-negative.

## Car Route Calculation

The `Car` class includes this method:

```python
calculate_route(self, destination, graph)
```

The method starts at the car's current `self.location` and calculates the
shortest route to the requested destination. It stores the result in:

- `self.route`: the ordered list of map nodes in the route
- `self.route_time`: the total travel time for the route

When no route exists, `self.route` is set to `None` and `self.route_time` is
set to `float("inf")`.

## Project Files

- `graph.py` - weighted graph implementation and CSV map loader
- `car.py` - Car class with integrated route calculation
- `pathfinding.py` - standalone Dijkstra function
- `map.csv` - sample weighted map
- `test_dijkstra.py` - isolated test of the standalone function
- `test_car_route.py` - demonstration of route calculation through a Car object

## How to Run

Open a terminal in the project directory.

Run the standalone pathfinding test:

```bash
python test_dijkstra.py
```

Run the integrated Car route test:

```bash
python test_car_route.py
```

Expected integrated output includes:

```text
Calculated route: ['A', 'C', 'B', 'D']
Calculated route time: 4.0
Car route test passed successfully.
```

## Complexity Analysis

Using an adjacency list and a binary min-heap, Dijkstra's algorithm has a time
complexity of:

```text
O((V + E) log V)
```

This is often written as `O(E log V)` for a connected graph.

Its additional space complexity is:

```text
O(V + E)
```

The graph requires space for vertices and edges, while the distance,
predecessor, and priority queue structures require additional space based on
the number of vertices and queued entries.
