from fastapi import APIRouter, HTTPException
from app.nearby.nearby_service import get_nearby_places

router= APIRouter(
    prefix="/nearby",
    tags=["Nearby"]
)

@router.get("/")
def nearby_places(
    lat: float,
    lon: float,
    category: str
):
    try:
        return get_nearby_places(lat,lon,category)
    
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )