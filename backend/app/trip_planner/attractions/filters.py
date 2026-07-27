"""
app/trip_planner/attractions/filters.py

Single responsibility: decide which attractions are even eligible to be
scored. Hard exclusions only — never a soft "this seems less relevant"
judgment, since that's what scorer.py's weighted factors are for.

Keeping this separate from scorer.py matters because the two answer
different questions: filters.py asks "should this attraction be
considered at all for this traveller/destination", scorer.py asks
"given it's eligible, how well does it rank". Mixing them makes it
harder to reason about why something never appeared vs. why it ranked
low.

Nothing here should ever be a *preference* (e.g. "user prefers indoor")
— that's scoring, not filtering. Only put something here if there's no
reasonable score, just an exclusion (wrong destination, permanently
closed, explicitly excluded by the user, hard accessibility mismatch).
"""

from __future__ import annotations

from .models import AttractionLike, UserProfileLike


def is_eligible(
    attraction: AttractionLike,
    destination_id,
    excluded_attraction_ids: set | None = None,
    wheelchair_needed: bool = False,
) -> bool:

    if excluded_attraction_ids and attraction.id in excluded_attraction_ids:
        return False

    if wheelchair_needed and "wheelchair_inaccessible" in attraction.tags:
        return False

    if "permanently_closed" in attraction.tags:
        return False

    return True


def filter_eligible(
    attractions: list[AttractionLike],
    destination_id,
    excluded_attraction_ids: set | None = None,
    wheelchair_needed: bool = False,
) -> list[AttractionLike]:
    return [
        a for a in attractions
        if is_eligible(a, destination_id, excluded_attraction_ids, wheelchair_needed)
    ]