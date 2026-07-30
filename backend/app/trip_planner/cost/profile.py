from .models import CostProfile
from .tier import infer_budget_tier

def get_cost_profile(
    destination,
    user_profile
):

    tier = infer_budget_tier(
        user_profile
    )

    daily_cost = destination.metadata_json.get(
        "daily_cost"
    )

    profile = daily_cost[tier]

    return CostProfile(
        accommodation=profile["accommodation"],
        food=profile["food"],
        transport=profile["transport"],
        activities=profile["activities"],
        misc=profile["misc"],
    )