from pydantic import BaseModel, Field

class Activity(BaseModel):
    id: int = Field(description="ID of the activity")
    project: int = Field(description="ID of the project associated with the activity")
    name: str = Field(description="Name of the activity")