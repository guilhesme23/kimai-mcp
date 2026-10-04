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

async def list_activities():
    project_id = 1
    activities = await api.get_activities(project_id=project_id)

    for activity in activities:
        print(f"Activity ID: {activity.id}, Name: {activity.name}")

    await api.close()

async def list_projects():
    projects = await api.get_projects()

    for project in projects:
        print(f"Project ID: {project.id}, Name: {project.name}")

    await api.close()

async def search_timesheets():
    from datetime import datetime, timedelta

    # Define the time range for the search
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)  # Last 7 days

    timesheets = await api.get_timesheets(begin=start_time, end=end_time)

    for timesheet in timesheets:
        print(f"Timesheet ID: {timesheet.id}, Activity ID: {timesheet.activity}, Project ID: {timesheet.project}, Begin: {timesheet.begin}, End: {timesheet.end}, Description: {timesheet.description}")

async def create_timesheet():
    from datetime import datetime, timedelta
    from model.dto import CreateTimesheetDTO

    # Define the timesheet data
    timesheet_data = CreateTimesheetDTO(
        activity=3,  # Replace with a valid activity ID
        project=1,   # Replace with a valid project ID
        begin=datetime.now() - timedelta(hours=1, days=1),  # 1 hour ago
        end=datetime.now() - timedelta(days=1),  # Now
        description="Exemplo de timesheet criado via API"
    )

    try:
        created_timesheet = await api.create_timesheet(timesheet_data)
        print(f"Timesheet created successfully: {created_timesheet}")
    except Exception as e:
        print(f"Error creating timesheet: {e}")

import asyncio

asyncio.run(search_timesheets())