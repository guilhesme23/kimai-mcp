from mcp.server import MCPServer
from settings import Settings

from .tools.projects import register_project_tools
from .tools.activities import register_activities_tools
from .tools.timesheets import register_timesheet_tools

def create_server(server_name: str, settings: Settings) -> MCPServer:
    server = MCPServer(server_name)
    register_project_tools(server, settings)
    register_activities_tools(server, settings)
    register_timesheet_tools(server, settings)
    return server