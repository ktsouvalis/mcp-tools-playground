# """
# Docstring for openai-local-shell.00_local_shell_client
# Module that provides a client interface for interacting with the OpenAI Local Shell service.
# """

# import os, sys, shlex, subprocess
# from datetime import datetime
# import readline
# from openai import OpenAI
# from dotenv import load_dotenv

# readline.parse_and_bind('tab: complete')

# # Add parent directory to path
# sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
# from helpers import Colors

# # Environment Setup
# BASE = os.path.dirname(os.path.dirname(__file__)) if "__file__" in globals() else os.getcwd()
# load_dotenv(dotenv_path=os.path.join(BASE, '.env'), verbose=True)
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# # --- LOGGING UTILITY ---

# def save_as_markdown(history):
#     """Saves the conversation as a readable Markdown file with code blocks."""
#     log_dir = os.path.join(BASE, "logs")
#     os.makedirs(log_dir, exist_ok=True)

#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     filepath = os.path.join(log_dir, f"session_{timestamp}.md")

#     with open(filepath, 'w', encoding='utf-8') as f:
#         f.write(f"# Session Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
#         for msg in history:
#             role = msg['role'].upper()
#             f.write(f"### {role}\n")
#             for item in msg['content']:
#                 text = item.get('text', str(item))
#                 # If it's shell output or action, wrap it in a code block
#                 if "Command Output:" in text or "[System Action:" in text:
#                     f.write(f"```bash\n{text}\n```\n")
#                 else:
#                     f.write(f"{text}\n")
#             f.write("\n---\n")

#     print(f"\n{Colors.BLUE}History saved to: {filepath}{Colors.ENDC}")

# def save_as_json(history):
#     """Saves the conversation history as a JSON file."""
#     import json
#     log_dir = os.path.join(BASE, "logs")
#     os.makedirs(log_dir, exist_ok=True)

#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     filepath = os.path.join(log_dir, f"session_{timestamp}.json")

#     with open(filepath, 'w', encoding='utf-8') as f:
#         json.dump(history, f, indent=4)

#     print(f"\n{Colors.BLUE}History saved to: {filepath}{Colors.ENDC}")
# # --- FUNCTIONAL CORE ---

# def execute_shell_command(call):
#     """Handles the subprocess execution with a user confirmation step."""
#     args = getattr(call, "action", None) or getattr(call, "arguments", None)

#     def _get(obj, key, default=None):
#         return obj.get(key, default) if isinstance(obj, dict) else getattr(obj, key, default)

#     command = _get(args, "command")
#     if not command: return "No command provided."

#     # --- CONFIRMATION STEP ---
#     print(f"\n{Colors.BOLD}{Colors.YELLOW}MODEL REQUESTS COMMAND:{Colors.ENDC} {command}")
#     confirm = input(f"Execute this command? ([y]/n): ").lower()

#     if confirm not in ['', 'y']:
#         print(f"{Colors.RED}Command aborted by user.{Colors.ENDC}")
#         return "User refused to execute this command."

#     if isinstance(command, str): command = shlex.split(command)

#     try:
#         completed = subprocess.run(
#             command,
#             cwd=_get(args, "working_directory") or os.getcwd(),
#             env={**os.environ, **(_get(args, "env") or {})},
#             capture_output=True, text=True,
#             timeout=(_get(args, "timeout_ms") / 1000) if _get(args, "timeout_ms") else None,
#         )
#         return completed.stdout + completed.stderr
#     except Exception as e:
#         return f"Error executing command: {str(e)}"

# def filter_assistant_output(response_output):
#     """Converts model output to API-safe formats for conversation history."""
#     history_items = []
#     for item in response_output:
#         if item.type == "text":
#             history_items.append({"type": "output_text", "text": item.text})
#         elif item.type in ["local_shell_call", "tool_call"]:
#             args = getattr(item, "action", None) or getattr(item, "arguments", None)
#             cmd = args.get('command') if isinstance(args, dict) else getattr(args, 'command', 'unknown')
#             history_items.append({"type": "output_text", "text": f"[System Action: Executed {cmd}]"})
#     return history_items

# # --- MAIN LOOP ---

# def main():
#     # Initial instruction set
#     conversation_history = [{
#         "role": "user",
#         "content": [{"type": "input_text", "text": "Helpful IT assistant. Always explain your shell actions."}]
#     }]

