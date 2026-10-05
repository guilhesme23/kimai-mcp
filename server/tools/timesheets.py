from datetime import datetime

from mcp.server import MCPServer
from model import Timesheet
from model.dto import CreateTimesheetDTO
from settings import Settings
from client import KimaiAPIClient

def register_timesheet_tools(server: MCPServer, settings: Settings):
    api = KimaiAPIClient(settings.kimai_base_url, settings.kimai_api_key)

    @server.tool()
    async def list_timesheets(
        begin: datetime, end: datetime, page: int = 1, size: int = 50
    ) -> list[Timesheet]:
        """
        Lista todas as entradas de timesheet no Kimai dentro do intervalo de datas especificado.

        Params:
            begin (datetime): A data e hora de início do intervalo.
            end (datetime): A data e hora de término do intervalo.
            page (int, optional): O número da página para paginação. Padrão é 1.
            size (int, optional): O número de entradas por página. Padrão é 50.
        Returns:
            list[Timesheet]: Uma lista de objetos Timesheet representando as entradas encontradas.
        """
        timesheets = await api.get_timesheets(begin=begin, end=end, page=page, size=size)
        return timesheets

    @server.tool()
    async def create_timesheet(timesheet: CreateTimesheetDTO) -> Timesheet:
        """
        Cria uma nova entrada de timesheet no Kimai.

        Params:
            timesheet (CreateTimesheetDTO): Um objeto CreateTimesheetDTO contendo os detalhes da entrada a ser criada.
        Returns:
            Timesheet: O objeto Timesheet criado, incluindo o ID gerado pelo Kimai.
        """
        created_timesheet = await api.create_timesheet(timesheet)
        return created_timesheet
