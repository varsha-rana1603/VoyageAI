from dotenv import load_dotenv
import boto3
import json
import os

load_dotenv()

client = boto3.client(
    "bedrock-runtime",
    region_name=os.environ["AWS_DEFAULT_REGION"]
)

MODEL_ID = "amazon.nova-lite-v1:0"


def build_prompt(city: str, country: str) -> str:
    return f"""
You are an expert travel destination analyst.

Analyze the destination below and estimate realistic CURRENT (2026) tourist costs.

City:
{city}

Country:
{country}

Return ONLY valid JSON.

{{
    "currency":"",

    "daily_cost":{{

        "budget":{{
            "accommodation":0,
            "food":0,
            "transport":0,
            "activities":0,
            "misc":0
        }},

        "mid_range":{{
            "accommodation":0,
            "food":0,
            "transport":0,
            "activities":0,
            "misc":0
        }},

        "luxury":{{
            "accommodation":0,
            "food":0,
            "transport":0,
            "activities":0,
            "misc":0
        }}
    }},

    "metadata":{{
        "terrain":[],
        "travel_styles":[],
        "crowd_level":"",

        "trip_duration_days":0,

        "family_friendly":true,
        "honeymoon":true,
        "solo_friendly":true,
        "group_friendly":true,
        "digital_nomad":false,

        "budget_friendly":true,

        "luxury_level":"",

        "nightlife":"",

        "shopping":"",

        "safety":"",

        "adventure_score":0,
        "relaxation_score":0,
        "culture_score":0,
        "food_score":0,
        "shopping_score":0,
        "nature_score":0,

        "description":""
    }}
}}

###############################
COST RULES
###############################

Estimate realistic CURRENT (2026) prices.

Do NOT underestimate.

Accommodation:

Budget = hostel / guesthouse

Mid-range = 3-star hotel

Luxury = 4-5 star hotel

Food:

Budget = street food

Mid-range = restaurants

Luxury = gourmet dining

Transport:

Average tourist usage.

Activities:

Typical sightseeing.

Misc:

Coffee, snacks, tips.

Use realistic numbers.

Examples:

83

142

367

Don't round excessively.

###############################
METADATA RULES
###############################

Terrain may ONLY contain:

[
"city",
"mountain",
"beach",
"forest",
"lake",
"river",
"island",
"desert",
"coastal",
"snow",
"volcanic"
]

Travel styles may ONLY contain:

[
"adventure",
"nature",
"relaxation",
"romantic",
"culture",
"touring",
"wildlife",
"food",
"luxury",
"road_trip",
"history",
"skiing",
"beach_holiday"
]

Crowd level:

low

medium

high

Nightlife:

low

medium

high

Shopping:

low

medium

high

Safety:

low

medium

high

Luxury level:

low

medium

high

All scores are integers from 1 to 10.

Trip duration should be the typical itinerary length.

Description should be less than 40 words.

Return ONLY JSON.

No markdown.

No explanation.
"""


def generate_destination_profile(
    city: str,
    country: str,
) -> dict:

    prompt = build_prompt(city, country)

    response = client.converse(
        modelId=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
    )

    text = response["output"]["message"]["content"][0]["text"].strip()

    # Remove markdown if the model adds it
    if text.startswith("```"):
        lines = text.splitlines()

        lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines)

    return json.loads(text)