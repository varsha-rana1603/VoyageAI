"""Generates polished, natural-language explanations for already-ranked
destinations. The LLM never influences ranking or invents reasons — it only
rewrites the supplied matched_features into readable sentences.
"""

import logging

from app.clients.bedrock import generate_json

logger = logging.getLogger(__name__)


def build_reason_prompt(destinations: list[dict]) -> str:
    return f"""
You are an expert travel advisor.

The recommendation engine has ALREADY selected the best destinations.

DO NOT change their ranking.
DO NOT recommend different destinations.
DO NOT invent new matching reasons.

Your only job is to rewrite the supplied matched features into concise,
natural explanations that would help a traveler understand why each
destination suits them.

Return ONLY valid JSON.

Format:

{{
    "destinations":[
        {{
            "destination":"Bali",
            "reasons":[
                "...",
                "...",
                "..."
            ]
        }}
    ]
}}

Rules:

- Generate 3 reasons maximum.
- Each reason should be one sentence.
- Keep each reason under 20 words.
- Sound like a knowledgeable travel advisor.
- Use only the supplied matched features.
- Do not mention scores.
- Do not mention embeddings or AI.
- Return ONLY JSON.

Destinations:

{destinations}
"""


def generate_reasons(destinations: list[dict]) -> dict[str, list[str]]:
    """
    destinations = [
        {
            "destination": "Bali",
            "matched_features": [
                "preferred terrain: beach",
                "travel style: relaxation",
                "fits the user's budget",
                "excellent during July"
            ]
        },
        ...
    ]

    Returns a dict of destination name -> list of polished reason strings.

    On any failure (Bedrock error, malformed JSON, unexpected shape), falls
    back to the raw matched_features for every destination rather than
    failing the whole recommendation request — the ranking and matching
    already succeeded deterministically before this function was ever
    called, so a language-polish failure shouldn't take that down with it.
    """

    fallback = {
        item["destination"]: item["matched_features"]
        for item in destinations
    }

    try:
        prompt = build_reason_prompt(destinations)
        response = generate_json(prompt)

        result = {
            item["destination"]: item["reasons"]
            for item in response["destinations"]
        }
    except Exception as exc:
        logger.error("Reason generation failed, falling back to matched_features: %s", exc)
        return fallback

    # Validate coverage: if the LLM dropped any destinations, fill the
    # gaps from matched_features rather than silently shipping empty
    # reason lists.
    missing = set(fallback.keys()) - set(result.keys())
    if missing:
        logger.warning("Reason generation missing destinations: %s", missing)
        for name in missing:
            result[name] = fallback[name]

    return result