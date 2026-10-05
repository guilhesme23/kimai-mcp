from settings import Settings
from server import create_server

server = create_server(
    server_name="kimai-mcp",
    settings=Settings()
)

if __name__ == "__main__":
    server.run()