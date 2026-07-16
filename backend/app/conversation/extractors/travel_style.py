from dataclasses import dataclass
from app.conversation.dictionaries.travel_style_keywords import TRAVEL_STYLE_KEYWORDS

@dataclass
class TravelStylePreference:
    travel_styles: list[str]

def extract_travel_styles(message: str) -> TravelStylePreference | None:
    text = message.lower()
    styles = set()

    for style, keywords in TRAVEL_STYLE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                styles.add(style)
                break
    
    if not styles:
        return None
    
    return TravelStylePreference(
        travel_styles=sorted(styles)
    )
