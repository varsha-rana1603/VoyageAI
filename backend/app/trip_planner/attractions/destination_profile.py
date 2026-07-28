KYOTO_PROFILE = {

    "preferred_categories": [
        "temple",
        "shrine",
        "garden",
        "heritage",
        "museum",
    ],

    "avoid_categories": [
        "bar",
        "nightclub",
    ],

    "search_terms": [
        "temples",
        "shrines",
        "traditional districts",
        "zen gardens",
        "cultural heritage",
    ]

}


ROME_PROFILE = {

    "preferred_categories": [
        "ancient_site",
        "museum",
        "church",
        "archaeological",
    ],

    "search_terms": [
        "roman ruins",
        "historic monuments",
        "art museums",
    ]

}


DESTINATION_PROFILES = {

    "Kyoto": KYOTO_PROFILE,

    "Rome": ROME_PROFILE,

}

def get_destination_profile(
    destination_name: str,
):

    return DESTINATION_PROFILES.get(
        destination_name,
        {}
    )