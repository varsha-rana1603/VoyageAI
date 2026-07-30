from app.trip_planner.domain.accommodation import Accommodation
from app.ml.embeddings import embed_text


def build_embedding_text(
    accommodation: Accommodation,
) -> str:

    parts = [
        accommodation.name,
        accommodation.hotel_category,
        accommodation.brand_name,
        accommodation.brand_tier,
        accommodation.location_type,
    ]

    parts.extend(accommodation.best_for)
    parts.extend(accommodation.amenities)

    if accommodation.pool:
        parts.append("pool")

    if accommodation.spa:
        parts.append("spa")

    if accommodation.business_friendly:
        parts.append("business hotel")

    if accommodation.family_friendly:
        parts.append("family friendly")

    if accommodation.star_rating:
        parts.append(
            f"{accommodation.star_rating} star"
        )

    text = ", ".join(
        str(p)
        for p in parts
        if p
    )

    accommodation.embedding_text = text

    return text


def generate_embedding(
    accommodation: Accommodation,
) -> Accommodation:

    text = build_embedding_text(
        accommodation,
    )

    accommodation.embedding = embed_text(
        text,
    )

    return accommodation