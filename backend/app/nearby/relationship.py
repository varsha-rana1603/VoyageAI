from math import radians, sin, cos, sqrt, atan2


CATEGORY_DISTANCE = {

    "culture": 15,      # museums, monuments, landmarks
    "nature": 20,       # parks, viewpoints, hiking areas
    "food": 5,           # restaurants, cafes
    "shopping": 8        # malls, markets

}


def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):
    """
    Returns distance in meters between two coordinates
    """

    R = 6371000

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)


    a = (
        sin(dlat / 2) ** 2
        +
        cos(radians(lat1))
        *
        cos(radians(lat2))
        *
        sin(dlon / 2) ** 2
    )


    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )


    return R * c



def get_relationship_message(
    category,
    distance_km
):

    if category == "food":

        if distance_km <= 2:
            return "A convenient dining option close to your stay"

        return "A popular food spot worth visiting nearby"


    if category == "shopping":

        if distance_km <= 3:
            return "Easy shopping option near your stay"

        return "A recommended shopping destination within reach"


    if category == "nature":

        if distance_km <= 5:
            return "A peaceful natural escape close to your stay"

        return "A scenic spot worth the short trip"


    if category == "culture":

        if distance_km <= 5:
            return "A major cultural attraction close to your stay"

        return "A highlight attraction worth exploring from your stay"


    return "A recommended place near your stay"



def get_category_threshold(place):

    category = place.get(
        "category",
        "culture"
    )

    return CATEGORY_DISTANCE.get(
        category,
        15
    )



def link_sights_to_stays(
    sights,
    stays
):
    """
    Adds nearby recommended stays to every sight
    """

    for sight in sights:

        sight["nearby_stays"] = []


        threshold_km = CATEGORY_DISTANCE.get(
            sight.get("category", "culture"),
            15
        )


        for stay in stays:

            distance = calculate_distance(
                stay["lat"],
                stay["lon"],
                sight["lat"],
                sight["lon"]
            )


            distance_km = distance / 1000


            if distance_km <= threshold_km:

                sight["nearby_stays"].append({

                    "name": stay["name"],

                    "distance_km":
                        round(distance_km, 1),

                    "message":
                        get_relationship_message(
                            sight.get("category"),
                            distance_km
                        )

                })


    return sights



def link_stays_to_sights(
    stays,
    sights
):
    """
    Adds nearby recommended sights to every stay
    """

    for stay in stays:

        stay["nearby_sights"] = []


        for sight in sights:

            threshold_km = CATEGORY_DISTANCE.get(
                sight.get("category", "culture"),
                15
            )


            distance = calculate_distance(
                stay["lat"],
                stay["lon"],
                sight["lat"],
                sight["lon"]
            )


            distance_km = distance / 1000


            if distance_km <= threshold_km:

                stay["nearby_sights"].append({

                    "name": sight["name"],

                    "category": sight.get(
                        "category",
                        "culture"
                    ),

                    "distance_km":
                        round(distance_km, 1),

                    "message":
                        get_relationship_message(
                            sight.get("category"),
                            distance_km
                        )

                })


    return stays