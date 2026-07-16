from dataclasses import dataclass
import re

from nltk.stem import PorterStemmer

from app.conversation.dictionaries.terrain_keywords import TERRAIN_KEYWORDS


stemmer = PorterStemmer()


def normalize(text: str) -> set[str]:
    words = re.findall(r"[a-z]+", text.lower())
    return {stemmer.stem(word) for word in words}


@dataclass
class TerrainPreference:
    terrain_preferences: list[str]


def extract_terrain_preferences(
    message: str,
) -> TerrainPreference | None:

    normalized_words = normalize(message)

    terrains = set()

    for terrain, keywords in TERRAIN_KEYWORDS.items():

        keyword_stems = {
            stemmer.stem(keyword)
            for keyword in keywords
        }

        if normalized_words & keyword_stems:
            terrains.add(terrain)

    if not terrains:
        return None

    return TerrainPreference(
        terrain_preferences=sorted(terrains)
    )