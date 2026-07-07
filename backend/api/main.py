from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.semantic_search import get_recommendations

app = FastAPI()

# Allow requests from your Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserRequest(BaseModel):
    travel_style: str
    budget: str
    crowd_tolerance: str
    terrain: str
    free_text: str


@app.post("/recommend")
def recommend(request: UserRequest):
    return get_recommendations(
        travel_style=request.travel_style,
        budget=request.budget,
        crowd_tolerance=request.crowd_tolerance,
        terrain=request.terrain,
        free_text=request.free_text,
    )