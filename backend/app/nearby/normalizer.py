from math import radians, sin, cos, sqrt, atan2


def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):

    R = 6371000

    dlat = radians(lat2-lat1)
    dlon = radians(lon2-lon1)

    a = (
        sin(dlat/2)**2
        +
        cos(radians(lat1))
        *
        cos(radians(lat2))
        *
        sin(dlon/2)**2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1-a)
    )

    return R*c

def normalize_geoapify_places(features, user_lat, user_lon):

    places=[]


    for feature in features:

        properties = feature.get(
            "properties",
            {}
        )


        place_lat = properties.get("lat")
        place_lon = properties.get("lon")


        places.append({

            "name": properties.get("name"),

            "address": properties.get("formatted"),

            "latitude": place_lat,

            "longitude": place_lon,

            "distance":
                calculate_distance(
                    user_lat,
                    user_lon,
                    place_lat,
                    place_lon
                ),

            "categories":
                properties.get(
                    "categories",
                    []
                )

        })


    return places