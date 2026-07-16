from app.conversation.state import ConversationState
from app.conversation.profile_updater import update_profile
from app.conversation.question_generator import (
    generate_opening_question,
    generate_next_question
)


def start_conversation():

    state = ConversationState()
    opening = generate_opening_question()

    state.messages.append(
        {
            "role": "assistant",
            "content": opening.question
        }
    )

    return state



def process_message(
    state: ConversationState,
    message: str
):

    state.messages.append(
        {
            "role":"user",
            "content":message
        }
    )


    state.profile = update_profile(
        state.profile,
        message
    )


    next_question = generate_next_question(
        state.profile,
        history=state.messages
    )


    state.messages.append(
        {
            "role":"assistant",
            "content":next_question.question
        }
    )


    if next_question.type == "complete":
        state.is_complete = True


    return state