#     while True:
#         print(f"{Colors.GREEN}System ready. Type 'quit' to exit.{Colors.ENDC}")
#         user_input = input(f"{Colors.BOLD}You: {Colors.ENDC}")

#         if user_input.lower() in ['quit', 'exit', 'q']:
#             save_as_markdown(conversation_history)
#             save_as_json(conversation_history)
#             sys.exit(0)

#         conversation_history.append({
#             "role": "user",
#             "content": [{"type": "input_text", "text": user_input}],
#         })

#         while True:
#             response = client.responses.create(
#                 model="codex-mini-latest",
#                 tools=[{"type": "local_shell"}],
#                 input=conversation_history,
#             )

#             # --- TOKEN TRACKING (Updated for Response API) ---
#             if hasattr(response, 'usage') and response.usage:
#                 u = response.usage
#                 # Χρησιμοποιούμε input_tokens και output_tokens αντί για prompt/completion
#                 in_t = getattr(u, 'input_tokens', 0)
#                 out_t = getattr(u, 'output_tokens', 0)
#                 total_t = getattr(u, 'total_tokens', 0)
#                 print(f"{Colors.BLUE}[Tokens: In: {in_t} | Out: {out_t} | Total: {total_t}]{Colors.ENDC}")

#             # Store assistant thought/text
#             assistant_items = filter_assistant_output(response.output)
#             if assistant_items:
#                 conversation_history.append({"role": "assistant", "content": assistant_items})

#             # Check for shell execution
#             shell_calls = [i for i in response.output if i.type in ["local_shell_call", "tool_call"]]
#             if not shell_calls:
#                 # Print final model text and break inner loop
#                 print(f"\n{Colors.GREEN}Model:{Colors.ENDC} {response.output_text or '(Done)'}\n")
#                 break

#             # Handle execution and return output to history
#             result = execute_shell_command(shell_calls[0])
#             print(f"\n{Colors.CYAN}Command Output:{Colors.ENDC}\n{result}\n")
#             conversation_history.append({
#                 "role": "user",
#                 "content": [{"type": "input_text", "text": f"Command Output:\n{result}"}],
#             })

# if __name__ == "__main__":
#     main()

"""
OpenAI Local Shell Client
Module providing an interactive CLI agent that executes shell commands locally
using OpenAI's tool-calling capabilities. Optimized for system administration.
"""

import os, sys, shlex, subprocess, signal, readline
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# --- ORIGINAL ENVIRONMENT SETUP ---
BASE = os.path.dirname(os.path.dirname(__file__)) if "__file__" in globals() else os.getcwd()
load_dotenv(dotenv_path=os.path.join(BASE, '.env'), verbose=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- CONFIGURATION & HISTORY SETUP ---
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".agent_history")

# Add parent directory to path for helpers (Colors, etc.)
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
try:
    from helpers import Colors
except ImportError:
    # Fallback if helpers is not found
    class Colors:
        BLUE = '\033[94m'; GREEN = '\033[92m'; YELLOW = '\033[93m'
        RED = '\033[91m'; BOLD = '\033[1m'; CYAN = '\033[96m'; ENDC = '\033[0m'

def setup_readline():
    """Initializes terminal history and tab-completion features."""
    readline.parse_and_bind('tab: complete')
    if os.path.exists(HISTORY_FILE):
        try:
            readline.read_history_file(HISTORY_FILE)
        except Exception:
            pass
    readline.set_history_length(1000)

def save_history():
    """Persists the current session's command history to the local disk."""
    readline.write_history_file(HISTORY_FILE)

# --- LOGGING UTILITIES ---

def save_as_markdown(history):
    """Exports conversation history to a formatted Markdown file with code blocks."""
    log_dir = os.path.join(BASE, "logs")
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(log_dir, f"session_{timestamp}.md")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# Session Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        for msg in history:
            role = msg['role'].upper()
            f.write(f"### {role}\n")
            content = msg.get('content', [])
            for item in content:
                text = item.get('text', str(item))
                if "Command Output:" in text or "[System Action:" in text:
                    f.write(f"```bash\n{text}\n```\n")
                else:
                    f.write(f"{text}\n")
            f.write("\n---\n")

    print(f"\n{Colors.BLUE}Markdown log saved to: {filepath}{Colors.ENDC}")

# --- FUNCTIONAL CORE ---

