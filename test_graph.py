"""Test script for Assignment 3.2."""

from simulation import Simulation


def main():
    """Load the map and display the completed adjacency list."""
    simulation = Simulation("map.csv")

    print("Simulation initialized successfully.")
    print()
    print(simulation.map)


if __name__ == "__main__":
    main()
