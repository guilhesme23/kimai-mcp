from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from client import KimaiAPIClient
from mcp.server import MCPServer
from settings import Settings

from .context import AppContext
from .tools.projects import register_project_tools
from .tools.activities import register_activities_tools
from .tools.timesheets import register_timesheet_tools

def create_server(server_name: str, settings: Settings) -> MCPServer[AppContext]:
    @asynccontextmanager
    async def lifespan(_: MCPServer[AppContext]) -> AsyncGenerator[AppContext]:
        api = KimaiAPIClient(settings.kimai_base_url, settings.kimai_api_key)
        try:
            yield AppContext(api=api)
        finally:
            await api.close()

    server = MCPServer(server_name, lifespan=lifespan)
    register_project_tools(server)
    register_activities_tools(server)
    register_timesheet_tools(server)
    return server
