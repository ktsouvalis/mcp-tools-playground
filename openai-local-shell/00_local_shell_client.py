"""
Docstring for openai-local-shell.00_local_shell_client
Module that provides a client interface for interacting with the OpenAI Local Shell service.
"""

import os, sys
import shlex
import subprocess
from openai import OpenAI
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from helpers import Colors

# Load environment variables from .env file
BASE = os.path.dirname(os.path.dirname(__file__)) if "__file__" in globals() else os.getcwd()
load_dotenv(dotenv_path=os.path.join(BASE, '.env'), verbose=True)
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# --- SYSTEM PROMPT ---
SYSTEM_MESSAGE = {
    "role": "user",
    "content": [{
        "type": "input_text",
        "text": "You are a helpful IT and Software Development assistant. "
                "When you execute a shell command, always provide a brief explanation of what you did. "
                "Do not perform Git operations unless specifically asked. "
                "Always respond with text after completing a tool call."
    }]
}

conversation_history = [SYSTEM_MESSAGE]

while True:
    print(f"{Colors.GREEN}System ready. Type 'quit' to exit.{Colors.ENDC}\n")
    user_input = input(f"{Colors.BOLD}You: {Colors.ENDC}")

    if user_input.lower() in ['quit', 'exit', 'q']:
        sys.exit(0)

    conversation_history.append({
        "role": "user",
        "content": [{"type": "input_text", "text": user_input}],
    })

    response = client.responses.create(
        model="codex-mini-latest",
        tools=[{"type": "local_shell"}],
        input=conversation_history,
    )

    while True:
        # Filter and convert Assistant output for history storage
        history_content = []
        for item in response.output:
            if item.type == "text":
                history_content.append({"type": "output_text", "text": item.text})
            elif item.type in ["local_shell_call", "tool_call"]:
                args = getattr(item, "action", None) or getattr(item, "arguments", None)
                cmd = args.get('command') if isinstance(args, dict) else getattr(args, 'command', 'unknown')
                history_content.append({"type": "output_text", "text": f"[System Action: Executed {cmd}]"})

        if history_content:
            conversation_history.append({
                "role": "assistant",
                "content": history_content
            })

        # Process shell calls
        shell_calls = [i for i in response.output if i.type in ["local_shell_call", "tool_call"]]

        if not shell_calls:
            break

        call = shell_calls[0]
        args = getattr(call, "action", None) or getattr(call, "arguments", None)

        def _get(obj, key, default=None):
            if isinstance(obj, dict): return obj.get(key, default)
            return getattr(obj, key, default)

        command = _get(args, "command")
        if not command: break

        print(f"{Colors.YELLOW}Executing command:{Colors.ENDC} {command}")

        if isinstance(command, str): command = shlex.split(command)

        completed = subprocess.run(
            command,
            cwd=_get(args, "working_directory") or os.getcwd(),
            env={**os.environ, **(_get(args, "env") or {})},
            capture_output=True,
            text=True,
            timeout=(_get(args, "timeout_ms") / 1000) if _get(args, "timeout_ms") else None,
        )

        tool_output_text = f"Command Output:\n{completed.stdout + completed.stderr}"
        conversation_history.append({
            "role": "user",
            "content": [{"type": "input_text", "text": tool_output_text}],
        })

        response = client.responses.create(
            model="codex-mini-latest",
            tools=[{"type": "local_shell"}],
            input=conversation_history,
        )

    final_text = response.output_text if response.output_text else "(Command finished successfully)"
    print(f"\n{Colors.GREEN}Model:{Colors.ENDC} {final_text}\n")
