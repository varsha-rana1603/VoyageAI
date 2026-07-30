from dataclasses import dataclass


@dataclass
class CostProfile:

    accommodation: float
    food: float
    transport: float
    activities: float
    misc: float

    @property
    def daily_total(self):
        return (
            self.accommodation
            + self.food
            + self.transport
            + self.activities
            + self.misc
        )


@dataclass
class TripCost:

    days: int

    accommodation: float
    food: float
    transport: float
    activities: float
    misc: float

    @property
    def total(self):
        return (
            self.accommodation
            + self.food
            + self.transport
            + self.activities
            + self.misc
        )