# Efficient Ride-Sharing Simulator

## Assignment 6.2: Simulation Engine Prototype

This milestone implements the event-driven simulation engine for the Efficient Ride-Sharing Simulator. It proves that the simulator can process ride requests, dispatch cars, handle pickups, handle dropoffs, and maintain consistent state before the final integration of the Graph, Dijkstra, and Quadtree components.

## Simulation Engine Prototype

The simulation is a **Discrete-Event Simulation**. Instead of updating every car continuously, the simulation jumps from one meaningful event to the next.

### Event Queue

Upcoming events are stored in a Python `heapq` Min-Heap using this tuple structure:

```python
(timestamp, sequence_number, event_type, data)
```

The timestamp keeps events in chronological order. The sequence number breaks ties when multiple events have the same timestamp.

### Main Event Loop

`Simulation.run()` repeatedly pops the earliest event, advances the simulation clock, and sends the event to the correct handler.

### Placeholder Matching

`find_closest_car_brute_force()` checks every available car and returns the closest one. This is an O(N) placeholder that will later be replaced by the Quadtree.

### Placeholder Navigation

`calculate_travel_time()` uses Manhattan distance:

```python
abs(x1 - x2) + abs(y1 - y2)
```

Travel time is `distance * TRAVEL_SPEED_FACTOR`. This will later be replaced by graph-based navigation and Dijkstra's algorithm.

### State Updates

At dispatch, `car.assigned_rider` links the car to the rider and the car becomes `en_route_to_pickup`.

At pickup, `car.location` is updated to `rider.start_location`, the car becomes `en_route_to_destination`, and the rider becomes `in_car`.

At dropoff, `car.location` is updated to `rider.destination`, the car becomes `available`, the rider becomes `completed`, and `assigned_rider` is cleared.

## Files

- `car.py` — Car model using physical `(x, y)` coordinates.
- `rider.py` — Rider model.
- `simulation.py` — Event-driven simulation engine.
- `video_script.txt` — Suggested 3–5 minute code review script.
- `sample_output.txt` — Verified example output.

## How to Run

```bash
python3 simulation.py
```

The console will print a chronological event log showing dispatch, pickup, and dropoff events.
