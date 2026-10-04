from pydantic import BaseModel, Field

class Project(BaseModel):
    id: int = Field(description="ID of the project")
    name: str = Field(description="Name of the project")