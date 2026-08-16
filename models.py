from dataclasses import dataclass
from typing import Optional, Tuple, List

Coordinate = Tuple[float, float]

@dataclass
class Rider:
    id: str
    start_location: Coordinate
    destination: Coordinate
    status: str = "waiting"
    request_time: Optional[float] = None
    pickup_time: Optional[float] = None
    dropoff_time: Optional[float] = None

class Car:
    def __init__(self, car_id: str, location: Coordinate):
        self.id = car_id
        self.location = location
        self.status = "available"
        self.assigned_rider: Optional[Rider] = None
        self.route: Optional[List[str]] = None
        self.route_time = 0.0
        self.busy_start_time: Optional[float] = None
        self.total_busy_time = 0.0
        self.trips_completed = 0

    def calculate_route(self, destination, graph):
        from graph import find_nearest_vertex, dijkstra
        start_vertex = find_nearest_vertex(self.location, graph.node_coordinates)
        end_vertex = find_nearest_vertex(destination, graph.node_coordinates)
        route, travel_time = dijkstra(graph, start_vertex, end_vertex)
        self.route = route
        self.route_time = travel_time
        return route, travel_time
