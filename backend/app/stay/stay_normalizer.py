#Converts raw GEOAPIFY hotel data into a common format to be used by VoyageAI

from math import radians,sin,cos,sqrt,atan2

#Infer approximate price category from stay type.
def infer_price_level(stay_type:str) -> str:
    stay_type = stay_type.lower()

    mapping = {
        "hostel": "budget",
        "guest house": "budget",
        "homestay": "budget",
        "hotel": "medium",
        "apartment": "medium",
        "resort": "luxury"
    }

    return mapping.get(
        stay_type,
        "medium"
    )

def haversine(lat1,lon1,lat2,lon2):
    #Returns distance in km between two coordinates

    R = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2 
        + cos(radians(lat1)) 
        * cos(radians(lat2)) 
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a),sqrt(1-a))
    return round(R * c, 2)

def infer_stay_type(categories):
    #Infer stay type from GEOAPIFY categories

    categories = [c.lower() for c in categories]

    if any("hostel" in c for c in categories):
        return "Hostel"
    if any("hotel" in c for c in categories):
        return "Hotel"
    if any("guest_house" in c for c in categories):
        return "Guest House"
    return "Stay"

def normalize_stays(stays,center_lat,center_lon):
    #Normalize GEOAPIGY response
    normalized = []

    for stay in stays:
        props = stay['properties']
        lat = props["lat"]
        lon = props["lon"]
        stay_type = infer_stay_type(
            props.get("categories",[])
        )

        normalized.append({
            "id": props.get("place_id"),

            "name": props.get("name", "Unknown"),

            "type": stay_type,

            "rating": None,

            "price_level": infer_price_level(
                stay_type=stay_type
            ),

            "lat": lat,

            "lon": lon,

            "address": props.get(
                "formatted",
                ""
            ),

            "website": props.get("website"),

            "phone": props.get("contact", {}).get("phone"),

            "distance_from_center": haversine(
                center_lat,
                center_lon,
                lat,
                lon,
            ),

            "categories": props.get("categories", [])
        })

        # print("Normalised",normalized)
    return normalized