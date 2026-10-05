from mcp.server import MCPServer
from model.project import Project
from settings import Settings
from client import KimaiAPIClient

def register_project_tools(server: MCPServer, settings: Settings):
    api = KimaiAPIClient(settings.kimai_base_url, settings.kimai_api_key)

    @server.tool()
    async def list_projects(query: str = None) -> list[Project]:
        """
        Lista todos os projetos visíveis no Kimai para o usuário atual. Se o parâmetro 'query' for fornecido, filtra os projetos pelo nome.
        
        Params:
            query (str, optional): Uma string para filtrar os projetos pelo nome. Se None, retorna todos os projetos.
        Returns:
            list[Project]: Uma lista de objetos Project representando os projetos encontrados.
        """
        projects = await api.get_projects(query=query)
        return projects