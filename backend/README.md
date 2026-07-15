# VoyageAI backend — Phase 1

Traveller profile builder, destination ranking, and budget estimation.
No hotels, safety scoring, itinerary generation, or real-time features yet
— those are Phase 2+.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in ANTHROPIC_API_KEY and DATABASE_URL
```

Postgres must have the `vector` extension available (pgvector). Then:

```bash
python init_db.py                       # creates tables + enables pgvector
python -m app.seed.destinations_seed     # seeds 8 starter destinations
uvicorn app.main:app --reload            # http://localhost:8000
```

## Endpoints

- `POST /api/profile/message` — send one conversation turn, get the next question back
- `GET /api/profile/{profile_id}` — fetch structured profile so far
- `POST /api/destinations/recommend` — ranked destinations for a profile
- `GET /api/destinations/{id}/budget?profile_id=` — cost breakdown for one destination

## Design notes

- **Scoring is rule-based** (`app/ml/scoring.py`), not learned — there's no
  interaction data yet to train a ranker on. Weights live in `config.py`.
- **`travel_style` is validated against a canonical list**, never silently
  coerced to a different value if the LLM returns something unrecognized
  (`app/services/profile_service.py`).
- **Destination cost is a researched `base_cost_inr` per destination**, not
  a Google Places `price_level` bucket — see `app/models/destination.py`
  and `app/seed/destinations_seed.py`.
- **Embedding model must stay identical** between profile and destination
  embedding calls (`app/ml/embeddings.py`) — cosine similarity is meaningless
  otherwise.
- Explanations for recommendations are template-based, not LLM-generated —
  reproducible and free; an LLM pass for more natural phrasing is a
  reasonable Phase 2 add-on, not required for Phase 1.

## What's deliberately NOT here yet

Hotels/stays, safety scoring, neighbourhood analysis, itinerary generation,
multi-destination trip splitting, real-time monitoring, and any external
API beyond the LLM (no Amadeus, OpenWeather, Google Places yet). See the
phased roadmap discussed with Claude for when these get added.
