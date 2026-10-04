from pydantic import BaseModel, field_serializer, Field
from datetime import datetime

class CreateTimesheetDTO(BaseModel):
    activity: int = Field(description="ID of the activity associated with the timesheet")
    project: int = Field(description="ID of the project associated with the timesheet")
    begin: datetime = Field(description="Start time of the timesheet entry")
    end: datetime = Field(description="End time of the timesheet entry")
    description: str = Field(description="Description of the timesheet entry")

    @field_serializer("begin", "end")
    def serialize_datetime(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%dT%H:%M:%S")