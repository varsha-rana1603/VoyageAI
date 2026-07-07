from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.destinations.semantic_search import get_recommendations
from app.stay.recommender import get_stay_recommendations

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3002",
        "http://127.0.0.1:3002",
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


class StayRequest(BaseModel):
    destination_name: str
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


@app.post("/recommend-stays")
def recommend_stays(request: StayRequest):
    # TODO: replace with real stay-matching logic (e.g. a places API, or
    # a stays dataset filtered/scored the same way destinations are)
    recommendations = get_stay_recommendations(
        destination_name=request.destination_name, 
        travel_style=request.travel_style,
        budget=request.budget,
        crowd_tolerance=request.crowd_tolerance,
        terrain=request.terrain,
        free_text=request.free_text       
    )
    return recommendations