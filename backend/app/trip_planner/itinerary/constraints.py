"""
app/trip_planner/itinerary/constraints.py

Single responsibility: hard legality only — "is this candidate move
ALLOWED", never "is this candidate move GOOD" (that's features.py +
evaluator.py's job). Same split as attractions/filters.py vs
attractions/scorer.py, for the same reason: mixing "allowed" and "good"
makes it harder to reason about why a move never appeared vs. why it
scored low.

ConstraintProfile lives here rather than in models.py because every
check in this file reads from it — keeping the schema next to its only
consumers, not split across files for no reason.

NOT enforced here (deliberately):
  - Budget: a SOFT evaluator penalty per your call, not a hard block.
  - must_see_attraction_ids: enforcing "this must appear somewhere in
    the trip" isn't a per-move legality question — it's a generation
    concern (actions.py should force-include/boost must-sees as
    candidates) and an end-of-trip scoring concern (evaluator.py should
    penalize ending the trip with must-sees still unvisited). A hard
    per-move check can't express "must happen eventually," so it's not
    attempted here.
  - Attraction closing times: explicitly future work per the original
    spec ("attraction closing times (future)") — opening_hours parsing
    isn't wired to this package yet.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time

from .models import Move, MoveType, PlannerState

_MEAL_KEY = {MoveType.TAKE_LUNCH: "lunch", MoveType.TAKE_DINNER: "dinner"}


@dataclass(frozen=True)
class ConstraintProfile:
    daily_start: time = time(9, 0)
    daily_end: time = time(21, 0)

    lunch_window: tuple[time, time] = (time(12, 30), time(14, 0))
    dinner_window: tuple[time, time] = (time(19, 0), time(20, 30))
    lunch_duration_minutes: int = 60
    dinner_duration_minutes: int = 75

    max_walking_minutes_per_day: int = 90
    max_attraction_minutes_per_day: int = 480

    must_see_attraction_ids: frozenset[int] = field(default_factory=frozenset)
    excluded_attraction_ids: frozenset[int] = field(default_factory=frozenset)

    wheelchair_needed: bool = False


def is_legal(
    move: Move,
    parent_state: PlannerState,
    resulting_state: PlannerState,
    profile: ConstraintProfile,
) -> bool:
    """Called AFTER apply_move() has produced resulting_state, so this
    checks the consequences of the move (does it push arrival past
    daily_end, past walking/attraction-time caps) rather than
    re-deriving them independently. parent_state is only needed for
    checks that compare before/after (visited-already, meal-already-taken).
    """
    if move.move_type == MoveType.VISIT_ATTRACTION:
        if move.attraction_id in parent_state.visited_attraction_ids:
            return False
        if move.attraction_id in profile.excluded_attraction_ids:
            return False
        if resulting_state.current_time > profile.daily_end:
            return False
        if resulting_state.walking_minutes_today > profile.max_walking_minutes_per_day:
            return False
        if resulting_state.attraction_minutes_today > profile.max_attraction_minutes_per_day:
            return False
        return True

    if move.move_type in _MEAL_KEY:
        meal = _MEAL_KEY[move.move_type]
        if meal in parent_state.meals_taken_today:
            return False
        window = profile.lunch_window if move.move_type == MoveType.TAKE_LUNCH else profile.dinner_window
        if not (window[0] <= parent_state.current_time <= window[1]):
            return False
        if resulting_state.current_time > profile.daily_end:
            return False
        return True

    if move.move_type in (MoveType.END_DAY, MoveType.END_TRIP):
        # Always legal — this is what lets attraction-count-per-day
        # emerge from search rather than being hardcoded: the search can
        # choose "stop here" purely because the evaluator scores it
        # higher than squeezing in one more mediocre stop.
        return True

    return False