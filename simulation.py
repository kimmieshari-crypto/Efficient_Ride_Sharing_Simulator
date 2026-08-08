"""Discrete-event simulation engine prototype for ride sharing."""

import heapq
import math

from car import Car
from rider import Rider

TRAVEL_SPEED_FACTOR = 0.1


def calculate_travel_time(start_location, end_location):
    """Calculate placeholder travel time using Manhattan distance."""
    x1, y1 = start_location
    x2, y2 = end_location
    distance = abs(x1 - x2) + abs(y1 - y2)
    return distance * TRAVEL_SPEED_FACTOR


class Simulation:
    """Runs an event-driven ride-sharing simulation."""

    def __init__(self):
        self.current_time = 0.0
        self.event_queue = []
        self.sequence_number = 0
        self.cars = {}
        self.riders = {}

    def add_car(self, car):
        self.cars[car.car_id] = car

    def add_rider(self, rider):
        self.riders[rider.rider_id] = rider

    def schedule_event(self, timestamp, event_type, data):
        """Push (timestamp, sequence_number, event_type, data) onto the Min-Heap."""
        self.sequence_number += 1
        heapq.heappush(
            self.event_queue,
            (timestamp, self.sequence_number, event_type, data),
        )

    def find_closest_car_brute_force(self, rider_location):
        """Return the closest available car using an O(N) brute-force search."""
        best_car = None
        best_distance = float("inf")
        rider_x, rider_y = rider_location

        for car in self.cars.values():
            if car.status != "available":
                continue
            car_x, car_y = car.location
            distance = math.sqrt(
                (car_x - rider_x) ** 2 + (car_y - rider_y) ** 2
            )
            if distance < best_distance:
                best_distance = distance
                best_car = car
        return best_car

    def handle_rider_request(self, rider):
        car = self.find_closest_car_brute_force(rider.start_location)

        if car is None:
            print(
                f"TIME {self.current_time:.2f}: "
                f"No available car for RIDER {rider.rider_id}"
            )
            return

        car.assigned_rider = rider
        car.status = "en_route_to_pickup"
        rider.status = "waiting_for_pickup"

        pickup_duration = calculate_travel_time(
            car.location, rider.start_location
        )
        self.schedule_event(
            self.current_time + pickup_duration,
            "ARRIVAL",
            car,
        )

        print(
            f"TIME {self.current_time:.2f}: "
            f"CAR {car.car_id} dispatched to RIDER {rider.rider_id}"
        )

    def handle_arrival(self, car):
        rider = car.assigned_rider
        if rider is None:
            return

        if car.status == "en_route_to_pickup":
            print(
                f"TIME {self.current_time:.2f}: "
                f"CAR {car.car_id} picked up RIDER {rider.rider_id}"
            )

            car.location = rider.start_location
            car.status = "en_route_to_destination"
            rider.status = "in_car"

            dropoff_duration = calculate_travel_time(
                car.location, rider.destination
            )
            self.schedule_event(
                self.current_time + dropoff_duration,
                "ARRIVAL",
                car,
            )

        elif car.status == "en_route_to_destination":
            print(
                f"TIME {self.current_time:.2f}: "
                f"CAR {car.car_id} dropped off RIDER {rider.rider_id}"
            )

            car.location = rider.destination
            car.status = "available"
            rider.status = "completed"
            car.assigned_rider = None

    def run(self):
        """Process events in chronological order until the heap is empty."""
        print("--- Simulation Started ---")
        while self.event_queue:
            timestamp, sequence_number, event_type, data = heapq.heappop(
                self.event_queue
            )
            self.current_time = timestamp

            if event_type == "RIDER_REQUEST":
                self.handle_rider_request(data)
            elif event_type == "ARRIVAL":
                self.handle_arrival(data)
            else:
                print(
                    f"TIME {self.current_time:.2f}: "
                    f"Unknown event type: {event_type}"
                )
        print("--- Simulation Complete ---")


def build_demo_simulation():
    simulation = Simulation()

    simulation.add_car(Car("CAR-01", (0.0, 0.0)))
    simulation.add_car(Car("CAR-02", (80.0, 20.0)))
    simulation.add_car(Car("CAR-03", (40.0, 90.0)))

    rider_1 = Rider("RIDER-01", (10.0, 10.0), (50.0, 40.0))
    rider_2 = Rider("RIDER-02", (75.0, 25.0), (20.0, 80.0))
    rider_3 = Rider("RIDER-03", (45.0, 85.0), (90.0, 90.0))

    for rider in (rider_1, rider_2, rider_3):
        simulation.add_rider(rider)

    simulation.schedule_event(0.0, "RIDER_REQUEST", rider_1)
    simulation.schedule_event(2.0, "RIDER_REQUEST", rider_2)
    simulation.schedule_event(4.0, "RIDER_REQUEST", rider_3)

    return simulation


if __name__ == "__main__":
    demo = build_demo_simulation()
    demo.run()
