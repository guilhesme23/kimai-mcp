from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from model.project import Project

from ..context import AppContext

def register_project_tools(server: MCPServer[AppContext]):
    @server.tool()
    async def list_projects(ctx: Context[AppContext], query: str = None) -> list[Project]:
        """
        Lista todos os projetos visíveis no Kimai para o usuário atual. Se o parâmetro 'query' for fornecido, filtra os projetos pelo nome.
        
        Params:
            query (str, optional): Uma string para filtrar os projetos pelo nome. Se None, retorna todos os projetos.
        Returns:
            list[Project]: Uma lista de objetos Project representando os projetos encontrados.
        """
        api = ctx.request_context.lifespan_context.api
        projects = await api.get_projects(query=query)
        return projects