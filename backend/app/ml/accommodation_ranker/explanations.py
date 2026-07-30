def generate_accommodation_reasons(
    profile,
    accommodation,
) -> list[str]:

    reasons = []

    # -------------------------
    # User preference matching
    # -------------------------

    if "luxury" in profile.travel_styles:

        if accommodation.luxury_score >= 0.85:
            reasons.append(
                "Matches your luxury travel preference"
            )


    # -------------------------
    # Couple suitability
    # -------------------------

    if profile.is_couple:

        if accommodation.romantic_score >= 0.75:
            reasons.append(
                "Excellent choice for a romantic getaway"
            )

        elif accommodation.romantic_score >= 0.5:
            reasons.append(
                "Suitable for couples"
            )


    # -------------------------
    # Location advantages
    # -------------------------

    if accommodation.location_type:

        location = accommodation.location_type.replace(
            "_",
            " "
        )

        if accommodation.location_quality_score >= 0.8:

            reasons.append(
                f"Prime {location} location"
            )


    # -------------------------
    # Amenities
    # -------------------------

    if accommodation.pool:
        reasons.append(
            "Includes a swimming pool"
        )

    if accommodation.spa:
        reasons.append(
            "Offers spa and wellness facilities"
        )


    # -------------------------
    # Beach / Waterfront
    # -------------------------

    planner = accommodation.planner_metadata or {}

    if planner.get("waterfront"):
        reasons.append(
            "Waterfront property with scenic views"
        )


    # -------------------------
    # Ratings
    # -------------------------

    if accommodation.rating:

        if accommodation.rating >= 4.7:
            reasons.append(
                f"Highly rated by travellers ({accommodation.rating}/5)"
            )

        elif accommodation.rating >= 4.5:
            reasons.append(
                f"Excellent guest ratings ({accommodation.rating}/5)"
            )


    # -------------------------
    # Brand positioning
    # -------------------------

    if accommodation.brand_tier:

        if accommodation.brand_tier == "ultra_luxury":
            reasons.append(
                "Ultra-luxury hospitality experience"
            )

        elif accommodation.brand_tier == "luxury":
            reasons.append(
                "Luxury hospitality experience"
            )


    # -------------------------
    # Traveller type
    # -------------------------

    if accommodation.best_for:

        best_for = accommodation.best_for

        if "business" in best_for:
            reasons.append(
                "Well suited for business travellers"
            )

        if "family" in best_for:
            reasons.append(
                "Family-friendly accommodation"
            )


    # Limit UI clutter
    return reasons[:5]