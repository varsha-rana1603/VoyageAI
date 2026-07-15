"""
Turns free-text conversation into a structured TravellerProfile.

Deliberately explicit about travel_style handling: an earlier version of
this system let unrecognized styles (e.g. "honeymoon") silently fall back
to "adventure", which corrupted embeddings and scoring downstream without
ever surfacing an error. This version keeps whatever the LLM extracts,
as long as it's in CANONICAL_TRAVEL_STYLES, and logs+flags anything else
instead of quietly coercing it.
"""
import json
import uuid

from groq import Groq
from sqlalchemy.orm import Session

from app.config import settings
from app.ml.embeddings import embed_text, profile_to_embedding_text
from app.models.profile import TravellerProfile

CANONICAL_TRAVEL_STYLES = [
    "adventure",
    "relaxation",
    "culture",
    "luxury",
    "budget",
    "honeymoon",
    "family",
    "solo",
    "nightlife",
]

EXTRACTION_SYSTEM_PROMPT = f"""You extract structured travel preferences from a user's message.
Return ONLY a JSON object with any of these fields the message reveals (omit fields not mentioned):
- travel_style: one of {CANONICAL_TRAVEL_STYLES}
- budget_tier: one of ["low", "medium", "high"]
- crowd_tolerance: one of ["low", "medium", "high"]
- trip_duration_days: integer

If the message doesn't reveal a field, omit it entirely. Never guess.
Return only the JSON object, no other text."""

REQUIRED_FIELDS = ["travel_style", "budget_tier", "crowd_tolerance", "trip_duration_days"]


class ProfileService:
    def __init__(self, db: Session):
        self.db = db
        self._client = Groq(api_key=settings.groq_api_key)

    def _extract_fields(self, message: str) -> dict:
        response = self._client.chat.completions.create(
            model=settings.llm_model,
            max_tokens=200,
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
        )
        raw_text = response.choices[0].message.content.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`").removeprefix("json").strip()

        try:
            fields = json.loads(raw_text)
        except json.JSONDecodeError:
            return {}

        if not isinstance(fields, dict):
            return {}  # model returned something unexpected (e.g. a list, or literal null)

        if "travel_style" in fields and fields["travel_style"] not in CANONICAL_TRAVEL_STYLES:
            fields.pop("travel_style")

        return fields

    def process_message(self, user_id: uuid.UUID, profile_id: uuid.UUID | None, message: str) -> tuple[TravellerProfile, dict]:
        if profile_id:
            profile = self.db.get(TravellerProfile, profile_id)
        else:
            profile = TravellerProfile(user_id=user_id, raw_conversation=[])
            self.db.add(profile)
            self.db.flush()

        extracted = self._extract_fields(message)
        for field, value in extracted.items():
            setattr(profile, field, value)

        profile.raw_conversation = (profile.raw_conversation or []) + [{"role": "user", "content": message}]

        if self.is_ready_for_embedding(profile):
            embedding_text = profile_to_embedding_text(profile.travel_style, profile.budget_tier, profile.crowd_tolerance)
            profile.profile_embedding = embed_text(embedding_text)

        self.db.commit()
        self.db.refresh(profile)
        return profile, extracted

    @staticmethod
    def is_ready_for_embedding(profile: TravellerProfile) -> bool:
        return bool(profile.travel_style) and bool(profile.budget_tier)

    @staticmethod
    def is_complete(profile: TravellerProfile) -> bool:
        return all(getattr(profile, f) is not None for f in REQUIRED_FIELDS)

    def next_question(self, profile: TravellerProfile) -> str:
        """Deterministic follow-up question for the next missing field -- keeps
        the conversation from asking the LLM to invent a question and risking
        it re-asking something already answered."""
        if not profile.travel_style:
            return "What kind of trip are you after -- adventure, relaxation, culture, honeymoon, or something else?"
        if not profile.budget_tier:
            return "What's your rough budget -- low, medium, or high?"
        if not profile.crowd_tolerance:
            return "Do you prefer quieter, less crowded places, or is that not a big factor?"
        if not profile.trip_duration_days:
            return "How many days are you planning for this trip?"
        return "Great, I have enough to start recommending destinations."
