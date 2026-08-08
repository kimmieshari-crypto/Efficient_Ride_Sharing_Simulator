"""Car model for the ride-sharing simulation prototype."""

class Car:
    """Represents a ride-sharing car."""

    def __init__(self, car_id, location):
        self.car_id = car_id
        self.location = location  # Physical map coordinates: (x, y)
        self.status = "available"
        self.assigned_rider = None

    def __repr__(self):
        return f"Car(id={self.car_id}, location={self.location}, status={self.status})"
