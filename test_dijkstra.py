from graph import Graph
from pathfinding import find_shortest_path


def main():
    city_map = Graph()
    city_map.load_from_file("map.csv")

    path, distance = find_shortest_path(city_map, "A", "D")

    print("Standalone Dijkstra Test")
    print("------------------------")
    print(f"Shortest path from A to D: {path}")
    print(f"Total travel time: {distance}")

    assert path == ["A", "C", "B", "D"]
    assert distance == 4.0

    print("Test passed successfully.")


if __name__ == "__main__":
    main()
