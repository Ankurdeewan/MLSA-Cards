from pydantic import BaseModel

class ProblemSchema(BaseModel):
    id: int
    question: str
    points: int
    category: str
    difficulty: str

class HealthResponse(BaseModel):
    status: str