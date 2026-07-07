#Enriches normalizes stays with additional attributes used by the VoyageAI ranking engine

from typing import Dict

def infer_price_level(stay_type: str) -> str:
    #infer an approximate price level from stay type.

    stay_type = stay_type.lower()

    if stay_type in ["hostel","guest house","homestay"]:
        return "budget"
    if stay_type in ["hotel", "resort"]:
        return "medium"
    
    return "medium"

def distance_score(distance: float) -> int:
    #Convert distance from town square into a score.
    if distance <= 1:
        return 100
    if distance <= 3:
        return 90
    if distance <= 5:
        return 80
    if distance <= 8:
        return 70
    return 60

def infer_nature_score(region: str) -> int:
    region = region.lower()
    mapping = {
        "mountains": 95,
        "beach": 90,
        "forest": 92,
        "desert": 80,
        "city": 45,
        "backwaters": 88
    }

    return mapping.get(region,70)

def enrich_stay(stay:Dict, region_type:str) -> Dict:
    #Add AI-friendly attributes.

    stay["price_level"] = infer_price_level(stay["type"])
    stay["distance_score"] = distance_score(stay["distance_from_center"])
    stay["nature_score"] = infer_nature_score(region_type)
    stay["tourism_score"] = 70
    stay["food_score"] = 65
    stay["shopping_score"] = 55
    stay["connectivity_score"] = 70
    return stay

def enrich_stays(stays,region_type):
    enriched = []

    for stay in stays:
        enriched.append(
            enrich_stay(stay,region_type)
        )

    return enriched