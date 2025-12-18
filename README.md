# MCP Tools (Local + OpenAI)

This repo contains three small, self-contained “sub-projects” for experimenting with tool-using LLMs:

1. **local-tools/**: MCP server + client wired to **Ollama** (`llama3.2`) and a couple of real tools (HTTP status + Docker).
2. **openai-file-search/**: OpenAI **Vector Stores** + `file_search` tool (upload → index → chat).
3. **openai-local-shell/**: OpenAI `local_shell` tool demo (model proposes shell commands, user confirms, output is fed back).

Each subdirectory has its own README with the detailed workflow and examples.

---

## Prerequisites

- **Conda** (Miniconda/Anaconda)
- **Python 3.12** (installed via conda env below)
- **OpenAI API Key** (for the OpenAI modules)
- **Ollama** (for `local-tools/`)
- **Docker Engine** (optional, only needed for the Docker tools in `local-tools/`)

---

## Setup

### 1) Create a virtual environment (Python 3.12). I prefer conda:

```bash
conda create -n mcp-tools python=3.12 -y
conda activate mcp-tools
```

### 2) Install Python dependencies

From the repo root:

```bash
pip install -r requirements.txt
```

### 3) Configure environment variables

Create a `.env` file in the repo root:

```ini
# Required for OpenAI modules
OPENAI_API_KEY=your_openai_api_key_here

# Used by local-tools (defaults to http://localhost:11434 if unset)
OLLAMA_HOST=http://localhost:11434

# Used by openai-file-search (set after you create/choose a vector store)
OPENAI_VECTOR_STORE_ID=
```

---

## Quick Start

### 1) local-tools (MCP + Ollama)

```bash
python local-tools/client.py
```

See: [local-tools/README.md](local-tools/README.md)

### 2) openai-file-search (Vector Store + file_search)

```bash
python openai-file-search/00_upload_file.py --file path/to/doc.pdf --store my_store
python openai-file-search/01_check_files.py
python openai-file-search/10_file_search_client.py
```

See: [openai-file-search/README.md](openai-file-search/README.md)

### 3) openai-local-shell (local_shell tool)

```bash
python openai-local-shell/00_local_shell_client.py
```

See: [openai-local-shell/README.md](openai-local-shell/README.md)