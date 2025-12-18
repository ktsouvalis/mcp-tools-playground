# openai-file-search (Vector Stores + `file_search`)

This sub-project is a minimal “upload → index → chat” flow using OpenAI **Vector Stores** and the `file_search` tool.

## What’s here

- `00_upload_file.py`
  - Uploads a file to OpenAI
  - Creates (or reuses) a vector store by name
  - Adds the uploaded file to the vector store
  - Polls until processing completes

- `01_check_files.py`
  - Verifies a vector store and lists files + their processing status

- `10_file_search_client.py`
  - Simple interactive chat loop
  - Uses `client.responses.create(...)` with the `file_search` tool bound to your vector store
  - Prints answer + any detected source filenames (when provided by annotations)

## Prerequisites

- OpenAI API key
- A `.env` in the repo root with:

```ini
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_VECTOR_STORE_ID=
```

> `OPENAI_VECTOR_STORE_ID` is required for `01_check_files.py` and `10_file_search_client.py`.

## Workflow

### 1) Upload a file and create/reuse a vector store

```bash
python openai-file-search/00_upload_file.py \
  --file path/to/document.pdf \
  --store my_store
```

This prints a vector store ID when the store is created or reused.

Important: copy the vector store ID into the repo root `.env`:

```ini
OPENAI_VECTOR_STORE_ID=vs_...
```

### 2) Check that files are processed

```bash
python openai-file-search/01_check_files.py
```

You’ll see:
- store name + overall status
- list of files with `completed` / `in_progress` / `failed`

### 3) Chat using `file_search`

```bash
python openai-file-search/10_file_search_client.py
```

Ask questions about the uploaded documents.

## Example questions

- "Summarize the main points of the document"
- "What does it say about deadlines?"
- "List the requirements and where they appear"
- "Quote the paragraph that mentions refunds"

## Notes

- `10_file_search_client.py` currently uses `model="gpt-5-nano"`. You can change it to another model if you prefer.
- If you upload multiple files into the same store, `file_search` can retrieve across all of them.
- If you see no sources, it may mean the response did not include filename annotations for that answer.
