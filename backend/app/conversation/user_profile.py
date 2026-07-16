from pydantic import BaseModel
from typing import Optional, List


class UserProfile(BaseModel):

    total_budget: Optional[int] = None
    minimum_budget: Optional[int] = None
    maximum_budget: Optional[int] = None

    duration_days: Optional[int] = None

    travel_month: Optional[str] = None

    terrain_preferences: List[str] = []

    travel_styles: List[str] = []

    crowd_preference: Optional[str] = None

    accommodation_type: Optional[str] = None

    traveller_count: Optional[int] = None

    adults: Optional[int] = None
    children: Optional[int] = None

    is_solo: bool = False
    is_couple: bool = False
    is_family: bool = False
    is_friends: bool = False
    is_business: bool = False


    # lifestyle

    food_importance: Optional[int] = None
    nightlife_importance: Optional[int] = None
    adventure_importance: Optional[int] = None
    relaxation_importance: Optional[int] = None
    culture_importance: Optional[int] = None
    nature_importance: Optional[int] = None


    free_text: str = ""