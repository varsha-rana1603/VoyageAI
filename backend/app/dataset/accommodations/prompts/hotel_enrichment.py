HOTEL_ENRICHMENT_PROMPT = """
You are an expert in the global hospitality industry.

You are helping build a machine-learning powered hotel recommendation engine.

You will receive a JSON array of hotels.

For EACH hotel, infer semantic hotel attributes using:

- hotel name
- hotel chain
- Google rating
- review count
- website
- Google place types
- hotel category
- globally known hotel brands
- publicly known positioning of the hotel

Do NOT estimate prices.

Do NOT invent information that cannot reasonably be inferred.

Return ONLY a valid JSON array.

Hotels

{hotels}


=========================================================
STRICT OUTPUT SCHEMA
=========================================================

Return EXACTLY these fields and NO OTHER FIELDS.

Allowed fields:

id
brand_name
brand_tier
hotel_category
estimated_stars
luxury_positioning
location_type
location_quality_score
pool
spa
business_friendly
family_friendly
best_for
confidence


Forbidden fields:

luxury_score
business_score
family_score
romantic_score
wellness_score
budget_score
scores
ranking
reason
explanation
notes


Example:

[
    {{
        "id": 0,

        "brand_name": "JW Marriott",
        "brand_tier": "luxury",

        "hotel_category": "hotel",
        "estimated_stars": 5,

        "luxury_positioning": 0.90,

        "location_type": "city_center",
        "location_quality_score": 0.90,

        "pool": true,
        "spa": true,

        "business_friendly": true,
        "family_friendly": false,

        "best_for": [
            "business",
            "luxury"
        ],

        "confidence": 0.95
    }}
]


=========================================================
GENERAL RULES
=========================================================

Return ONE object for EVERY hotel.

Keep exactly the same id.

Never change or omit the id.

Never add extra fields.

Never remove fields.

Boolean values must never be null.

Arrays must never be null.

The JSON array must end after the confidence field.

=========================================================
brand_name
=========================================================

Return the hotel chain if it exists.

Examples:

JW Marriott
Marriott
Hilton
Conrad
Hyatt
Grand Hyatt
Hyatt Regency
Holiday Inn
InterContinental
Fairmont
Ritz-Carlton
Four Seasons
Jumeirah
Shangri-La
Novotel
Accor
Citymax
Millennium


If the hotel is independent return null.


=========================================================
brand_tier
=========================================================

Must be EXACTLY one of:

budget
midscale
upscale
luxury
ultra_luxury


Examples:

Citymax -> midscale

Holiday Inn Express -> budget

Holiday Inn -> midscale

Novotel -> upscale

Hilton -> upscale

Hyatt Regency -> upscale

Conrad -> luxury

JW Marriott -> luxury

InterContinental -> luxury

Fairmont -> luxury

Four Seasons -> ultra_luxury

Ritz-Carlton -> ultra_luxury


Important:

Do NOT classify a brand as luxury only because it is globally famous.

Use the individual property positioning.

Examples:

Hilton Dubai Al Habtoor City -> upscale

Conrad Dubai -> luxury

JW Marriott Marquis Dubai -> luxury

The Ritz-Carlton DIFC -> ultra_luxury

Four Seasons Dubai -> ultra_luxury


=========================================================
hotel_category
=========================================================

Must be EXACTLY one of:

hotel
resort
boutique
hostel
apartment
villa


=========================================================
estimated_stars
=========================================================

Official hotel star classification.

Must ONLY be:

1
2
3
4
5


Never use decimal values.

Never use Google rating.


=========================================================
luxury_positioning
=========================================================

Float between:

0.0
and
1.0


Examples:

0.05 hostel

0.20 economy

0.40 budget

0.60 upscale

0.80 luxury

1.00 iconic ultra luxury


=========================================================
location_type
=========================================================

Must be EXACTLY one of:

city_center
tourist_area
beach_area
business_district
airport_area
suburban


Infer from:

- hotel name
- website
- known location
- nearby landmarks
- hotel positioning


=========================================================
location_quality_score
=========================================================

Float between:

0.0
and
1.0


Higher means the location is more desirable for the hotel's target customers.


=========================================================
pool
=========================================================

Boolean.

Infer from:

- Google place types
- hotel category
- website
- hotel positioning


Luxury resorts usually have pools.

Beach resorts usually have pools.

Budget hotels often do not.


=========================================================
spa
=========================================================

Boolean.

Infer from:

- Google place types
- website
- hotel brand
- hotel positioning


Luxury hotels frequently have spas.

Wellness hotels frequently have spas.


=========================================================
business_friendly
=========================================================

Boolean.

True when the hotel is suitable for business travellers.

Consider:

- conference facilities
- business center
- meeting rooms
- financial district location
- airport proximity
- corporate hotel positioning


=========================================================
family_friendly
=========================================================

Boolean.

True when the hotel is suitable for families.

Consider:

- resorts
- kids activities
- family rooms
- pools
- beach location
- vacation positioning


Usually false for:

- airport hotels
- corporate hotels
- business district hotels


=========================================================
best_for
=========================================================

Return a JSON array.

Allowed values ONLY:

budget

luxury

business

family

couples

beach

shopping

nightlife

wellness

romantic

long_stay

airport


Examples:


JW Marriott Marquis Dubai:

[
    "luxury",
    "business"
]


Conrad Dubai:

[
    "luxury",
    "business"
]


Citymax:

[
    "budget"
]


Atlantis The Palm:

[
    "luxury",
    "family",
    "beach"
]


Airport business hotel:

[
    "business",
    "airport"
]


=========================================================
confidence
=========================================================

Float between:

0.0
and
1.0


Lower confidence when information is inferred.


=========================================================
FINAL VALIDATION
=========================================================

Before returning:

1. Verify every hotel has all required fields.
2. Verify no forbidden fields exist.
3. Verify JSON syntax is valid.
4. Verify the output ends after confidence.
5. Return ONLY JSON.

No markdown.

No explanations.

No comments.

No code fences.

"""