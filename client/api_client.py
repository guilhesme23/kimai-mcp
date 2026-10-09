import logging
from datetime import datetime
from typing import TypeVar

from httpx import AsyncClient, Response
from model import Project, Activity, Timesheet, Page
from model.dto import CreateTimesheetDTO, UpdateTimesheetDTO
from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class KimaiAPIClient:
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url
        self.api_token = api_token
        self.client = AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_token}"},
        )

    async def get_projects(self, query: str = None) -> list[Project]:
        params = {"term": query} if query else None
        response = await self.client.get("/projects", params=params)
        response.raise_for_status()
        return [Project.model_validate(project) for project in response.json()]

    async def get_project_by_id(self, project_id: int) -> Project:
        response = await self.client.get(f"/projects/{project_id}")
        response.raise_for_status()
        return Project.model_validate(response.json())

    async def get_activities(
        self, project_id: int, query: str = None
    ) -> list[Activity]:
        params = {"term": query} if query else {}
        params["project"] = project_id
        params["visible"] = 1  # Ensure only visible activities are returned

        response = await self.client.get("/activities", params=params)
        response.raise_for_status()
        return [Activity.model_validate(activity) for activity in response.json()]

    async def get_timesheets(
        self, begin: datetime, end: datetime, page: int = 1, size: int = 50
    ) -> Page[Timesheet]:
        params = {
            "begin": begin.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": end.strftime("%Y-%m-%dT%H:%M:%S"),
            "page": page,
            "size": size,
        }

        logger.debug("Fetching timesheets with params: %s", params)
        response = await self.client.get("/timesheets", params=params)
        response.raise_for_status()
        return self._to_page(response, Timesheet)

    async def get_timesheet_by_id(self, timesheet_id: int) -> Timesheet:
        response = await self.client.get(f"/timesheets/{timesheet_id}")
        response.raise_for_status()
        return Timesheet.model_validate(response.json())

    async def create_timesheet(self, timesheet: CreateTimesheetDTO) -> Timesheet:
        json = timesheet.model_dump()
        logger.debug("Creating timesheet with data: %s", json)
        response = await self.client.post(
            "/timesheets",
            json=json,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        response.raise_for_status()
        return Timesheet.model_validate(response.json())

    async def update_timesheet(
        self, timesheet_id: int, timesheet: UpdateTimesheetDTO
    ) -> Timesheet:
        # Only the fields that were provided are sent, so the others keep their current values
        json = timesheet.model_dump(exclude_none=True)
        logger.debug("Updating timesheet %d with data: %s", timesheet_id, json)
        response = await self.client.patch(
            f"/timesheets/{timesheet_id}",
            json=json,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        response.raise_for_status()
        return Timesheet.model_validate(response.json())

    async def delete_timesheet(self, timesheet_id: int) -> None:
        logger.debug("Deleting timesheet %d", timesheet_id)
        response = await self.client.delete(f"/timesheets/{timesheet_id}")
        response.raise_for_status()

    @staticmethod
    def _to_page(response: Response, model: type[T]) -> Page[T]:
        """Builds a Page from a paginated Kimai response, reading the X-* pagination headers."""

        def header(name: str) -> int:
            value = response.headers.get(name)
            if value is None:
                raise ValueError(f"Kimai response is missing the pagination header '{name}'")
            return int(value)

        page = header("X-Page")
        total_pages = header("X-Total-Pages")
        result = Page[model](
            items=[model.model_validate(item) for item in response.json()],
            page=page,
            size=header("X-Per-Page"),
            total_items=header("X-Total-Count"),
            total_pages=total_pages,
            remaining_pages=max(total_pages - page, 0),
            has_next_page=page < total_pages,
        )
        logger.debug(
            "Fetched page %d/%d (%d of %d items)",
            result.page,
            result.total_pages,
            len(result.items),
            result.total_items,
        )
        return result

    async def close(self):
        await self.client.aclose()
