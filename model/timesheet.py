from pydantic import BaseModel
from datetime import datetime

class Timesheet(BaseModel):
    id: int
    activity: int
    project: int
    begin: datetime
    end: datetime | None = None
    description: str | None = None
