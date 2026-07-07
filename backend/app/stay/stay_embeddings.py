#Creates semantic descriptions and embeddings for stays.

from app.models import embedding_model


def build_stay_text(stay):
    text = f"""
        {stay['name']}.{stay["type"]}.{stay["price_level"]} accomodation.
        Located {stay['distance_from_center']} km from the town centre.
        Nature score {stay['nature_score']}.
        Tourism score {stay['tourism_score']}.
        Food scene score {stay['food_score']}.
        Shopping score {stay['shopping_score']}.
        Connectivity score {stay['connectivity_score']}.
        """

    return " ".join(text.split())

def embed_stay(stay):
    text = build_stay_text(stay)
    embedding = embedding_model.encode(text)
    stay["semantic_text"] = text
    stay["embedding"] = embedding
    return stay

def embed_stays(stays):
    return[embed_stay(stay) for stay in stays]