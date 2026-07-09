from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json
import queue
import threading
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.destinations.semantic_search import get_recommendations
from app.stay.recommender import get_stay_recommendations
from app.nearby.router import router as nearby_router
from app.explore.router import router as explore_router

app = FastAPI()

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

app.include_router(explore_router)


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

@app.post("/recommend-stays-stream")
def recommend_stays_stream(request: StayRequest):

    progress_queue = queue.Queue()


    def progress_callback(data):
        progress_queue.put(data)



    result = {}


    def run_engine():

        result["recommendations"] = get_stay_recommendations(

            destination_name=request.destination_name,

            travel_style=request.travel_style,

            budget=request.budget,

            crowd_tolerance=request.crowd_tolerance,

            terrain=request.terrain,

            free_text=request.free_text,

            progress_callback=progress_callback
        )



    def event_generator():

        thread = threading.Thread(
            target=run_engine
        )

        thread.start()



        while thread.is_alive():

            try:

                update = progress_queue.get(
                    timeout=1
                )


                yield (
                    f"data: {json.dumps(update)}\n\n"
                )


            except queue.Empty:

                pass



        yield (
            f"data: {json.dumps({
                'stage':'complete',
                'progress':100,
                'recommendations':result.get('recommendations', [])
            })}\n\n"
        )



    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )