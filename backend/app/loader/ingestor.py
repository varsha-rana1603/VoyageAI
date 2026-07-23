from datetime import datetime

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.destination import Destination
from app.ml.embeddings import embed_text

from app.clients.places_client import get_place_details, search_destination
from app.loader.climate_processor import get_climate_profile
from app.loader.cost_loader import load_destination_profile
from app.loader.validation import (
    validate_place,
    validate_climate,
    validate_metadata,
    validate_cost_profile,
    validate_embedding,
)


def _enrich_and_upsert(db: Session, destination, country: str) -> str:
    """Enrich a single (name, country) destination via Google Places, Open
    Meteo (climate) and the LLM-based cost/metadata profile, then upsert it
    into Postgres. Returns 'created', 'updated', or 'skipped'."""

    # ----------------------------------------
    # Skip if already present in database
    # ----------------------------------------
    existing = (
        db.query(Destination)
        .filter(
            Destination.name == destination.name,
            Destination.country == country,
        )
        .first()
    )

    if existing:
        print("Already exists. Skipping.")
        return "skipped"

    query = f"{destination.name} {country}"
    print(f"Loading {query}...")

    # ----------------------------
    # 1. Google Places
    # ----------------------------
    search_result = search_destination(query)
    place = get_place_details(search_result["id"])
    validate_place(place)

    # ----------------------------
    # 2. Open Meteo climate
    # ----------------------------
    climate = get_climate_profile(
        latitude=place["latitude"],
        longitude=place["longitude"],
    )
    validate_climate(climate)

    # ----------------------------
    # 3. LLM-based destination profile (metadata + cost)
    # ----------------------------
    destination_profile = load_destination_profile(
        place["name"],
        place["country"],
    )
    print("DESTINATION_PROFILE: ", destination_profile)

    metadata = destination_profile["metadata"]
    validate_metadata(metadata)

    terrain = metadata["terrain"]
    travel_styles = metadata["travel_styles"]
    crowd = metadata["crowd_level"]
    description = metadata["description"]

    cost_profile = {
        "currency": destination_profile["currency"],
        "daily_cost": destination_profile["daily_cost"],
        "source": destination_profile["source"],
        "updated_at": destination_profile["updated_at"],
    }
    validate_cost_profile(cost_profile)

    # ----------------------------
    # 4. Embedding
    # ----------------------------
    embedding_text = f"""
    Destination:
    {place['name']}

    Country:
    {place['country']}

    Terrain:
    {terrain}

    Travel styles:
    {travel_styles}

    Best season:
    {climate['best_season']}

    Crowd:
    {crowd}

    Description:
    {description}
    """

    embedding = embed_text(embedding_text)
    validate_embedding(embedding)

    # ----------------------------
    # 5. Upsert (keyed on google_place_id)
    # ----------------------------
    existing = (
        db.query(Destination)
        .filter(Destination.google_place_id == place["google_place_id"])
        .first()
    )

    if existing:
        print("Updating existing destination")

        existing.name = place["name"]
        existing.country = place["country"]
        existing.description = description
        existing.latitude = place["latitude"]
        existing.longitude = place["longitude"]
        existing.cost_profile = cost_profile
        existing.best_season = climate["best_season"]
        existing.worst_season = climate["worst_season"]
        existing.terrain = terrain
        existing.travel_styles = travel_styles
        existing.typical_crowd_level = crowd
        existing.destination_embedding = embedding
        existing.data_updated_at = datetime.utcnow()

        db.commit()
        return "updated"

    print("Creating new destination")

    new_destination = Destination(
        name=place["name"],
        country=place["country"],
        description=description,
        latitude=place["latitude"],
        longitude=place["longitude"],
        cost_profile=cost_profile,
        best_season=climate["best_season"],
        worst_season=climate["worst_season"],
        terrain=terrain,
        travel_styles=travel_styles,
        typical_crowd_level=crowd,
        google_place_id=place["google_place_id"],
        destination_embedding=embedding,
    )

    print("Adding to db...")
    db.add(new_destination)
    db.commit()
    print("Added.")

    return "created"


def ingest_destinations(country: str, destinations, limit=None):
    """Enrich and upsert a list of (name, country) destinations into
    Postgres. `destinations` is any iterable of objects with .name and
    .country (e.g. the output of verify_dataset / deduplicate_destinations,
    or iter_destinations()).

    Returns (created_count, updated_count, skipped_count).
    """

    db: Session = SessionLocal()
    created = updated = skipped = 0

    try:
        for i, destination in enumerate(destinations):

            if limit is not None and i >= limit:
                break

            print(f"Destination: {destination.name}, {country}")

            try:
                result = _enrich_and_upsert(db, destination, country)

                if result == "created":
                    created += 1
                elif result == "updated":
                    updated += 1
                else:
                    skipped += 1

            except Exception as e:
                print(f"✗ Skipping {destination.name}, {country}: {e}")
                db.rollback()
                skipped += 1
                continue

    finally:
        db.close()

    return created, updated, skipped