"""Rider model for the ride-sharing simulator."""


class Rider:
    """Represents a rider requesting transportation."""

    def __init__(self, rider_id, pickup_location, destination):
        self.rider_id = rider_id
        self.pickup_location = pickup_location
        self.destination = destination

    def __str__(self):
        return (
            f"Rider {self.rider_id}: pickup={self.pickup_location}, "
            f"destination={self.destination}"
        )
