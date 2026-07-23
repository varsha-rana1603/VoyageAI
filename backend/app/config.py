"""
Central app configuration. All environment-driven settings live here so
nothing reaches into os.environ directly from business logic.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql+psycopg://varsha_bits:bitspilani@localhost:5432/voyageai"

    # LLM provider for conversational profile extraction + explanations.
    # Groq: free tier, no billing required, OpenAI-compatible API.
    groq_api_key: str = ""
    llm_model: str = "llama-3.3-70b-versatile"

    # Google Places API (new, not legacy) -- destination name/coords/terrain/description.
    google_places_api_key: str = ""

    # Open-Meteo climate API needs no key -- historical monthly normals, free.
    open_meteo_base_url: str = "https://archive-api.open-meteo.com/v1/archive"

    # Amadeus self-service API -- OAuth2 client credentials flow, used for
    # average nightly hotel rate per destination (see amadeus_client.py).
    amadeus_api_key: str = ""
    amadeus_api_secret: str = ""
    amadeus_base_url: str = "https://test.api.amadeus.com"  # self-service/test env; swap to api.amadeus.com in production

    # Embedding model used for both traveller profiles and destinations.
    # Must stay identical across both or cosine similarity is meaningless.
    embedding_model_name: str = "all-MiniLM-L6-v2"
    embedding_dimensions: int = 384

    # Scoring weights (Phase 1: rule-based, see app/ml/scoring.py)
    weight_style_match: float = 0.35
    weight_budget_fit: float = 0.30
    weight_season_fit: float = 0.20
    weight_crowd_fit: float = 0.15

    environment: str = "development"


settings = Settings()