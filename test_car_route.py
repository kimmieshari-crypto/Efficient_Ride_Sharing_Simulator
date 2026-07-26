from car import Car
from graph import Graph


def main():
    city_map = Graph()
    city_map.load_from_file("map.csv")

    car = Car("CAR-01", "A")

    print("Before route calculation:")
    print(car)

    car.calculate_route("D", city_map)

    print("\nAfter route calculation:")
    print(f"Car location: {car.location}")
    print(f"Destination: D")
    print(f"Calculated route: {car.route}")
    print(f"Calculated route time: {car.route_time}")

    assert car.route == ["A", "C", "B", "D"]
    assert car.route_time == 4.0

    print("\nCar route test passed successfully.")


if __name__ == "__main__":
    main()
