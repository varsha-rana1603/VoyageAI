#Single source truth for acco ranking model's feature columns.

FEATURE_NAMES = [
    #BUDGET
    "price_per_night_norm",
    "price_vs_budget_per_night_ratio",
    "price_within_budget_flag",

    #persona
    "persona_luxury",
    "persona_budget",
    "persona_business",
    "persona_family",

    #hotel quality
    "hotel_rating",
    "hotel_review_count_log",
    "hotel_star_rating",
    "hotel_quality_score",

    #brand
    "brand_tier_ordinal",
    "luxury_positioning_score",
    "has_recognized_brand",

    # --- location (numeric distances, not guessed string categories) ---
    "location_quality_score",
    "distance_from_city_center_km",
    "distance_to_metro_m_norm",
    "distance_to_main_attractions_km",
    "average_travel_time_minutes",

    # --- amenities (real boolean columns) ---
    "amenity_pool",
    "amenity_spa",
    "amenity_family_friendly",
    "amenity_business_friendly",

    # --- best_for enrichment match ---
    "best_for_matches_persona",

    # --- semantic (placeholder until embedding wiring exists) ---
    "semantic_similarity",

    # --- interaction features ---
    "persona_luxury_x_luxury_positioning",
    "persona_luxury_x_brand_tier",
    "persona_budget_x_price_ratio",
    "persona_business_x_business_friendly",
    "persona_business_x_metro_distance",
    "persona_family_x_pool",
    "persona_family_x_family_friendly",
]