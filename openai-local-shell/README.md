# openai-local-shell (`local_shell` tool)

This sub-project demonstrates OpenAI’s `local_shell` tool in a safe interactive loop:

- The **model proposes** a shell command.
- The **user confirms** before anything runs.
- The command output is **fed back** to the model.
- The whole session is saved to `logs/` as Markdown when you quit.

## What’s here

- `00_local_shell_client.py`: Interactive client implementing:
  - command confirmation gate (`Execute this command? ([y]/n)`)
  - subprocess execution with optional `cwd`, `env`, timeout
  - Markdown session logging to `logs/session_YYYYMMDD_HHMMSS.md`

## Prerequisites

- OpenAI API key
- A `.env` in the repo root with:

```ini
OPENAI_API_KEY=your_openai_api_key_here
```

## Run

```bash
python openai-local-shell/00_local_shell_client.py
```

Type `quit` / `exit` / `q` to end the session and write the Markdown log.

## Example prompts

- Safe inspection / navigation:
  - "Show disk usage for the current folder"
  - "List running processes and show top 5 by CPU"
  - "Find all `.log` files under `logs/`"

- Git / repo questions:
  - "Show me the last 5 git commits"
  - "Search for the string OPENAI_VECTOR_STORE_ID in the repo"

- Python environment checks:
  - "Show me installed packages"
  - "Run the file-search client and tell me if it errors"

## How the loop works (high level)

1) Your message is appended to a structured conversation history.
2) The client calls `responses.create(...)` with:
   - `tools=[{"type": "local_shell"}]`
3) If the model returns a `local_shell_call` (tool call), the client:
   - prints the proposed command
   - asks for confirmation
   - runs it via `subprocess.run(...)`
   - appends `Command Output:\n...` back into the conversation
4) If the model returns only text, the client prints the final answer.

## Notes

- The script currently uses `model="codex-mini-latest"`. You can change that in `00_local_shell_client.py`.
- Treat this as a demo: always review commands before confirming.
