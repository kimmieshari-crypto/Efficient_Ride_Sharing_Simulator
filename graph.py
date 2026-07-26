import csv


class Graph:
    """Weighted, directed graph stored as an adjacency-list dictionary."""

    def __init__(self):
        self.adjacency_list = {}

    def add_node(self, node):
        """Add a node if it does not already exist."""
        if node not in self.adjacency_list:
            self.adjacency_list[node] = []

    def add_edge(self, start, end, weight):
        """Add a directed, weighted edge from start to end."""
        if weight < 0:
            raise ValueError("Dijkstra's algorithm requires non-negative weights.")

        self.add_node(start)
        self.add_node(end)
        self.adjacency_list[start].append((end, float(weight)))

    def get_neighbors(self, node):
        """Return a list of (neighbor, weight) tuples."""
        return self.adjacency_list.get(node, [])

    def load_from_file(self, filename):
        """
        Load edges from a CSV file.

        Expected row format:
        start_node,end_node,travel_time
        """
        with open(filename, "r", newline="", encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file)

            for line_number, row in enumerate(reader, start=1):
                if not row or all(not value.strip() for value in row):
                    continue

                if len(row) != 3:
                    raise ValueError(
                        f"Invalid row {line_number}: expected 3 values, received {len(row)}."
                    )

                start, end, weight = (value.strip() for value in row)

                try:
                    numeric_weight = float(weight)
                except ValueError as exc:
                    raise ValueError(
                        f"Invalid weight on row {line_number}: {weight!r}"
                    ) from exc

                self.add_edge(start, end, numeric_weight)

    def __str__(self):
        return "\n".join(
            f"{node}: {neighbors}"
            for node, neighbors in self.adjacency_list.items()
        )
