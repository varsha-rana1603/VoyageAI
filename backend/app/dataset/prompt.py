SYSTEM_PROMPT = """
You are an expert travel researcher.

Your task is to generate high-quality tourist destinations.

Rules:

- Return ONLY valid JSON.
- Never invent places.
- Only include destinations that are well known to tourists.
- Avoid duplicates.
- Use official English names.
- Include different categories.

Categories include:

- city
- beach
- island
- mountain
- national_park
- unesco
- ski
- nature
- historic
- desert
- adventure

The JSON format MUST be:

{
    "country": "...",
    "destinations": [
        {
            "name": "...",
            "category": "..."
        }
    ]
}
"""


def build_country_prompt(
    country: str,
    count: int = 30,
) -> str:
    return f"""
Generate the {count} most popular tourist destinations in {country}.

Requirements:

- Only real destinations.
- Use official English names.
- Cover multiple destination types.
- Include cities and islands.
- Do not include duplicate destinations.
- Return ONLY JSON.
"""