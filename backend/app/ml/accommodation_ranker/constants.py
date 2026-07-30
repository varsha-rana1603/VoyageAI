FEATURE_NAMES = [

    # =====================================================
    # USER FEATURES
    # =====================================================

    "log_budget",
    "duration_days",
    "adults",
    "children",
    "is_family",
    "is_couple",
    "is_solo",
    "is_business",

    # =====================================================
    # HOTEL FEATURES
    # =====================================================

    "log_price",
    "rating",
    "log_review_count",
    "star_rating",
    "quality_score",
    "luxury_score",
    "business_score",
    "family_score",
    "romantic_score",
    "wellness_score",
    "budget_score",

    "distance_from_city_center_km",

    "pool",
    "spa",
    "family_friendly",
    "business_friendly",

    # =====================================================
    # LOCATION FEATURES
    # =====================================================

    "walkability",
    "shopping",
    "nightlife",
    "waterfront",
    "poi_density",

    # =====================================================
    # INTERACTION FEATURES
    # =====================================================

    "budget_match",

    "family_x_family_score",
    "business_x_business_score",
    "couple_x_romantic_score",
    "solo_x_budget_score",
    "family_x_wellness_score",
    "couple_x_wellness_score",
    "luxury_style_x_luxury_score",

    # =====================================================
    # EMBEDDING
    # =====================================================

    "semantic_similarity",
]