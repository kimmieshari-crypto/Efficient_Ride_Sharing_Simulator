import heapq
import tempfile
import unittest

from graph import Graph, dijkstra
from models import Car
from quadtree import Point, Quadtree, Rectangle
from simulation import DEFAULT_CANDIDATE_COUNT, Simulation


class ProjectTests(unittest.TestCase):
    def test_event_tie_breaker_handles_same_timestamp(self):
        sim = Simulation(
            map_file="city_map.csv",
            max_time=0,
            num_riders=0,
            num_cars=2,
            random_seed=1,
        )
        sim.events = []
        sim.schedule_event(5, "TEST_A", {"a": 1})
        sim.schedule_event(5, "TEST_B", {"b": 2})
        first = heapq.heappop(sim.events)
        second = heapq.heappop(sim.events)
        self.assertEqual(first[0], 5)
        self.assertEqual(second[0], 5)
        self.assertNotEqual(first[1], second[1])
        self.assertEqual(len(first), 4)
        self.assertEqual(len(second), 4)

    def test_default_candidate_count_is_five(self):
        self.assertEqual(DEFAULT_CANDIDATE_COUNT, 5)

    def test_quadtree_fewer_than_k_and_empty(self):
        tree = Quadtree(Rectangle(0, 0, 10, 10))
        self.assertEqual(tree.find_k_nearest(Point(5, 5), 5), [])
        p1 = Point(1, 1, data="a")
        p2 = Point(2, 2, data="b")
        tree.insert(p1)
        tree.insert(p2)
        result = tree.find_k_nearest(Point(0, 0), 5)
        self.assertEqual(len(result), 2)
        self.assertIs(result[0], p1)

    def test_quadtree_exact_identity_removal(self):
        tree = Quadtree(Rectangle(0, 0, 10, 10), capacity=1)
        p1 = Point(3, 3, data="first")
        p2 = Point(3, 3, data="second")
        self.assertTrue(tree.insert(p1))
        self.assertTrue(tree.insert(p2))
        self.assertTrue(tree.remove(p1))
        remaining = tree.all_points()
        self.assertNotIn(p1, remaining)
        self.assertIn(p2, remaining)

    def test_dispatched_car_removed_until_dropoff(self):
        sim = Simulation(
            map_file="city_map.csv",
            max_time=0,
            num_riders=1,
            num_cars=5,
            random_seed=7,
        )
        rider_event = heapq.heappop(sim.events)
        sim.current_time = rider_event[0]
        rider = rider_event[3]
        sim.handle_rider_request(rider)

        busy_cars = [car for car in sim.cars if car.status == "en_route_to_pickup"]
        self.assertEqual(len(busy_cars), 1)
        car = busy_cars[0]
        self.assertNotIn(car.id, sim.available_cars)
        self.assertNotIn(car.id, sim.available_car_points)

        event = heapq.heappop(sim.events)
        sim.current_time = event[0]
        self.assertEqual(event[2], "PICKUP_ARRIVAL")
        sim.handle_pickup_arrival(event[3])
        self.assertNotIn(car.id, sim.available_cars)

        event = heapq.heappop(sim.events)
        sim.current_time = event[0]
        self.assertEqual(event[2], "DROPOFF_ARRIVAL")
        destination = car.assigned_rider.destination
        sim.handle_dropoff_arrival(event[3])
        self.assertIn(car.id, sim.available_cars)
        point = sim.available_car_points[car.id]
        self.assertEqual((point.x, point.y), destination)

    def test_no_infinite_events(self):
        sim = Simulation(
            map_file="city_map.csv",
            max_time=0,
            num_riders=0,
            num_cars=1,
        )
        with self.assertRaises(ValueError):
            sim.schedule_event(float("inf"), "BAD", None)

    def test_full_simulation_finishes_active_trips(self):
        sim = Simulation(
            map_file="city_map.csv",
            max_time=10,
            num_riders=10,
            num_cars=5,
            random_seed=11,
        )
        metrics = sim.run()
        self.assertFalse(sim.events)
        self.assertTrue(
            all(car.status == "available" for car in sim.cars),
            "Every car should finish active trips before the run ends.",
        )
        self.assertGreaterEqual(metrics["simulation_span"], 0)


if __name__ == "__main__":
    unittest.main()
