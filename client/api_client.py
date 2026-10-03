from httpx import AsyncClient
from model import Project
from model.activity import Activity

class KimaiAPIClient:
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url
        self.api_token = api_token
        self.client = AsyncClient(base_url=self.base_url, headers={"Authorization": f"Bearer {self.api_token}"})

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

    async def close(self):
        await self.client.aclose()
