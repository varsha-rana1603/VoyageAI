from fastapi import APIRouter

from app.explore.service import get_destination_explore


router = APIRouter(
    prefix="/explore",
    tags=["Explore"]
)


@router.post("/{destination_name}")
def explore_destination(
    destination_name: str,
    request: dict
):

    return get_destination_explore(

        destination_name,

        request["lat"],
        request["lon"],

        request["travel_style"],
        request["budget"],
        request["crowd_tolerance"],
        request["terrain"],
        request["free_text"]

    )