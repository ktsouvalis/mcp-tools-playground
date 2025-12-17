import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import ollama
from ollama import Client
from dotenv import load_dotenv

# Load environment variables from .env file
BASE = os.path.dirname(os.path.dirname(__file__)) if "__file__" in globals() else os.getcwd()
load_dotenv(dotenv_path=os.path.join(BASE, '.env'), verbose=True)

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL = "llama3.2"
client = Client(host=OLLAMA_URL)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

async def run():
    # 1. Setup the server connection parameters
    server_params = StdioServerParameters(
        command="python",
        args=["local-tools/server.py"],
        env=os.environ.copy(),
    )

    print(f"{Colors.HEADER}--- Starting MCP Client with {MODEL} ---{Colors.ENDC}")

    # 2. Connect to the MCP Server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Prepare tools for Ollama
            tools_list = await session.list_tools()
            ollama_tools = []
            for tool in tools_list.tools:
                ollama_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })

            conversation_history = []

            print(f"{Colors.GREEN}System ready. Type 'quit' to exit.{Colors.ENDC}\n")

            # 3. Start the Chat Loop
            while True:
                user_input = input(f"{Colors.BOLD}You: {Colors.ENDC}")
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break

                # Add user message to history
                conversation_history.append({'role': 'user', 'content': user_input})

                # Call Ollama
                print(f"{Colors.YELLOW}Thinking...{Colors.ENDC}", end="\r")
                response = client.chat(
                    model=MODEL,
                    messages=conversation_history,
                    tools=ollama_tools,
                )

                # Check for tool calls
                if response.get('message', {}).get('tool_calls'):
                    tool_calls = response['message']['tool_calls']

                    # Add the model's intent to call a tool to history
                    conversation_history.append(response['message'])

                    print(f"{Colors.BLUE}➔ Model wants to use tools:{Colors.ENDC}")

                    for tool_call in tool_calls:
                        fn_name = tool_call['function']['name']
                        fn_args = tool_call['function']['arguments']

                        print(f"  Executing {Colors.BOLD}{fn_name}{Colors.ENDC} with {fn_args}...")

                        # Execute tool via MCP
                        try:
                            result = await session.call_tool(fn_name, arguments=fn_args)
                            tool_output = str(result.content)
                        except Exception as e:
                            tool_output = f"Error executing tool: {str(e)}"
                            print(f"{Colors.RED}{tool_output}{Colors.ENDC}")

                        # Add result to history
                        conversation_history.append({
                            'role': 'tool',
                            'content': tool_output,
                        })

                    # Second call to Ollama with the tool data
                    final_response = client.chat(
                        model=MODEL,
                        messages=conversation_history,
                    )

                    answer = final_response['message']['content']
                    conversation_history.append(final_response['message'])

                    print(f"\n{Colors.GREEN}Llama:{Colors.ENDC} {answer}\n")

                else:
                    # No tool needed, just normal chat
                    answer = response['message']['content']
                    conversation_history.append(response['message'])
                    print(f"\n{Colors.GREEN}Llama:{Colors.ENDC} {answer}\n")

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\nGoodbye!")