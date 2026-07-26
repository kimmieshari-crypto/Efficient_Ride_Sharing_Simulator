import heapq


class Car:
    """Represents a car participating in the ride-sharing simulation."""

    def __init__(self, car_id, location, status="available"):
        self.car_id = car_id
        self.location = location
        self.status = status
        self.route = []
        self.route_time = float("inf")

    def calculate_route(self, destination, graph):
        """
        Calculate and store the shortest route from the car's current
        location to destination using Dijkstra's algorithm.
        """
        start_node = self.location
        end_node = destination

        if start_node == end_node:
            self.route = [start_node]
            self.route_time = 0.0
            return self.route, self.route_time

        distances = {start_node: 0.0}
        predecessors = {}
        priority_queue = [(0.0, start_node)]

        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)

            # A node can appear in the heap more than once. Skip old entries.
            if current_distance > distances.get(current_node, float("inf")):
                continue

            if current_node == end_node:
                break

            for neighbor, edge_weight in graph.get_neighbors(current_node):
                if edge_weight < 0:
                    raise ValueError(
                        "Dijkstra's algorithm cannot process negative edge weights."
                    )

                new_distance = current_distance + edge_weight

                if new_distance < distances.get(neighbor, float("inf")):
                    distances[neighbor] = new_distance
                    predecessors[neighbor] = current_node
                    heapq.heappush(
                        priority_queue,
                        (new_distance, neighbor)
                    )

        if end_node not in distances:
            self.route = None
            self.route_time = float("inf")
            return self.route, self.route_time

        path = []
        current_node = end_node

        while current_node is not None:
            path.append(current_node)

            if current_node == start_node:
                break

            current_node = predecessors.get(current_node)

        if not path or path[-1] != start_node:
            self.route = None
            self.route_time = float("inf")
            return self.route, self.route_time

        path.reverse()
        self.route = path
        self.route_time = distances[end_node]

        return self.route, self.route_time

    def __str__(self):
        return (
            f"Car ID: {self.car_id}, "
            f"Location: {self.location}, "
            f"Status: {self.status}, "
            f"Route: {self.route}, "
            f"Route Time: {self.route_time}"
        )
