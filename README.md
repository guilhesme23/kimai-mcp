# kimai-mcp

Servidor [MCP](https://modelcontextprotocol.io) para o [Kimai](https://www.kimai.org), o sistema de controle de horas. Ele permite que um agente (como o Claude) consulte projetos e atividades, liste, crie, edite e exclua lançamentos de horas, tudo em linguagem natural.

## Tools disponíveis

| Tool | Parâmetros | O que faz |
|---|---|---|
| `list_projects` | `query` (opcional) | Lista os projetos visíveis ao usuário, com filtro opcional pelo nome. |
| `list_activities` | `project_id`, `query` (opcional) | Lista as atividades visíveis de um projeto, com filtro opcional pelo nome. |
| `list_timesheets` | `begin`, `end`, `page` (padrão 1), `size` (padrão 50) | Lista os lançamentos de horas dentro de um intervalo de datas, paginados. Devolve `items` e os metadados `page`, `size`, `total_items`, `total_pages`, `remaining_pages` e `has_next_page`. |
| `get_timesheet` | `timesheet_id` | Busca um único lançamento de horas pelo ID. |
| `create_timesheet` | `timesheet`: `activity`, `project`, `begin`, `end`, `description` | Cria um lançamento de horas e devolve o registro criado. |
| `update_timesheet` | `timesheet_id`, `timesheet`: `activity`, `project`, `begin`, `end`, `description` (todos opcionais) | Atualiza um lançamento de horas. Só os campos informados mudam; devolve o registro atualizado. |
| `delete_timesheet` | `timesheet_id` | Exclui um lançamento de horas. A ação é permanente e a tool é marcada como destrutiva, para que o cliente peça confirmação. |

Os horários (`begin`/`end`) são enviados ao Kimai no formato `YYYY-MM-DDThh:mm:ss`, sem informação de fuso. O Kimai os interpreta no fuso horário configurado para o usuário.

## Requisitos e instalação

- Python 3.12 ou superior
- [uv](https://docs.astral.sh/uv/)
- Uma instância do Kimai com a API habilitada e um token de API

```bash
git clone <url-do-repositorio> kimai-mcp
cd kimai-mcp
uv sync
```

## Variáveis de ambiente

| Variável | Obrigatória | Descrição | Exemplo |
|---|---|---|---|
| `KIMAI_API_KEY` | Sim | Token de API do Kimai, enviado como `Authorization: Bearer <token>`. Gere-o no perfil do seu usuário no Kimai, na seção de API (o nome exato varia conforme a versão). | `seu-token-aqui` |
| `KIMAI_BASE_URL` | Sim | URL base da API do Kimai, **incluindo** `/api` e sem barra final. | `https://kimai.exemplo.com/api` |

Há duas formas de fornecê-las:

1. **Arquivo `.env`** na raiz do projeto (já está no `.gitignore`):

   ```env
   KIMAI_API_KEY=seu-token-aqui
   KIMAI_BASE_URL=https://kimai.exemplo.com/api
   ```

   O `.env` é lido a partir do **diretório de trabalho** do processo. Por isso os exemplos abaixo iniciam o servidor com `uv --directory <caminho>`, que muda para a pasta do projeto antes de executar.

2. **Variáveis de ambiente do cliente MCP**, definidas na configuração do servidor (veja a seção seguinte). Elas têm precedência sobre o `.env`.

Se alguma das duas estiver ausente, o servidor não inicia e informa qual campo falta.

## Arquitetura

```
kimai-mcp/
├── main.py                  # ponto de entrada: monta o servidor e roda em stdio
├── settings.py              # Settings (pydantic-settings): lê as variáveis de ambiente
├── client/
│   └── api_client.py        # KimaiAPIClient: chamadas HTTP (httpx) à API do Kimai
├── model/                   # models pydantic das respostas da API
│   │                        # (project, activity, customer, timesheet)
│   ├── page.py              # Page[T]: wrapper paginado (itens + total de itens e de páginas)
│   └── dto/                 # payloads de entrada
│       ├── create_timesheet.py  # criação de timesheet
│       └── update_timesheet.py  # atualização parcial de timesheet
└── server/
    ├── __init__.py          # create_server: lifespan e registro das tools
    ├── context.py           # AppContext: o que o lifespan entrega às tools
    └── tools/               # tools MCP: projects.py, activities.py, timesheets.py
```

Fluxo de execução:

1. `main.py` carrega as `Settings` e chama `create_server`.
2. `create_server` cria o `MCPServer` com um **lifespan**. Ao iniciar, o lifespan cria o `KimaiAPIClient` e o entrega dentro de um `AppContext`; ao encerrar, fecha o cliente.
3. Cada tool declara um parâmetro `ctx: Context[AppContext]`, que o SDK injeta (ele não aparece no schema que o agente enxerga), e obtém o cliente com `ctx.request_context.lifespan_context.api`.
4. O `KimaiAPIClient` chama a API do Kimai e converte as respostas nos models de `model/`, que as tools devolvem ao agente. Nos endpoints paginados (hoje, só os timesheets), o client também lê os headers `X-Page`, `X-Per-Page`, `X-Total-Count` e `X-Total-Pages` e devolve um `Page[T]`, para o agente saber o total de itens e quantas páginas faltam.

O servidor usa o transporte **stdio**: o stdout é o canal do protocolo MCP.

### Como adicionar uma tool

1. Adicione o método que chama o endpoint em `client/api_client.py`.
2. Se necessário, crie o model da resposta em `model/` (ou o DTO de entrada em `model/dto/`) e exporte-o no `__init__.py`.
3. Registre a tool em um módulo de `server/tools/`, recebendo `ctx: Context[AppContext]` como primeiro parâmetro. A docstring vira a descrição que o agente lê, então descreva os parâmetros nela (menos o `ctx`).
4. Se criou um módulo novo, chame a função `register_*_tools` em `server/__init__.py`.

Não use `print()` no código do servidor: como o stdout é o canal do protocolo, qualquer texto ali corrompe a comunicação. Use `logging`, que escreve em stderr.

## Usando com um agente

O servidor roda como um subprocesso do cliente MCP. O comando é o mesmo em todos os casos:

```bash
uv --directory /caminho/absoluto/para/kimai-mcp run main.py
```

### Claude Code

Com as credenciais no `.env`:

```bash
claude mcp add kimai -- uv --directory /caminho/absoluto/para/kimai-mcp run main.py
```

Ou passando as credenciais direto na configuração, sem `.env`:

```bash
claude mcp add kimai \
  -e KIMAI_API_KEY=seu-token-aqui \
  -e KIMAI_BASE_URL=https://kimai.exemplo.com/api \
  -- uv --directory /caminho/absoluto/para/kimai-mcp run main.py
```

Por padrão o servidor fica disponível só para você, neste projeto (`--scope local`). Use `-s user` para tê-lo em todos os seus projetos ou `-s project` para compartilhá-lo com a equipe pelo arquivo `.mcp.json`. Com `-s project`, prefira o `.env` à opção `-e`, para o token não ir para o repositório.

Para conferir, rode `claude mcp list` ou use o comando `/mcp` dentro do Claude Code. As tools aparecem com o prefixo `mcp__kimai__`. Depois é só pedir, por exemplo:

- "Quais projetos eu tenho com 'interno' no nome?"
- "Liste meus lançamentos de horas da semana passada."
- "Lance 2 horas hoje, das 14h às 16h, na atividade de desenvolvimento do projeto X."

### Claude Desktop

Edite o arquivo de configuração e adicione o servidor em `mcpServers`:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "kimai": {
      "command": "uv",
      "args": ["--directory", "/caminho/absoluto/para/kimai-mcp", "run", "main.py"],
      "env": {
        "KIMAI_API_KEY": "seu-token-aqui",
        "KIMAI_BASE_URL": "https://kimai.exemplo.com/api"
      }
    }
  }
}
```

Reinicie o Claude Desktop depois de salvar. Se o aplicativo não encontrar o `uv`, troque `"command": "uv"` pelo caminho completo (`which uv` no Linux/macOS, `where uv` no Windows).

### Outros clientes

Qualquer cliente MCP com suporte ao transporte stdio funciona: basta informar o comando acima e, se não usar `.env`, as duas variáveis de ambiente.

## Solução de problemas

| Sintoma | Causa provável |
|---|---|
| O servidor não aparece ou não conecta | Caminho no `--directory` relativo ou errado; `uv` fora do `PATH` do cliente; `.env` ausente ou sem as duas variáveis. |
| A tool falha com erro de autenticação (401/403) | `KIMAI_API_KEY` inválido, expirado ou sem permissão para o recurso. |
| A tool falha com 404 | `KIMAI_BASE_URL` sem o `/api` no final, ou apontando para outro endereço. |
| A tool retorna só `Error executing tool <nome>` | Os erros HTTP do Kimai não são repassados ao agente com detalhes. O motivo aparece no log do servidor (stderr). |
