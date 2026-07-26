import heapq


def find_shortest_path(graph, start_node, end_node):
    """
    Find the shortest path between two nodes using Dijkstra's algorithm.

    Args:
        graph: A Graph object that provides get_neighbors(node).
        start_node: Beginning node.
        end_node: Destination node.

    Returns:
        tuple: (path, total_distance)
            path is a list of nodes, or None when no route exists.
            total_distance is float('inf') when no route exists.
    """
    if start_node == end_node:
        return [start_node], 0.0

    # The best known distance from the start node to each discovered node.
    distances = {start_node: 0.0}

    # Used later to reconstruct the final route.
    predecessors = {}

    # Heap entries are (distance_from_start, node).
    priority_queue = [(0.0, start_node)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        # Ignore outdated heap entries.
        if current_distance > distances.get(current_node, float("inf")):
            continue

        # Once the destination is removed with its best distance, we are done.
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
                heapq.heappush(priority_queue, (new_distance, neighbor))

    if end_node not in distances:
        return None, float("inf")

    # Reconstruct the route by walking backward from destination to start.
    path = []
    current_node = end_node

    while current_node is not None:
        path.append(current_node)

        if current_node == start_node:
            break

        current_node = predecessors.get(current_node)

    if not path or path[-1] != start_node:
        return None, float("inf")

    path.reverse()
    return path, distances[end_node]
