"""Car model for the ride-sharing simulator."""


class Car:
    """Represents a car participating in the simulation."""

    def __init__(self, car_id, location, status="available"):
        self.car_id = car_id
        self.location = location
        self.status = status

    def __str__(self):
        return (
            f"Car {self.car_id}: location={self.location}, "
            f"status={self.status}"
        )
