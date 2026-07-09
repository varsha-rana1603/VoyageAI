def calculate_popularity(place):
    google = place.get(
        "google"
    )

    if not google:
        return 0
    rating = google.get(
        "rating",
        0
    )
    reviews = google.get(
        "reviews",
        0
    )
    review_score = min(reviews/5000,1) * 30
    rating_score = (rating / 5) * 60
    
    distance = place.get("distance") or 5000


    distance_score = max(
        0,
        10 - distance / 500
    )
    return round(
        rating_score + review_score + distance_score , 2
    )