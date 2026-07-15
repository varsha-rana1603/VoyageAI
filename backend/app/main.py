from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import budget, destinations, profile

app = FastAPI(title="VoyageAI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile.router)
app.include_router(destinations.router)
app.include_router(budget.router)


@app.get("/health")
def health():
    return {"status": "ok"}
