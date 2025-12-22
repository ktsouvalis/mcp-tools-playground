"""
Docstring for openai-local-shell.00_local_shell_client
Module that provides a client interface for interacting with the OpenAI Local Shell service.
"""

import os, sys, shlex, subprocess
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from helpers import Colors

# Environment Setup
BASE = os.path.dirname(os.path.dirname(__file__)) if "__file__" in globals() else os.getcwd()
load_dotenv(dotenv_path=os.path.join(BASE, '.env'), verbose=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- LOGGING UTILITY ---

def save_as_markdown(history):
    """Saves the conversation as a readable Markdown file with code blocks."""
    log_dir = os.path.join(BASE, "logs")
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(log_dir, f"session_{timestamp}.md")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# Session Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        for msg in history:
            role = msg['role'].upper()
            f.write(f"### {role}\n")
            for item in msg['content']:
                text = item.get('text', str(item))
                # If it's shell output or action, wrap it in a code block
                if "Command Output:" in text or "[System Action:" in text:
                    f.write(f"```bash\n{text}\n```\n")
                else:
                    f.write(f"{text}\n")
            f.write("\n---\n")

    print(f"\n{Colors.BLUE}History saved to: {filepath}{Colors.ENDC}")

def save_as_json(history):
    """Saves the conversation history as a JSON file."""
    import json
    log_dir = os.path.join(BASE, "logs")
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(log_dir, f"session_{timestamp}.json")

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=4)

    print(f"\n{Colors.BLUE}History saved to: {filepath}{Colors.ENDC}")
# --- FUNCTIONAL CORE ---

def execute_shell_command(call):
    """Handles the subprocess execution with a user confirmation step."""
    args = getattr(call, "action", None) or getattr(call, "arguments", None)

    def _get(obj, key, default=None):
        return obj.get(key, default) if isinstance(obj, dict) else getattr(obj, key, default)

    command = _get(args, "command")
    if not command: return "No command provided."

    # --- CONFIRMATION STEP ---
    print(f"\n{Colors.BOLD}{Colors.YELLOW}MODEL REQUESTS COMMAND:{Colors.ENDC} {command}")
    confirm = input(f"Execute this command? ([y]/n): ").lower()

    if confirm not in ['', 'y']:
        print(f"{Colors.RED}Command aborted by user.{Colors.ENDC}")
        return "User refused to execute this command."

    if isinstance(command, str): command = shlex.split(command)

    try:
        completed = subprocess.run(
            command,
            cwd=_get(args, "working_directory") or os.getcwd(),
            env={**os.environ, **(_get(args, "env") or {})},
            capture_output=True, text=True,
            timeout=(_get(args, "timeout_ms") / 1000) if _get(args, "timeout_ms") else None,
        )
        return completed.stdout + completed.stderr
    except Exception as e:
        return f"Error executing command: {str(e)}"

def filter_assistant_output(response_output):
    """Converts model output to API-safe formats for conversation history."""
    history_items = []
    for item in response_output:
        if item.type == "text":
            history_items.append({"type": "output_text", "text": item.text})
        elif item.type in ["local_shell_call", "tool_call"]:
            args = getattr(item, "action", None) or getattr(item, "arguments", None)
            cmd = args.get('command') if isinstance(args, dict) else getattr(args, 'command', 'unknown')
            history_items.append({"type": "output_text", "text": f"[System Action: Executed {cmd}]"})
    return history_items

# --- MAIN LOOP ---

def main():
    # Initial instruction set
    conversation_history = [{
        "role": "user",
        "content": [{"type": "input_text", "text": "Helpful IT assistant. Always explain your shell actions."}]
    }]

    while True:
        print(f"{Colors.GREEN}System ready. Type 'quit' to exit.{Colors.ENDC}")
        user_input = input(f"{Colors.BOLD}You: {Colors.ENDC}")

        if user_input.lower() in ['quit', 'exit', 'q']:
            save_as_markdown(conversation_history)
            save_as_json(conversation_history)
            sys.exit(0)

        conversation_history.append({
            "role": "user",
            "content": [{"type": "input_text", "text": user_input}],
        })

        while True:
            response = client.responses.create(
                model="codex-mini-latest",
                tools=[{"type": "local_shell"}],
                input=conversation_history,
            )

            # Store assistant thought/text
            assistant_items = filter_assistant_output(response.output)
            if assistant_items:
                conversation_history.append({"role": "assistant", "content": assistant_items})

            # Check for shell execution
            shell_calls = [i for i in response.output if i.type in ["local_shell_call", "tool_call"]]
            if not shell_calls:
                # Print final model text and break inner loop
                print(f"\n{Colors.GREEN}Model:{Colors.ENDC} {response.output_text or '(Done)'}\n")
                break

            # Handle execution and return output to history
            result = execute_shell_command(shell_calls[0])
            print(f"\n{Colors.CYAN}Command Output:{Colors.ENDC}\n{result}\n")
            conversation_history.append({
                "role": "user",
                "content": [{"type": "input_text", "text": f"Command Output:\n{result}"}],
            })

if __name__ == "__main__":
    main()