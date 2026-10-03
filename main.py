from mcp.server import MCPServer

# server = MCPServer("Kimai MCP Server")

# @server.tool()
# async def create_project(project_name: str) -> str:
#     return f"Projeto criado: {project_name}"

# @server.resource("projects://{project_id}")
# def get_project_with_id(project_id: str) -> str:
#     return f"Retorno do projeto com ID: {project_id}"

import os

from dotenv import load_dotenv
from client import KimaiAPIClient

load_dotenv()

KIMAI_API_KEY = os.getenv("KIMAI_API_KEY")
KIMAI_BASE_URL = os.getenv("KIMAI_BASE_URL")

api = KimaiAPIClient(base_url=KIMAI_BASE_URL, api_token=KIMAI_API_KEY)

async def main():
    project_id = 147
    activities = await api.get_activities(project_id=project_id)

    for activity in activities:
        print(f"Activity ID: {activity.id}, Name: {activity.name}")

    await api.close()

import asyncio

asyncio.run(main())