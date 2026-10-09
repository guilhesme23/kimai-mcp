from datetime import datetime

from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from mcp.types import ToolAnnotations
from model import Page, Timesheet
from model.dto import CreateTimesheetDTO, UpdateTimesheetDTO

from ..context import AppContext

def register_timesheet_tools(server: MCPServer[AppContext]):
    @server.tool()
    async def list_timesheets(
        ctx: Context[AppContext],
        begin: datetime,
        end: datetime,
        page: int = 1,
        size: int = 50,
    ) -> Page[Timesheet]:
        """
        Lista as entradas de timesheet no Kimai dentro do intervalo de datas especificado, de forma paginada.

        Params:
            begin (datetime): A data e hora de início do intervalo.
            end (datetime): A data e hora de término do intervalo.
            page (int, optional): O número da página para paginação, começando em 1. Padrão é 1.
            size (int, optional): O número de entradas por página. Padrão é 50.
        Returns:
            Page[Timesheet]: A página pedida, com os campos:
                - items: as entradas (Timesheet) da página atual.
                - page: o número da página atual.
                - size: o número máximo de entradas por página.
                - total_items: o total de entradas do intervalo, somando todas as páginas.
                - total_pages: o total de páginas do intervalo.
                - remaining_pages: quantas páginas ainda faltam depois da atual.
                - has_next_page: se existe uma página depois da atual.
            Para obter todas as entradas, repita a chamada com page + 1 enquanto has_next_page for verdadeiro.
            Não peça páginas acima de total_pages: o Kimai responde com erro.
        """
        api = ctx.request_context.lifespan_context.api
        timesheets = await api.get_timesheets(begin=begin, end=end, page=page, size=size)
        return timesheets

    @server.tool()
    async def get_timesheet(ctx: Context[AppContext], timesheet_id: int) -> Timesheet:
        """
        Busca uma única entrada de timesheet no Kimai pelo ID.

        Params:
            timesheet_id (int): O ID da entrada de timesheet.
        Returns:
            Timesheet: O objeto Timesheet correspondente ao ID informado.
        """
        api = ctx.request_context.lifespan_context.api
        timesheet = await api.get_timesheet_by_id(timesheet_id)
        return timesheet

    @server.tool()
    async def create_timesheet(
        ctx: Context[AppContext], timesheet: CreateTimesheetDTO
    ) -> Timesheet:
        """
        Cria uma nova entrada de timesheet no Kimai.

        Params:
            timesheet (CreateTimesheetDTO): Um objeto CreateTimesheetDTO contendo os detalhes da entrada a ser criada.
        Returns:
            Timesheet: O objeto Timesheet criado, incluindo o ID gerado pelo Kimai.
        """
        api = ctx.request_context.lifespan_context.api
        created_timesheet = await api.create_timesheet(timesheet)
        return created_timesheet

    @server.tool()
    async def update_timesheet(
        ctx: Context[AppContext], timesheet_id: int, timesheet: UpdateTimesheetDTO
    ) -> Timesheet:
        """
        Atualiza uma entrada de timesheet existente no Kimai. Apenas os campos informados são alterados; os demais mantêm o valor atual.

        Params:
            timesheet_id (int): O ID da entrada de timesheet a ser atualizada.
            timesheet (UpdateTimesheetDTO): Um objeto UpdateTimesheetDTO com os campos a alterar (activity, project, begin, end, description). Omita os campos que não devem mudar.
        Returns:
            Timesheet: O objeto Timesheet atualizado.
        """
        api = ctx.request_context.lifespan_context.api
        updated_timesheet = await api.update_timesheet(timesheet_id, timesheet)
        return updated_timesheet

    @server.tool(annotations=ToolAnnotations(destructive_hint=True))
    async def delete_timesheet(ctx: Context[AppContext], timesheet_id: int) -> str:
        """
        Exclui permanentemente uma entrada de timesheet do Kimai. A ação não pode ser desfeita; confirme com o usuário antes de excluir.

        Params:
            timesheet_id (int): O ID da entrada de timesheet a ser excluída.
        Returns:
            str: Uma mensagem confirmando a exclusão.
        """
        api = ctx.request_context.lifespan_context.api
        await api.delete_timesheet(timesheet_id)
        return f"Timesheet {timesheet_id} excluído com sucesso."
