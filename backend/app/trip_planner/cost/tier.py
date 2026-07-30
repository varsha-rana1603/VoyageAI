def infer_budget_tier(profile):

    budget = (
        profile.total_budget
        or profile.maximum_budget
    )

    days = profile.duration_days or 1

    travellers = (
        profile.traveller_count
        or 1
    )

    if not budget:
        return "mid_range"


    daily_budget = (
        budget
        /
        days
        /
        travellers
    )


    if daily_budget < 100:
        return "budget"

    if daily_budget < 300:
        return "mid_range"

    return "luxury"