def execute_shell_command(call):
    """
    Handles local subprocess execution with real-time streaming.
    Resolves list-formatting and login-shell latency issues.
    """
    args = getattr(call, "action", None) or getattr(call, "arguments", None)

    def _get(obj, key, default=None):
        return obj.get(key, default) if isinstance(obj, dict) else getattr(obj, key, default)

    command_raw = _get(args, "command")
    if not command_raw:
        return "No command provided."

    # 1. FIX: Handle if the model sends a Python List instead of a String
    if isinstance(command_raw, list):
        # Join list items into a single string for shell execution
        command_str = " ".join(command_raw)
    else:
        command_str = str(command_raw)

    # 2. FIX: Clean up 'bash -lc' or literal list strings that cause hangs
    if "bash -lc" in command_str:
        # Strip the shell wrapper to execute the command directly in the current env
        command_str = command_str.replace("bash -lc", "").strip().strip("'").strip('"')

    print(f"\n{Colors.BOLD}{Colors.YELLOW}⚡ EXECUTE:{Colors.ENDC} {Colors.CYAN}{command_str}{Colors.ENDC}")
    confirm = input(f"Confirm? ([y]/n): ").lower()

    if confirm not in ['', 'y']:
        return "User refused execution."

    full_output = []
    try:
        # We pass a String to Popen + shell=True for reliable behavior
        process = subprocess.Popen(
            command_str,
            shell=True,
            cwd=_get(args, "working_directory") or os.getcwd(),
            env={**os.environ, **(_get(args, "env") or {})},
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        print(f"{Colors.BLUE}--- Output Start ---{Colors.ENDC}")

        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                print(line, end="", flush=True) # Flush ensures instant terminal update
                full_output.append(line)

        process.stdout.close()
        result = "".join(full_output)
        return result if result else "Command finished with no output."

    except KeyboardInterrupt:
        process.terminate()
        process.wait()
        print(f"\n{Colors.RED}⚠ Interrupted.{Colors.ENDC}")
        return "Command interrupted by user."
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        print(f"{Colors.BLUE}--- Output End ---{Colors.ENDC}")

def filter_assistant_output(response_output):
    """Converts model response objects into API-compliant message history formats."""
    history_items = []
    for item in response_output:
        if item.type == "text":
            history_items.append({"type": "output_text", "text": item.text})
        elif item.type in ["local_shell_call", "tool_call"]:
            args = getattr(item, "action", None) or getattr(item, "arguments", None)
            cmd = args.get('command') if isinstance(args, dict) else getattr(args, 'command', 'unknown')
            history_items.append({"type": "output_text", "text": f"[System Action: Local Shell Execution of {cmd}]"})
    return history_items

# --- MAIN CHAT LOOP ---

def main():
    """Orchestrates the conversation loop and OpenAI API interactions."""
    setup_readline()

    conversation_history = [{
        "role": "user",
        "content": [{"type": "input_text", "text": "You are a professional IT System Administrator for the University of Peloponnese. Be concise and accurate. When listing files, always prefer machine-readable flags like 'ls -1' or 'find' from the start to avoid redundant calls."}]
    }]

    while True:
        try:
            print(f"\n{Colors.GREEN}● Status: System Ready{Colors.ENDC}")
            user_input = input(f"{Colors.BOLD}You > {Colors.ENDC}")

            if user_input.lower() in ['quit', 'exit', 'q']:
                save_history()
                save_as_markdown(conversation_history)
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

                if hasattr(response, 'usage') and response.usage:
                    u = response.usage
                    in_t = getattr(u, 'input_tokens', 0)
                    out_t = getattr(u, 'output_tokens', 0)
                    print(f"{Colors.BLUE}[Usage Track - In: {in_t} | Out: {out_t}]{Colors.ENDC}")

                assistant_items = filter_assistant_output(response.output)
                if assistant_items:
                    conversation_history.append({"role": "assistant", "content": assistant_items})

                shell_calls = [i for i in response.output if i.type in ["local_shell_call", "tool_call"]]
                if not shell_calls:
                    print(f"\n{Colors.GREEN}Agent:{Colors.ENDC} {response.output_text or '(Process Finished)'}")
                    break

                result = execute_shell_command(shell_calls[0])
                conversation_history.append({
                    "role": "user",
                    "content": [{"type": "input_text", "text": f"Command Output:\n{result}"}],
                })

        except KeyboardInterrupt:
            print("\nSession active. Type 'exit' to close.")
            continue

if __name__ == "__main__":
    main()