"""
app/trip_planner/itinerary/models.py

Data contracts for the search-based itinerary planner.

Self-contained — does NOT import from trip_planner/planner/ (the old
greedy-scheduler package this replaces). That package's files are being
retired; nothing here should depend on them still existing in the repo.

PlannerState is the one type every other file in this package touches,
so its immutability contract matters more than usual: apply_move()
(in planner_state.py) always returns a NEW PlannerState rather than
mutating this one. Beam search branches one parent state into several
sibling children at every step — if state were mutated in place, one
branch's update would corrupt its siblings, since Python dicts/sets are
shared by reference on a shallow copy. Frozen dataclasses + always
returning a new instance is the discipline that prevents this; it's not
just style.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time
from enum import Enum
from typing import Optional
from uuid import UUID


class MoveType(str, Enum):
    VISIT_ATTRACTION = "visit_attraction"
    TAKE_LUNCH = "take_lunch"
    TAKE_DINNER = "take_dinner"
    END_DAY = "end_day"
    END_TRIP = "end_trip"


@dataclass(frozen=True)
class Location:
    """A point the planner can be 'at'. Either a real attraction
    (attraction_id set) or a non-attraction waypoint — the hotel/start
    point each day begins from. Until accommodation ranking exists, the
    caller passes a destination-centroid placeholder here instead.
    """
    latitude: float
    longitude: float
    attraction_id: Optional[int] = None
    label: str = ""


@dataclass(frozen=True)
class Move:
    move_type: MoveType
    attraction_id: Optional[int] = None  # set only when move_type is VISIT_ATTRACTION


@dataclass(frozen=True)
class FeatureVector:
    """Named signals for one candidate move, computed by features.py,
    consumed by evaluator.py.

    A dict rather than fixed named fields, deliberately — new signals
    get added in features.py without ever touching evaluator.py's
    signature, and this is also the natural shape a future
    `model.predict(list(features.values()))` expects. Same pattern as
    RankingFactor/WEIGHTS in the attraction ranker; keeping it
    consistent across the codebase rather than inventing a second style.
    """
    values: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class Stop:
    move_type: MoveType
    attraction_id: Optional[int]
    name: str
    arrival_time: time
    departure_time: time
    travel_minutes_from_previous: float = 0.0
    travel_mode: Optional[str] = None
    reason: str = ""


@dataclass(frozen=True)
class DayPlan:
    day_number: int
    stops: tuple[Stop, ...]
    walking_minutes: float
    travel_minutes: float


@dataclass(frozen=True)
class Itinerary:
    destination_id: UUID
    days: tuple[DayPlan, ...]
    total_score: float
    dropped_must_see: tuple[int, ...] = ()


@dataclass(frozen=True)
class PlannerState:
    current_day: int
    current_time: time
    current_location: Location

    visited_attraction_ids: frozenset[int] = field(default_factory=frozenset)
    day_stops: tuple[Stop, ...] = ()  # committed stops for current_day only
    committed_days: tuple[DayPlan, ...] = ()  # finalized, day < current_day

    walking_minutes_today: float = 0.0
    travel_minutes_today: float = 0.0
    attraction_minutes_today: float = 0.0  # time spent INSIDE attractions today — distinct from walking/travel between them
    # NOTE: dict is technically mutable even inside a frozen dataclass —
    # frozen only blocks attribute *reassignment*, not mutating the dict
    # itself. Discipline required: apply_move() must always build a new
    # dict (`{**old, category: old.get(category, 0) + 1}`), never call
    # .update()/__setitem__ on an existing instance's dict.
    category_counts_today: dict[str, int] = field(default_factory=dict)
    category_counts_total: dict[str, int] = field(default_factory=dict)
    meals_taken_today: frozenset[str] = field(default_factory=frozenset)

    budget_spent: float = 0.0
    energy: float = 1.0  # 0-1, depletes across a day, partially restored on EndDay

    cumulative_score: float = 0.0  # running sum of evaluate_move() across the whole path so far

    def is_terminal(self, num_days: int) -> bool:
        return self.current_day > num_days


@dataclass(frozen=True)
class SearchConfig:
    beam_width: int = 6
    k_nearest: int = 10
    top_m_global_candidates: int = 5


@dataclass(frozen=True)
class CandidateEvaluation:
    """One evaluated candidate move, considered during the expansion of
    ONE parent state. This is the atomic unit of the search trace —
    'full trace' means every candidate gets one of these, whether or not
    it survived pruning into the next beam, so the frontend can render
    both the accepted move and the rejected alternatives it was weighed
    against.
    """
    parent_state_id: int  # id() of the parent PlannerState at trace time — stable within one search run, lets the frontend draw edges from the right parent node
    from_attraction_id: Optional[int]  # None when the parent's current_location is a non-attraction waypoint (hotel/start)
    move: Move
    to_attraction_id: Optional[int]  # None for TakeLunch/TakeDinner/EndDay/EndTrip moves
    score: float  # evaluate_move() output for this candidate
    resulting_cumulative_score: float  # parent's cumulative_score + score, i.e. what this candidate's full path would total
    survived: bool  # True if the resulting state made it into the new beam after pruning


@dataclass(frozen=True)
class SearchStep:
    """Fires once per PARENT STATE EXPANSION — i.e. once for each state
    in the current beam as its candidates get generated and scored, not
    once per whole beam iteration. Finer-grained, chosen deliberately
    for smoother frontend animation over fewer/chunkier events.

    Purely observational: planner.py's search loop produces these and
    hands them to an optional callback, but never reads them back or
    branches on their contents. Behavior and output are identical
    whether or not anything is listening.
    """
    step_number: int  # monotonically increasing across the whole search run, not reset per day/beam-iteration
    day: int
    parent_state_id: int
    parent_location_label: str  # human-readable, e.g. attraction name or "Hotel" — for display without reconstructing full state
    parent_cumulative_score: float
    candidates: tuple[CandidateEvaluation, ...]  # every candidate considered for this parent, survived or not