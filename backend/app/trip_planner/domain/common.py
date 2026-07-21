from pydantic import BaseModel, Field
class Coordinates(BaseModel):
    latitude: float = Field(...,ge = -90, le = 90)
    longitude: float = Field(...,ge = -180, le = 180)

class Money(BaseModel):
    amount: float = Field(..., ge = 0)
    currency: str

class CostRange(BaseModel): 
    minimum: Money
    average: Money
    maximum: Money