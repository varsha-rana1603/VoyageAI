from dataclasses import dataclass

from app.conversation.extractors.terrain import normalize


@dataclass
class CrowdPreference:
    crowd: str


LOW = {
    "quiet",
    "peaceful",
    "hidden",
    "uncrowded",
    "secluded",
    "calm",
    "tranquil",
}

HIGH = {
    "busy",
    "crowded",
    "lively",
    "vibrant",
    "nightlife",
    "touristy",
}


def extract_crowd_preference(
    message: str,
) -> CrowdPreference | None:

    words = normalize(message)

    low = {
        normalize(word).pop()
        for word in LOW
    }

    high = {
        normalize(word).pop()
        for word in HIGH
    }

    if words & low:
        return CrowdPreference("low")

    if words & high:
        return CrowdPreference("high")

    return None