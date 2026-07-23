from app.trip_planner.domain.accommodation import Accommodation


def enrich_tags(accommodation: Accommodation) -> None:
    tags: set[str] = set()

    if accommodation.price_tier:
        tags.add(accommodation.price_tier)

    if accommodation.lodging_type:
        tags.add(accommodation.lodging_type)

    if accommodation.pool:
        tags.add("pool")

    if accommodation.spa:
        tags.add("spa")

    if accommodation.family_friendly:
        tags.add("family")

    if accommodation.business_friendly:
        tags.add("business")

    accommodation.tags = sorted(tags)

TYPE_DESCRIPTIONS = {
    "hotel": "Comfortable hotel suitable for most travellers.",
    "hostel": "Budget-friendly accommodation popular with backpackers.",
    "guest_house": "Local guest house offering a cozy stay.",
    "resort": "Resort focused on leisure and relaxation.",
    "bed_and_breakfast": "Small accommodation with breakfast included.",
}    


def enrich_descriptions(accommodation: Accommodation) -> None:
    if accommodation.description:
        return

    accommodation.description = TYPE_DESCRIPTIONS.get(
        accommodation.lodging_type,
        "Accommodation for travellers."
    )

def enrich_metadata(accommodation: Accommodation) -> None:
    accommodation.planner_metadata = {
        "highly_rated": (
            accommodation.rating is not None and accommodation.rating >= 4.5
        ),
        "popular": (
            accommodation.review_count is not None
            and accommodation.review_count >= 500
        ),
        "budget_option": accommodation.price_tier == "budget",
        "luxury_option": accommodation.price_tier == "luxury",
    }

def enrich_embedding_text(accommodation: Accommodation) -> None:
    parts = [
        accommodation.name,
        accommodation.description or "",
        accommodation.lodging_type or "",
        accommodation.price_tier or "",
        " ".join(accommodation.tags),
        " ".join(accommodation.amenities),
    ]

    accommodation.embedding_text = "\n".join(
        part for part in parts if part
    )


def enrich(accommodation: Accommodation) -> Accommodation:
    enrich_descriptions(accommodation)
    enrich_tags(accommodation)
    enrich_metadata(accommodation)
    enrich_embedding_text(accommodation)

    return accommodation