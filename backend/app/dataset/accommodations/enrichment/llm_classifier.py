"""
Batch hotel semantic enrichment using Amazon Bedrock.

Responsibilities
----------------
✓ Build one prompt for multiple hotels
✓ Call Bedrock once
✓ Parse JSON response
✓ Return semantic features mapped by google_place_id

Not responsible for
-------------------
✗ Applying features
✗ Quality scoring
✗ Pricing
✗ Persistence
"""

import json

from app.clients.bedrock import generate_json
from app.trip_planner.domain.accommodation import Accommodation

from .schemas import HotelSemanticFeatures
from ..prompts.hotel_enrichment import HOTEL_ENRICHMENT_PROMPT


# ---------------------------------------------------------
# Build Prompt
# ---------------------------------------------------------

def build_prompt(
    accommodations: list[Accommodation],
) -> str:

    hotels = []

    for idx, accommodation in enumerate(accommodations):

        hotels.append(
            {
                "id": idx,
                "name": accommodation.name,
                "rating": accommodation.rating,
                "reviews": accommodation.review_count,
                "website": accommodation.website,
                "tags": accommodation.tags,
            }
        )

    return HOTEL_ENRICHMENT_PROMPT.format(
        hotels=json.dumps(
            hotels,
            indent=2,
        ),
    )


# ---------------------------------------------------------
# Batch Enrichment
# ---------------------------------------------------------

HOTEL_CATEGORY_MAP = {
    "hotel": "hotel",
    "resort": "resort",
    "resort_hotel": "resort",
    "boutique": "boutique",
    "boutique_hotel": "boutique",
    "hostel": "hostel",
    "apartment": "apartment",
    "serviced_apartment": "apartment",
    "villa": "villa",
}

def enrich_hotels_with_llm(
    accommodations: list[Accommodation],
) -> dict[str, HotelSemanticFeatures]:

    if not accommodations:
        return {}

    prompt = build_prompt(
        accommodations,
    )

    response = generate_json(
        prompt,
        temperature=0.2,
    )

    if not isinstance(response, list):
        raise ValueError(
            "LLM did not return a JSON array."
        )

    results: dict[str, HotelSemanticFeatures] = {}

    for item in response:

        hotel = accommodations[item["id"]]

        item["google_place_id"] = (
            hotel.google_place_id
        )

        item["hotel_category"] = HOTEL_CATEGORY_MAP.get(
            item.get("hotel_category"),
            "hotel",
        )

        features = HotelSemanticFeatures(

            brand_name=item.get(
                "brand_name"
            ),

            brand_tier=item.get(
                "brand_tier"
            ),

            hotel_category=HOTEL_CATEGORY_MAP.get(
                item.get("hotel_category"),
                "hotel",
            ),

            estimated_stars=item.get(
                "estimated_stars",
                3,
            ),

            luxury_positioning=item.get(
                "luxury_positioning",
                0.5,
            ),

            location_type=item.get(
                "location_type",
                "city_center",
            ),

            location_quality_score=item.get(
                "location_quality_score",
                0.5,
            ),

            pool=item.get(
                "pool",
                False,
            ),

            spa=item.get(
                "spa",
                False,
            ),

            business_friendly=item.get(
                "business_friendly",
                False,
            ),

            family_friendly=item.get(
                "family_friendly",
                False,
            ),
        

            best_for=item.get(
                "best_for",
                [],
            ),

            confidence=item.get(
                "confidence",
                0.8,
            ),
        )

        results[hotel.google_place_id] = features

    return results


# ---------------------------------------------------------
# Convenience Wrapper
# ---------------------------------------------------------

def enrich_hotel_with_llm(
    accommodation: Accommodation,
) -> HotelSemanticFeatures:

    return next(
        iter(
            enrich_hotels_with_llm(
                [accommodation],
            ).values()
        )
    )