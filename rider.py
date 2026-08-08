"""Rider model for the ride-sharing simulation prototype."""

class Rider:
    """Represents a rider requesting transportation."""

    def __init__(self, rider_id, start_location, destination):
        self.rider_id = rider_id
        self.start_location = start_location
        self.destination = destination
        self.status = "waiting"

    def __repr__(self):
        return (
            f"Rider(id={self.rider_id}, start={self.start_location}, "
            f"destination={self.destination}, status={self.status})"
        )
