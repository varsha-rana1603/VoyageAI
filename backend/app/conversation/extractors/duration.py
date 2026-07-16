from dataclasses import dataclass
import re

@dataclass

class DurationPreference:
    minimum: int | None = None
    maximum: int | None = None
    target: int | None = None

DAY_UNITS = {
    "day",
    "days"
}
WEEK_UNITS = {
    "week",
    "weeks"
}
MONTH_UNITS = {
    "month",
    "months"
}
YEAR_UNITS = {
    "year",
    "years"
}

def parse_days(value: str, unit: str) -> int:
    value = float(value)

    if unit.lower() in DAY_UNITS:
        return int(value)
    
    if unit.lower() in WEEK_UNITS:
        return int(value * 7)
    
    if unit.lower() in MONTH_UNITS:
        return (value * 30)
    
    if unit.lower() in YEAR_UNITS:
        return (value * 365)
    
    return int(value)

def extract_duration(message:str) -> DurationPreference | None:

    text = message.lower()

    #RANGE
    match = re.search(r"""
        (?:between|from)?
        \s*
        (\d+(?:\.\d+)?)
        \s*
        (day|days|week|weeks|month|month|year|years)?
        \s*
        (?:and|to|-)
        \s*
        (\d+(?:\.\d+)?)
        \s*
        (day|days|week|weeks|month|month|year|years)?
        """,
        text,
        re.VERBOSE
    )

    if match:
        value1, unit1, value2, unit2 = match.groups()
        if unit1 is None and unit2 is not None: 
            unit1 = unit2
        if unit2 is None and unit1 is not None:
            unit2 = unit1
        unit1 = unit1 or "days"
        unit2 = unit2 or "days"

        minimum = parse_days(value1, unit1)
        maximum = parse_days(value2, unit2)

        if minimum > maximum:
            minimum, maximum = maximum, minimum

        return DurationPreference(
            minimum=minimum,
            maximum=maximum,
        )       
    
    # Minimum

    match = re.search(
        r"""
        (?:at\s+least|minimum|min|more\s+than)
        \s*
        (\d+(?:\.\d+)?)
        \s*
        (day|days|week|weeks|month|month|year|years)
        """,
        text,
        re.VERBOSE,
    )

    if match:
        return DurationPreference(
            minimum=parse_days(
                match.group(1),
                match.group(2),
            )
        )
    
    # Maximum    
    match = re.search(
        r"""
        (?:maximum|max|under|below|less\s+than|up\s+to|upto)
        \s*
        (\d+(?:\.\d+)?)
        \s*
        (day|days|week|weeks|month|month|year|years)
        """,
        text,
        re.VERBOSE,
    )

    if match:
        return DurationPreference(
            maximum=parse_days(
                match.group(1),
                match.group(2),
            )
        )

    # ---------------------------------------------------
    # Approximate
    # ---------------------------------------------------

    match = re.search(
        r"""
        (?:around|about|roughly|approximately)?
        \s*
        (\d+(?:\.\d+)?)
        \s*
        (day|days|week|weeks|month|month|year|years)
        """,
        text,
        re.VERBOSE,
    )

    if match:
        return DurationPreference(
            target=parse_days(
                match.group(1),
                match.group(2),
            )
        )

    return None