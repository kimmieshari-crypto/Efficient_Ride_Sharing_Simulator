# Efficient, Analyzed Ride-Sharing Simulator

## Overview

This project is a discrete-time, event-driven ride-sharing simulator. It integrates:

- A weighted `Graph` representing roads and node coordinates.
- Dijkstra's shortest-path algorithm for true road-network travel times.
- A Quadtree for quickly locating the geographically nearest available cars.
- `Car` and `Rider` object models with explicit state transitions.
- A deterministic four-field event queue.
- Simulation metrics and an integrated Matplotlib visualization.

## Requirements

- Python 3.10+
- matplotlib

Install the dependency with:

```bash
pip install matplotlib
```

## Files

- `simulation.py` - Main event-driven simulation.
- `models.py` - `Car` and `Rider` models.
- `graph.py` - Graph loading, vertex snapping, and Dijkstra.
- `quadtree.py` - Spatial indexing, k-nearest search, and identity-based removal.
- `city_map.csv` - Unified city map containing coordinates and weighted roads.
- `test_simulation.py` - Repeatable correctness checks.
- `simulation_summary.png` - Required analytical visualization.
- `simulation_log.txt` - Chronological simulation log.

## Running the Simulation

From the project directory:

```bash
python simulation.py
```

Example with options:

```bash
python simulation.py --max-time 180 --num-riders 75 --num-cars 100 --candidate-count 5 --random-seed 42 --map-file city_map.csv
```

### Command-Line Options

- `--max-time` - Stop generating new rider requests after this simulation time.
- `--num-riders` - Maximum number of riders to generate.
- `--num-cars` - Number of cars to initialize.
- `--candidate-count` - Number of nearest Quadtree candidates to evaluate. Default is `5`.
- `--random-seed` - Seed for repeatable simulations.
- `--map-file` - Path to the unified city-map CSV file.

If both `--max-time` and `--num-riders` are supplied, rider generation stops when either limit is reached. Already scheduled pickup and drop-off events are still processed so active trips finish.

## Unified Map Format

Each non-comment row in `city_map.csv` contains seven values:

```text
start_node_id,start_x,start_y,end_node_id,end_x,end_y,weight
```

Example:

```text
N00,0,0,N10,10,0,2.0
```

The Graph stores both the weighted road network and each node's `(x, y)` coordinates.

## Event Queue

Every event uses the same four-field tuple:

```python
(timestamp, sequence_number, event_type, data)
```

`itertools.count()` creates the sequence number. It guarantees deterministic ordering and prevents `heapq` from trying to compare `Car` or `Rider` objects when multiple events have the same timestamp.

The required event types are:

- `RIDER_REQUEST`
- `PICKUP_ARRIVAL`
- `DROPOFF_ARRIVAL`

## State Transitions

### Car

```text
available
  -> en_route_to_pickup
  -> en_route_to_destination
  -> available
```

### Rider

```text
waiting
  -> in_car
  -> completed
```

A rider may also become `unmatched` or `unsuccessful` when no suitable car or route exists.

## Quadtree-to-Dijkstra Matching

The matching workflow is:

```text
Quadtree -> up to k geographically nearest available cars
Dijkstra -> minimum reachable road-network travel time
```

The Quadtree's default `k` is 5. Every returned candidate is evaluated with Dijkstra before the winner is selected. A geographically close car is not automatically assumed to be the fastest car by road.

## Availability Synchronization

The simulation maintains three synchronized structures:

- `available_cars`
- `available_car_points`
- `available_car_quadtree`

`available_cars` maps car IDs to `Car` objects.

`available_car_points` maps car IDs to the exact immutable `Point` objects inserted into the Quadtree.

`available_car_quadtree` indexes only currently available cars.

All changes go through `add_available_car()` and `remove_available_car()`.

A car is removed immediately when dispatched and remains absent while driving to the rider and while carrying the rider. At drop-off, a new immutable `Point` is created at the car's destination and inserted into the Quadtree.

## Unavailable Cars and Unreachable Routes

If no cars are available, the rider is marked `unmatched`.

If every Quadtree candidate is unreachable by Dijkstra, the rider is marked `unmatched`.

If a destination becomes unreachable after pickup, the rider is marked `unsuccessful`. The car's elapsed busy time is recorded, the assignment is cleared, and the car is returned to availability at the pickup location.

No event is ever scheduled with `float("inf")` as its timestamp.

## Reported Metrics

The project reports:

- Total riders generated.
- Total riders completed.
- Total unmatched or unsuccessful riders.
- Average rider wait time.
- Average completed-trip duration.
- Driver utilization.
- Trips completed per car.

Driver utilization is defined as:

```text
total busy time for all cars
--------------------------------
number of cars × simulation span
```

The simulation span is the time of the final processed event, allowing trips to finish after rider generation stops.

## Analytical Visualization

The required `simulation_summary.png` combines:

- A large road-map view with the final locations of all cars.
- A metrics panel.
- A chart showing the distribution of trips completed by active cars.

Generate the image by running:

```bash
python simulation.py
```

## Testing

Run:

```bash
python -m unittest test_simulation.py -v
```

The tests demonstrate:

- Safe same-timestamp event handling.
- The required four-field event format.
- Default `k=5`.
- Empty and fewer-than-five Quadtree results.
- Identity-based removal for cars at identical coordinates.
- A dispatched car stays unavailable through pickup and passenger travel.
- A completed car is reinserted at its destination.
- Infinite event timestamps are rejected.
- Active trips finish after rider generation stops.

## Suggested Final Code Review Video

For the 3-5 minute demonstration:

1. Show the four-field event tuple and sequence-number tie breaker.
2. Show the command-line arguments.
3. Show the unified map loader and coordinate-to-vertex snapping.
4. Show `find_k_nearest()` and Quadtree `remove()`.
5. Show the Quadtree-to-Dijkstra candidate-selection process.
6. Show `remove_available_car()` and `add_available_car()`.
7. Run the simulation and point out multiple rider events.
8. Show the correctness test for events sharing the same timestamp.
9. Open `simulation_summary.png`.
10. Briefly explain the final metrics and driver utilization formula.


## Production Map Scale

The production `city_map.csv` uses a 20x20 road grid with 400 graph nodes. The default fleet remains 100 cars, so vehicles no longer begin on every node. This creates more useful spatial variation for Quadtree candidate selection and Dijkstra comparison while preserving the production default of 100 cars.

## Additional Correctness Tests

The test suite explicitly verifies:

- A single unreachable candidate is skipped while reachable candidates are still considered.
- An entirely unreachable candidate set is handled consistently.
- Zero available cars are handled safely at the simulation level.
- Dijkstra is run for every candidate returned by the Quadtree before the final car is selected.
