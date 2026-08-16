import argparse
import heapq
import random
from itertools import count

import matplotlib.pyplot as plt

from graph import Graph, dijkstra, find_nearest_vertex
from models import Car, Rider
from quadtree import Point, Quadtree, Rectangle

DEFAULT_CANDIDATE_COUNT = 5
MEAN_ARRIVAL_TIME = 5.0


class Simulation:
    def __init__(
        self,
        map_file="city_map.csv",
        max_time=120.0,
        num_riders=50,
        num_cars=100,
        candidate_count=DEFAULT_CANDIDATE_COUNT,
        random_seed=42,
    ):
        self.current_time = 0.0
        self.events = []
        self.event_sequence = count()
        self.graph = Graph()
        self.graph.load_map_data(map_file)

        self.max_time = max_time
        self.num_riders = num_riders
        self.num_cars = num_cars
        self.candidate_count = candidate_count
        self.random_seed = random_seed
        self.random = random.Random(random_seed)

        self.rider_counter = 0
        self.riders = []
        self.completed_riders = []
        self.unsuccessful_riders = []
        self.wait_times = []
        self.trip_durations = []
        self.log = []

        xs = [coord[0] for coord in self.graph.node_coordinates.values()]
        ys = [coord[1] for coord in self.graph.node_coordinates.values()]
        margin = 1.0
        self.min_x = min(xs)
        self.max_x = max(xs)
        self.min_y = min(ys)
        self.max_y = max(ys)
        boundary = Rectangle(
            self.min_x - margin,
            self.min_y - margin,
            (self.max_x - self.min_x) + margin * 2,
            (self.max_y - self.min_y) + margin * 2,
        )

        self.available_cars = {}
        self.available_car_points = {}
        self.available_car_quadtree = Quadtree(boundary)

        self.cars = []
        node_coords = list(self.graph.node_coordinates.values())
        for i in range(num_cars):
            location = node_coords[i % len(node_coords)]
            car = Car(f"CAR-{i + 1}", location)
            self.cars.append(car)
            self.add_available_car(car)

        if self._generation_allowed(0.0):
            first_rider = self.generate_rider_request()
            self.schedule_event(0.0, "RIDER_REQUEST", first_rider)

    def schedule_event(self, timestamp, event_type, data):
        if timestamp == float("inf"):
            raise ValueError("Events may not be scheduled at infinity.")
        heapq.heappush(
            self.events,
            (timestamp, next(self.event_sequence), event_type, data),
        )

    def add_available_car(self, car):
        if car.id in self.available_cars or car.id in self.available_car_points:
            raise ValueError(f"{car.id} is already marked available.")

        point = Point(car.location[0], car.location[1], data=car)
        if not self.available_car_quadtree.insert(point):
            raise ValueError(f"{car.id} is outside the Quadtree boundary.")

        self.available_cars[car.id] = car
        self.available_car_points[car.id] = point
        car.status = "available"
        self._assert_availability_consistency()

    def remove_available_car(self, car):
        if car.id not in self.available_car_points:
            raise ValueError(f"{car.id} does not have an indexed availability point.")

        point = self.available_car_points[car.id]
        if not self.available_car_quadtree.remove(point):
            raise RuntimeError(f"Could not remove {car.id} from the Quadtree.")

        del self.available_car_points[car.id]
        del self.available_cars[car.id]
        self._assert_availability_consistency()

    def _assert_availability_consistency(self):
        dict_ids = set(self.available_cars)
        point_ids = set(self.available_car_points)
        tree_ids = {
            point.data.id
            for point in self.available_car_quadtree.all_points()
            if getattr(point.data, "id", None) is not None
        }
        if not (dict_ids == point_ids == tree_ids):
            raise AssertionError("Availability structures are out of sync.")

    def _generation_allowed(self, request_time):
        if self.num_riders is not None and self.rider_counter >= self.num_riders:
            return False
        if self.max_time is not None and request_time > self.max_time:
            return False
        return True

    def _random_coordinate(self):
        x = self.random.uniform(self.min_x, self.max_x)
        y = self.random.uniform(self.min_y, self.max_y)
        return (x, y)

    def generate_rider_request(self):
        self.rider_counter += 1
        rider = Rider(
            id=f"RIDER-{self.rider_counter}",
            start_location=self._random_coordinate(),
            destination=self._random_coordinate(),
        )
        self.riders.append(rider)
        return rider

    def _schedule_next_rider_request(self):
        if self.num_riders is not None and self.rider_counter >= self.num_riders:
            return

        interval = self.random.expovariate(1.0 / MEAN_ARRIVAL_TIME)
        next_time = self.current_time + interval

        if self.max_time is not None and next_time > self.max_time:
            return

        if not self._generation_allowed(next_time):
            return

        rider = self.generate_rider_request()
        self.schedule_event(next_time, "RIDER_REQUEST", rider)

    def handle_rider_request(self, rider):
        if rider.request_time is None:
            rider.request_time = self.current_time

        self.log.append(
            f"{self.current_time:8.2f} RIDER_REQUEST {rider.id} "
            f"from {rider.start_location} to {rider.destination}"
        )

        self._schedule_next_rider_request()

        query_point = Point(rider.start_location[0], rider.start_location[1])
        candidate_points = self.available_car_quadtree.find_k_nearest(
            query_point, k=self.candidate_count
        )

        if not candidate_points:
            rider.status = "unmatched"
            self.unsuccessful_riders.append(rider)
            self.log.append(
                f"{self.current_time:8.2f} UNMATCHED {rider.id}: no available cars"
            )
            return

        rider_vertex = find_nearest_vertex(
            rider.start_location, self.graph.node_coordinates
        )

        best = None
        for order, point in enumerate(candidate_points):
            car = point.data
            car_vertex = find_nearest_vertex(
                car.location, self.graph.node_coordinates
            )
            route, pickup_time = dijkstra(self.graph, car_vertex, rider_vertex)
            if route is None:
                continue

            candidate_key = (pickup_time, order, car.id)
            if best is None or candidate_key < best[0]:
                best = (candidate_key, car, route, pickup_time)

        if best is None:
            rider.status = "unmatched"
            self.unsuccessful_riders.append(rider)
            self.log.append(
                f"{self.current_time:8.2f} UNMATCHED {rider.id}: candidates unreachable"
            )
            return

        _, best_car, best_route, best_pickup_time = best
        self.remove_available_car(best_car)

        best_car.status = "en_route_to_pickup"
        best_car.assigned_rider = rider
        best_car.route = best_route
        best_car.route_time = best_pickup_time
        best_car.busy_start_time = self.current_time
        rider.status = "waiting"

        self.schedule_event(
            self.current_time + best_pickup_time,
            "PICKUP_ARRIVAL",
            best_car,
        )

        self.log.append(
            f"{self.current_time:8.2f} DISPATCH {best_car.id} -> {rider.id} "
            f"pickup_time={best_pickup_time:.2f}"
        )

    def handle_pickup_arrival(self, car):
        rider = car.assigned_rider
        if rider is None:
            raise RuntimeError(f"{car.id} reached pickup without an assigned rider.")

        car.location = rider.start_location
        car.status = "en_route_to_destination"
        rider.status = "in_car"
        rider.pickup_time = self.current_time
        self.wait_times.append(rider.pickup_time - rider.request_time)

        pickup_vertex = find_nearest_vertex(
            rider.start_location, self.graph.node_coordinates
        )
        destination_vertex = find_nearest_vertex(
            rider.destination, self.graph.node_coordinates
        )

        route, trip_time = dijkstra(self.graph, pickup_vertex, destination_vertex)

        if route is None:
            rider.status = "unsuccessful"
            self.unsuccessful_riders.append(rider)
            car.total_busy_time += self.current_time - car.busy_start_time
            car.busy_start_time = None
            car.assigned_rider = None
            car.route = None
            car.route_time = 0.0
            self.add_available_car(car)
            self.log.append(
                f"{self.current_time:8.2f} FAILED_TRIP {rider.id}: destination unreachable"
            )
            return

        car.route = route
        car.route_time = trip_time
        self.schedule_event(
            self.current_time + trip_time,
            "DROPOFF_ARRIVAL",
            car,
        )
        self.log.append(
            f"{self.current_time:8.2f} PICKUP {rider.id} by {car.id} "
            f"trip_time={trip_time:.2f}"
        )

    def handle_dropoff_arrival(self, car):
        rider = car.assigned_rider
        if rider is None:
            raise RuntimeError(f"{car.id} reached drop-off without an assigned rider.")

        car.location = rider.destination
        rider.status = "completed"
        rider.dropoff_time = self.current_time

        self.trip_durations.append(rider.dropoff_time - rider.pickup_time)
        self.completed_riders.append(rider)

        car.total_busy_time += self.current_time - car.busy_start_time
        car.busy_start_time = None
        car.trips_completed += 1
        car.assigned_rider = None
        car.route = None
        car.route_time = 0.0

        self.add_available_car(car)

        self.log.append(
            f"{self.current_time:8.2f} DROPOFF {rider.id} by {car.id}"
        )

    def run(self):
        while self.events:
            timestamp, sequence_number, event_type, data = heapq.heappop(self.events)
            self.current_time = timestamp

            if event_type == "RIDER_REQUEST":
                self.handle_rider_request(data)
            elif event_type == "PICKUP_ARRIVAL":
                self.handle_pickup_arrival(data)
            elif event_type == "DROPOFF_ARRIVAL":
                self.handle_dropoff_arrival(data)
            else:
                raise ValueError(f"Unknown event type: {event_type}")

        self._assert_availability_consistency()
        return self.metrics()

    def metrics(self):
        total_riders = len(self.riders)
        total_completed = len(self.completed_riders)
        total_unsuccessful = len(self.unsuccessful_riders)
        average_wait = (
            sum(self.wait_times) / len(self.wait_times)
            if self.wait_times else 0.0
        )
        average_trip = (
            sum(self.trip_durations) / len(self.trip_durations)
            if self.trip_durations else 0.0
        )
        simulation_span = max(self.current_time, 0.0)
        total_busy = sum(car.total_busy_time for car in self.cars)
        utilization = (
            total_busy / (len(self.cars) * simulation_span)
            if self.cars and simulation_span > 0 else 0.0
        )

        return {
            "total_riders_generated": total_riders,
            "total_riders_completed": total_completed,
            "total_unmatched_or_unsuccessful": total_unsuccessful,
            "average_rider_wait_time": average_wait,
            "average_completed_trip_duration": average_trip,
            "driver_utilization": utilization,
            "simulation_span": simulation_span,
            "trips_completed_per_car": {
                car.id: car.trips_completed for car in self.cars
            },
        }

    def save_log(self, filename="simulation_log.txt"):
        with open(filename, "w", encoding="utf-8") as file:
            file.write("\n".join(self.log))

    def create_visualization(self, filename="simulation_summary.png"):
        metrics = self.metrics()

        fig = plt.figure(figsize=(14, 8))
        grid = fig.add_gridspec(2, 2, width_ratios=[2, 1], height_ratios=[1, 1])

        ax_map = fig.add_subplot(grid[:, 0])
        ax_metrics = fig.add_subplot(grid[0, 1])
        ax_chart = fig.add_subplot(grid[1, 1])

        # Draw graph roads.
        seen_edges = set()
        for start, neighbors in self.graph.adjacency_list.items():
            sx, sy = self.graph.node_coordinates[start]
            for end, _ in neighbors:
                edge = tuple(sorted((start, end)))
                if edge in seen_edges:
                    continue
                seen_edges.add(edge)
                ex, ey = self.graph.node_coordinates[end]
                ax_map.plot([sx, ex], [sy, ey], linewidth=0.8, alpha=0.45)

        car_x = [car.location[0] for car in self.cars]
        car_y = [car.location[1] for car in self.cars]
        ax_map.scatter(car_x, car_y, s=25)
        ax_map.set_title("Final Car Locations")
        ax_map.set_xlabel("X Coordinate")
        ax_map.set_ylabel("Y Coordinate")
        ax_map.grid(True, alpha=0.2)

        ax_metrics.axis("off")
        metrics_text = (
            "Simulation Metrics\n\n"
            f"Riders generated: {metrics['total_riders_generated']}\n"
            f"Riders completed: {metrics['total_riders_completed']}\n"
            f"Unmatched/unsuccessful: {metrics['total_unmatched_or_unsuccessful']}\n"
            f"Average wait time: {metrics['average_rider_wait_time']:.2f}\n"
            f"Average trip duration: {metrics['average_completed_trip_duration']:.2f}\n"
            f"Driver utilization: {metrics['driver_utilization']:.1%}\n"
            f"Simulation span: {metrics['simulation_span']:.2f}"
        )
        ax_metrics.text(0.02, 0.98, metrics_text, va="top", fontsize=12)

        trip_counts = [
            car.trips_completed for car in self.cars if car.trips_completed > 0
        ]
        if not trip_counts:
            trip_counts = [0]
        ax_chart.hist(trip_counts, bins=range(0, max(trip_counts) + 2), align="left")
        ax_chart.set_title("Trips Completed per Active Car")
        ax_chart.set_xlabel("Trips Completed")
        ax_chart.set_ylabel("Number of Cars")

        fig.suptitle("Ride-Sharing Simulation Summary", fontsize=16)
        fig.tight_layout()
        fig.savefig(filename, dpi=150)
        plt.close(fig)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Event-driven ride-sharing simulator."
    )
    parser.add_argument("--map-file", default="city_map.csv")
    parser.add_argument("--max-time", type=float, default=120.0)
    parser.add_argument("--num-riders", type=int, default=50)
    parser.add_argument("--num-cars", type=int, default=100)
    parser.add_argument(
        "--candidate-count", type=int, default=DEFAULT_CANDIDATE_COUNT
    )
    parser.add_argument("--random-seed", type=int, default=42)
    return parser


def main():
    args = build_parser().parse_args()
    if args.candidate_count <= 0:
        raise ValueError("--candidate-count must be greater than 0.")

    sim = Simulation(
        map_file=args.map_file,
        max_time=args.max_time,
        num_riders=args.num_riders,
        num_cars=args.num_cars,
        candidate_count=args.candidate_count,
        random_seed=args.random_seed,
    )
    metrics = sim.run()
    sim.save_log("simulation_log.txt")
    sim.create_visualization("simulation_summary.png")

    print("Simulation complete.")
    print(f"Riders generated: {metrics['total_riders_generated']}")
    print(f"Riders completed: {metrics['total_riders_completed']}")
    print(
        "Unmatched/unsuccessful: "
        f"{metrics['total_unmatched_or_unsuccessful']}"
    )
    print(f"Average wait time: {metrics['average_rider_wait_time']:.2f}")
    print(
        "Average trip duration: "
        f"{metrics['average_completed_trip_duration']:.2f}"
    )
    print(f"Driver utilization: {metrics['driver_utilization']:.1%}")


if __name__ == "__main__":
    main()
