from dataclasses import dataclass

from app.conversation.extractors.terrain import normalize


@dataclass
class TravelMonthPreference:
    month: int


MONTHS = {
    1: {"january", "jan"},
    2: {"february", "feb"},
    3: {"march", "mar"},
    4: {"april", "apr"},
    5: {"may"},
    6: {"june", "jun"},
    7: {"july", "jul"},
    8: {"august", "aug"},
    9: {"september", "sep", "sept"},
    10: {"october", "oct"},
    11: {"november", "nov"},
    12: {"december", "dec"},
}


def extract_travel_month(
    message: str,
) -> TravelMonthPreference | None:

    words = normalize(message)

    for month, keywords in MONTHS.items():

        keyword_stems = {
            normalize(keyword).pop()
            for keyword in keywords
        }

        if words & keyword_stems:
            return TravelMonthPreference(month)

    return None