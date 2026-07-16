#explain recommendations

from app.clients.bedrock import generate_json


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
    """

    prompt = build_reason_prompt(destinations)

    response = generate_json(prompt)

    return {
        item["destination"]: item["reasons"]
        for item in response["destinations"]
    }