from dotenv import load_dotenv

import os


load_dotenv()

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_API_KEY")

if GEOAPIFY_API_KEY is None:
    raise Exception("Missing GEOAPIFY_API_KEY")
if GOOGLE_PLACES_API_KEY is None:
    raise Exception("Missing GOOGLE_API_KEY")