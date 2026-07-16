from typing import Literal

from pydantic import BaseModel


class Question(BaseModel):
    type: Literal[
        "text",
        "mcq",
        "multi_select",
        "complete",
    ]

    field: str | None = None

    question: str

    options: list[str] = []