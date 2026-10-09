from pydantic import BaseModel, field_serializer, Field
from datetime import datetime

class UpdateTimesheetDTO(BaseModel):
    activity: int | None = Field(default=None, description="New ID of the activity associated with the timesheet")
    project: int | None = Field(default=None, description="New ID of the project associated with the timesheet")
    begin: datetime | None = Field(default=None, description="New start time of the timesheet entry")
    end: datetime | None = Field(default=None, description="New end time of the timesheet entry")
    description: str | None = Field(default=None, description="New description of the timesheet entry")

    @field_serializer("begin", "end")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        return value.strftime("%Y-%m-%dT%H:%M:%S") if value else None
