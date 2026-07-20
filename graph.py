"""Graph data structure for the ride-sharing simulator."""

import csv


class Graph:
    """Represents a directed, weighted city map using an adjacency list."""

    def __init__(self):
        """Initialize an empty adjacency list."""
        self.adjacency_list = {}

    def add_edge(self, start_node, end_node, weight):
        """
        Add a directed, weighted edge to the graph.

        Args:
            start_node (str): The starting location.
            end_node (str): The destination location.
            weight (int): Travel time between the two locations.
        """
        if start_node not in self.adjacency_list:
            self.adjacency_list[start_node] = []

        self.adjacency_list[start_node].append((end_node, weight))

        # Ensure destination-only nodes also appear in the graph.
        if end_node not in self.adjacency_list:
            self.adjacency_list[end_node] = []

    def load_from_file(self, filename):
        """
        Load directed roads from a CSV file.

        Each nonblank row must contain:
        start_node,end_node,travel_time

        Args:
            filename (str): Path to the CSV map file.
        """
        self.adjacency_list.clear()

        try:
            with open(filename, "r", newline="", encoding="utf-8") as map_file:
                reader = csv.reader(map_file)

                for line_number, row in enumerate(reader, start=1):
                    if not row or all(not value.strip() for value in row):
                        continue

                    if len(row) != 3:
                        raise ValueError(
                            f"Invalid map data on line {line_number}: "
                            "expected 3 values."
                        )

                    start_node = row[0].strip()
                    end_node = row[1].strip()

                    if not start_node or not end_node:
                        raise ValueError(
                            f"Invalid map data on line {line_number}: "
                            "node names cannot be blank."
                        )

                    try:
                        weight = int(row[2].strip())
                    except ValueError as exc:
                        raise ValueError(
                            f"Invalid travel time on line {line_number}: "
                            f"{row[2]!r} is not an integer."
                        ) from exc

                    if weight < 0:
                        raise ValueError(
                            f"Invalid travel time on line {line_number}: "
                            "weight cannot be negative."
                        )

                    self.add_edge(start_node, end_node, weight)

        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"Map file was not found: {filename}"
            ) from exc

    def __str__(self):
        """Return a readable representation of the adjacency list."""
        lines = ["City Map Adjacency List:"]

        for node in sorted(self.adjacency_list):
            neighbors = self.adjacency_list[node]

            if neighbors:
                formatted_neighbors = ", ".join(
                    f"{neighbor} ({weight} min)"
                    for neighbor, weight in neighbors
                )
            else:
                formatted_neighbors = "No outgoing roads"

            lines.append(f"{node} -> {formatted_neighbors}")

        return "\n".join(lines)
