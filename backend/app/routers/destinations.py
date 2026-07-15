from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.destination import DestinationRecommendation, RecommendationRequest, RecommendationResponse
from app.services.ranking_service import RankingService

router = APIRouter(prefix="/api/destinations", tags=["destinations"])


@router.post("/recommend", response_model=RecommendationResponse)
def recommend(payload: RecommendationRequest, db: Session = Depends(get_db)):
    service = RankingService(db)
    try:
        results = service.recommendations_for_profile_id(payload.profile_id, payload.limit, user_budget_inr=None)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    recommendations = [
        DestinationRecommendation(
            destination_id=item["destination"].id,
            name=item["destination"].name,
            country=item["destination"].country,
            match_score=item["match_score"],
            estimated_cost_inr=item["estimated_cost_inr"],
            within_budget=item["within_budget"],
            reason=item["reason"],
        )
        for item in results
    ]
    return RecommendationResponse(profile_id=payload.profile_id, recommendations=recommendations)
