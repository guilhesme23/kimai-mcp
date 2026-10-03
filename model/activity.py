from pydantic import BaseModel

class Activity(BaseModel):
    id: int
    project: int
    name: str