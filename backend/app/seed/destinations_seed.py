"""
Phase 1 seed set: a small number of real destinations with researched cost
figures, not placeholder price_level buckets. base_cost_inr is a rough
total for base_cost_duration_days for one traveller, mid-range comfort --
meant as a defensible starting estimate, refine with real flight/hotel
data in Phase 2.

Run with: python -m app.seed.destinations_seed
"""
from app.database import SessionLocal
from app.ml.embeddings import embed_text
from app.models.destination import Destination

DESTINATIONS = [
    dict(name="Goa", country="India", description="Beaches, nightlife, Portuguese-era architecture, laid-back pace.",
         base_cost_inr=25000, base_cost_duration_days=5, best_season="Nov-Feb",
         travel_styles=["relaxation", "nightlife", "budget"], typical_crowd_level="high"),
    dict(name="Manali", country="India", description="Himalayan adventure town, trekking, snow, mountain views.",
         base_cost_inr=20000, base_cost_duration_days=5, best_season="Mar-Jun",
         travel_styles=["adventure", "budget", "honeymoon"], typical_crowd_level="medium"),
    dict(name="Udaipur", country="India", description="Lake city, palaces, romantic architecture, boutique hotels.",
         base_cost_inr=35000, base_cost_duration_days=4, best_season="Oct-Mar",
         travel_styles=["luxury", "honeymoon", "culture"], typical_crowd_level="medium"),
    dict(name="Rishikesh", country="India", description="Yoga, river rafting, spiritual retreats, Himalayan foothills.",
         base_cost_inr=15000, base_cost_duration_days=5, best_season="Sep-Apr",
         travel_styles=["adventure", "relaxation", "budget", "solo"], typical_crowd_level="low"),
    dict(name="Coorg", country="India", description="Coffee plantations, misty hills, quiet homestays.",
         base_cost_inr=22000, base_cost_duration_days=4, best_season="Oct-Mar",
         travel_styles=["relaxation", "honeymoon", "family"], typical_crowd_level="low"),
    dict(name="Ladakh", country="India", description="High-altitude desert, monasteries, extreme adventure, remote roads.",
         base_cost_inr=45000, base_cost_duration_days=7, best_season="Jun-Sep",
         travel_styles=["adventure", "solo"], typical_crowd_level="low"),
    dict(name="Jaipur", country="India", description="Forts, palaces, bazaars, classic Rajasthan culture circuit.",
         base_cost_inr=28000, base_cost_duration_days=4, best_season="Oct-Mar",
         travel_styles=["culture", "family", "budget"], typical_crowd_level="high"),
    dict(name="Andaman Islands", country="India", description="Coral reefs, scuba diving, remote white-sand beaches.",
         base_cost_inr=55000, base_cost_duration_days=6, best_season="Nov-May",
         travel_styles=["luxury", "honeymoon", "adventure"], typical_crowd_level="low"),
]


def seed():
    db = SessionLocal()
    try:
        for entry in DESTINATIONS:
            exists = db.query(Destination).filter_by(name=entry["name"]).first()
            if exists:
                continue
            embedding_text = f"{entry['description']} Styles: {', '.join(entry['travel_styles'])}."
            destination = Destination(**entry, destination_embedding=embed_text(embedding_text))
            db.add(destination)
        db.commit()
        print(f"Seeded {len(DESTINATIONS)} destinations (skipped any already present).")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
