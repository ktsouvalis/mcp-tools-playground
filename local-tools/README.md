# local-tools (MCP + Ollama)

This sub-project demonstrates a local tool-using LLM loop using **MCP (Model Context Protocol)**:

- An MCP server exposes “real” tools (HTTP website status + Docker inspection).
- A local Llama model (**`llama3.2` via Ollama**) decides when to call those tools.
- The client executes the tool calls through MCP and feeds results back to the model.

## What’s here

- `server.py`: MCP server (FastMCP) exposing tools:
  - `check_website_status(url)`
  - `list_docker_containers()`
  - `get_container_logs(container_name_or_id)`
- `client.py`: Interactive chat client that:
  1) starts the MCP server (stdio)
  2) asks the server for tool schemas
  3) sends your prompts to Ollama with those tools
  4) executes any tool calls via MCP
  5) sends tool outputs back to the model for a final answer

## Prerequisites

- Ollama installed and running
- (Optional) Docker Engine installed/running, and your user can access Docker

## Setup

From the repo root:

```bash
conda activate mcp-tools
pip install -r requirements.txt
```

Make sure your `.env` (repo root) includes:

```ini
OLLAMA_HOST=http://localhost:11434
```

## Run

1) Start Ollama and pull the model:

```bash
ollama serve
# In a second terminal (one-time)
ollama pull llama3.2
```

2) Run the MCP client:

```bash
python local-tools/client.py
```

You should see something like “System ready. Type 'quit' to exit.”

## Example prompts

- Website check:
  - "Check if upatras.gr is reachable"
  - "Is https://uop.gr up?"

- Docker:
  - "List running docker containers"
  - "Show me the logs for container redis"
  - "Do I have any containers exposing port 5432?"

## Notes / troubleshooting

- If Docker tools fail with permissions, ensure:
  - Docker is running
  - your user can access the Docker socket (often membership in the `docker` group)
- If Ollama is remote, set `OLLAMA_HOST` accordingly (e.g. `http://server:11434`).
