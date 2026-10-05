from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from model import Activity

from ..context import AppContext


def register_activities_tools(server: MCPServer[AppContext]):
    @server.tool()
    async def list_activities(
        ctx: Context[AppContext], project_id: int, query: str = None
    ) -> list[Activity]:
        """
        Lista todas as atividades visíveis no Kimai para o usuário atual. Se o parâmetro 'query' for fornecido, filtra as atividades pelo nome.
        
        Params:
            project_id (int): O ID do projeto para o qual listar atividades.
            query (str, optional): Uma string para filtrar as atividades pelo nome. Se None, retorna todas as atividades.
        Returns:
            list[Activity]: Uma lista de objetos Activity representando as atividades encontradas.
        """
        api = ctx.request_context.lifespan_context.api
        activities = await api.get_activities(project_id=project_id, query=query)
        return activities