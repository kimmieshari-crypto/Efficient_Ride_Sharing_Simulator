import collections
import heapq

class Graph:
    """City map containing road edges and graph-node coordinates."""

    def __init__(self):
        self.adjacency_list = collections.defaultdict(list)
        self.node_coordinates = {}

    def load_map_data(self, filename):
        with open(filename, "r", encoding="utf-8") as file:
            for raw_line in file:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = line.split(",")
                if len(parts) != 7:
                    raise ValueError(
                        f"Expected 7 comma-separated values, got {len(parts)}: {line}"
                    )

                (
                    start_id,
                    start_x,
                    start_y,
                    end_id,
                    end_x,
                    end_y,
                    weight,
                ) = parts

                self.node_coordinates[start_id] = (float(start_x), float(start_y))
                self.node_coordinates[end_id] = (float(end_x), float(end_y))

                w = float(weight)
                self.adjacency_list[start_id].append((end_id, w))
                self.adjacency_list[end_id].append((start_id, w))


def find_nearest_vertex(point, node_coordinates):
    if not node_coordinates:
        raise ValueError("No graph vertices were loaded.")

    point_x, point_y = point
    return min(
        node_coordinates,
        key=lambda node_id: (
            node_coordinates[node_id][0] - point_x
        ) ** 2 + (
            node_coordinates[node_id][1] - point_y
        ) ** 2,
    )


def dijkstra(graph, start, goal):
    if start not in graph.node_coordinates or goal not in graph.node_coordinates:
        return None, float("inf")

    distances = {start: 0.0}
    previous = {}
    heap = [(0.0, start)]

    while heap:
        current_distance, node = heapq.heappop(heap)
        if current_distance != distances.get(node):
            continue

        if node == goal:
            route = []
            cursor = goal
            while True:
                route.append(cursor)
                if cursor == start:
                    break
                cursor = previous[cursor]
            route.reverse()
            return route, current_distance

        for neighbor, weight in graph.adjacency_list.get(node, []):
            new_distance = current_distance + weight
            if new_distance < distances.get(neighbor, float("inf")):
                distances[neighbor] = new_distance
                previous[neighbor] = node
                heapq.heappush(heap, (new_distance, neighbor))

    return None, float("inf")
