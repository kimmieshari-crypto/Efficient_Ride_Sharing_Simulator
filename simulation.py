"""Main simulation class for the ride-sharing project."""

from graph import Graph


class Simulation:
    """Coordinates the objects and map used by the simulation."""

    def __init__(self, map_filename):
        """
        Initialize the simulation and load its city map.

        Args:
            map_filename (str): Path to the CSV map data file.
        """
        self.map = Graph()
        self.map.load_from_file(map_filename)
        self.cars = {}
        self.riders = {}

    def __str__(self):
        return (
            "Ride-Sharing Simulation\n"
            f"Cars: {len(self.cars)}\n"
            f"Riders: {len(self.riders)}\n"
            f"{self.map}"
        )
