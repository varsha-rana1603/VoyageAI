from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Travel recommender API is alive"}