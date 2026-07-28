from .models import TripCostEstimate

def estimate_attraction_cost(attractions):
    total = 0
    for attraction in attractions: 
        cost = (attraction.estimated_cost or 0)
        total += cost
    return total