from app.conversation.user_profile import UserProfile
from app.clients.bedrock import generate_json
from app.conversation.prompts import build_question_prompt
from app.conversation.models.question import Question
from app.conversation.prompts import (
    build_opening_prompt,
)
QUESTION_PRIORITY = [
    (
        "budget",
        "total_budget",
    ),
    (
        "duration",
        "duration_days",
    ),
    (
        "month",
        "travel_month",
    ),
    (
        "companions",
        "traveller_count",
    ),
    (
        "travel_style",
        "travel_styles",
    ),
    (
        "crowd_preference",
        "crowd_preference",
    ),
    (
        "accommodation",
        "accommodation_type",
    ),
]

def is_missing(value):
    if value is None:
        return True
    if isinstance(value,list):
        return len(value) == 0
    return False

def get_missing_fields(
    profile: UserProfile,
) -> list[str]:

    missing = []

    for logical_name, profile_field in QUESTION_PRIORITY:

        value = getattr(
            profile,
            profile_field,
        )

        if is_missing(value):
            missing.append(logical_name)

    return missing

def generate_opening_question() -> Question:

    prompt = build_opening_prompt()

    response = generate_json(prompt)

    return Question.model_validate(response)

def generate_next_question(
    profile: UserProfile,
    history: list[dict],
) -> Question:

    missing_fields = get_missing_fields(
        profile
    )

    if not missing_fields:

        return Question(
            type="complete",
            question=(
                "Perfect! I have everything I need "
                "to recommend destinations."
            ),
        )

    next_field = missing_fields[0]

    prompt = build_question_prompt(
        profile=profile,
        history=history,
        missing_fields=missing_fields,
        next_field=next_field,
    )

    response = generate_json(prompt)

    return Question.model_validate(response)