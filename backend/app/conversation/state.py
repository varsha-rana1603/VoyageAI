from pydantic import BaseModel, Field
from typing import List, Dict

from .user_profile import UserProfile


class ConversationState(BaseModel):

    profile: UserProfile = Field(
        default_factory=UserProfile
    )

    messages: List[Dict] = Field(default_factory=list)

    is_complete: bool = False