# MCP SysAdmin & OpenAI Vector Search Tools

This repository contains two distinct experimental modules for interacting with LLMs:

1.  **Local SysAdmin Dashboard (MCP + Ollama):** A local implementation using the Model Context Protocol (MCP) to connect a local Llama 3.2 model (via Ollama) to system tools like Docker and HTTP checks.
2.  **OpenAI Vector Store (File Search):** A set of scripts to upload files, manage OpenAI Vector Stores, and perform RAG (Retrieval-Augmented Generation) using OpenAI's `file_search` tool.

---

## 📋 Prerequisites

Before running these scripts, ensure you have the following installed:

* **Python 3.10+**
* **Docker Engine** (running and accessible by the user)
* **Ollama** (for local model interaction)
* **OpenAI API Key**

---

## 🛠️ Installation & Setup

### 1. Directory Structure
The `client.py` script expects a specific folder structure for the MCP server. Ensure your project looks like this:

```text
project_root/
├── README.md
├── .env.example            # Template for environment variables
├── requirements.txt
├── helpers.py
├── .gitignore
└── local-tools/
    └── server.py
    └── client.py
└── openai-file-search/
    └── 00_upload_file.py
    └── 01_check_files.py
    └── 10_client.py
```

### 2. Environment Variables
Create a `.env` file in the root directory (using `.env.example` as a template):

```ini
OPENAI_API_KEY=your_openai_api_key_here
OLLAMA_HOST=http://localhost:11434
# The ID below will be generated automatically by 00_upload_file.py
# Paste it here after running that script or paste it in case you use a pre-existing vector store
OPENAI_VECTOR_STORE_ID=
```

### 3. Install Dependencies
Install the requirements (virtual environment recommended, i use conda):

```bash
conda create -n mcp python=3.14.2 -y
conda activate mcp
# Install packages
pip install -r requirements.txt
```

---

## 🚀 Module 1: Local SysAdmin Dashboard (MCP)

This module connects a local Llama 3.2 model to your system's tools using the Model Context Protocol.

### 1. Prepare Ollama
Ensure Ollama is running and you have pulled the required model:

```bash
ollama serve
# Open a new terminal
ollama pull llama3.2
```

### 2. Run the Client
This script starts the MCP server (subprocess) and the interactive client.

```bash
python client.py
```

### 3. Usage Examples
Once the system says `System ready`, you can ask questions like:
* "Check if upatras.gr is down."
* "List my running docker containers."
* "Show me the logs for the container named 'redis'."

---

## 📂 Module 2: OpenAI Vector Search

This module uses OpenAI's Assistants API `file_search` tool (RAG).

### Step 1: Upload File & Create Vector Store
Run this script to upload a file. It will create a vector store or it will use an existing one and link the file.

```bash
python 00_upload_file.py --file path/to/your/document.pdf --store your_vector_store_name
```
* **Output:** It will print a **Vector Store ID**.
* **Action:** Copy this ID and paste it into your `.env` file as `OPENAI_VECTOR_STORE_ID`.
OR
* If you already have a vector store, just paste its ID into the `.env` file.

### Step 2: Check Processing Status
Verify that the file has been successfully processed and indexed by OpenAI.

```bash
python 01_check_files.py
```

### Step 3: Chat with your Data
Start the chat client. It uses the model defined in the script (e.g., `gpt-5-nano` or `gpt-4o`) to answer questions based on the uploaded file.

```bash
python 10_client.py
```