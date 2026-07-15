from datetime import datetime

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.destination import Destination
from app.ml.embeddings import embed_text

from app.clients.places_client import get_place_details, search_destination, extract_country
from app.loader.climate_processor import get_climate_profile
from app.loader.cost_loader import load_destination_profile
from app.loader.destination_source import iter_destinations

def load_destinations():

    db: Session = SessionLocal()

    try:
        print("Trying")

        for i, destination in enumerate(iter_destinations()):

            if i >= 50:
                break

            print("Destination:", destination.country)
            try:
                query = f"{destination.name} {destination.country}"
            

                print(
                    f"\nLoading {query}..."
                )

                # ----------------------------
                # 1. Google Places
                # ----------------------------

                search_result = search_destination(query)
                place = get_place_details(search_result["id"])                

                climate = get_climate_profile(
                    latitude=place["latitude"],
                    longitude=place["longitude"]
                )
                print("CLIMATE: ", climate)

                destination_profile = load_destination_profile(
                    place["name"],
                    place["country"]
                )     

                print("DESTINATION_PROFILE: ", destination_profile)

                metadata = destination_profile["metadata"]
                print("METADATA: ", metadata)

                terrain = metadata["terrain"]

                travel_styles = metadata["travel_styles"]

                crowd = metadata["crowd_level"]

                cost_profile = {
                    "currency": destination_profile["currency"],
                    "daily_cost": destination_profile["daily_cost"],
                    "source": destination_profile["source"],
                    "updated_at": destination_profile["updated_at"],

                }

                description = metadata["description"]

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


                embedding = embed_text(
                    embedding_text
                )

                #UPSERT DB

                existing = (
                    db.query(Destination)
                    .filter(
                        Destination.google_place_id
                        ==
                        place["google_place_id"]
                    )
                    .first()
                )


                if existing:

                    print(
                        "Updating existing destination"
                    )

                    existing.name = place["name"]
                    existing.country = place["country"]
                    existing.description = description
                    existing.latitude = place["latitude"]
                    existing.longitude = place["longitude"]

                    existing.cost_profile = cost_profile

                    existing.best_season = (
                        climate["best_season"]
                    )

                    existing.worst_season = (
                        climate["worst_season"]
                    )

                    existing.terrain = terrain

                    existing.travel_styles = (
                        travel_styles
                    )

                    existing.typical_crowd_level = crowd

                    existing.destination_embedding = (
                        embedding
                    )

                    existing.data_updated_at = (
                        datetime.utcnow()
                    )


                else:

                    print(
                        "Creating new destination"
                    )


                    destination = Destination(
                        name=place["name"],

                        country=place["country"],

                        description=description,

                        latitude = place["latitude"],
                        longitude = place["longitude"],

                        cost_profile = cost_profile,

                        best_season=(
                            climate["best_season"]
                        ),

                        worst_season=(
                            climate["worst_season"]
                        ),

                        terrain=terrain,

                        travel_styles=travel_styles,

                        typical_crowd_level=crowd,

                        google_place_id=(
                            place["google_place_id"]
                        ),

                        destination_embedding=embedding
                    )

                    print("Adding to db...")
                    db.add(destination)
                    print("Added. Commiting.")

                db.commit()


                print(
                    "\nDestination loading complete."
                )
            except Exception as e:
                print(
                    f"✗ Skipping {destination.name}, {destination.country}: {e}"
                )
                db.rollback()
                continue
    finally:
        db.close()



if __name__ == "__main__":

    load_destinations()