from dotenv import load_dotenv

import os


load_dotenv()

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

if GEOAPIFY_API_KEY is None:
    raise Exception("Missing GEOAPIFY_API_KEY")