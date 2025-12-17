from openai import OpenAI
import os, sys
from dotenv import load_dotenv
# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from helpers import Colors

# Load environment variables from .env file
BASE = os.path.dirname(os.path.dirname(__file__)) if "__file__" in globals() else os.getcwd()
load_dotenv(dotenv_path=os.path.join(BASE, '.env'), verbose=True)
api_key = os.getenv("OPENAI_API_KEY")
vector_store_id = os.getenv("OPENAI_VECTOR_STORE_ID")
client=OpenAI(api_key=api_key)

def speak():

    print(f"{Colors.GREEN}System ready. Type 'quit' to exit.{Colors.ENDC}\n")
    history=[]
    while True:
        user_input = input(f"{Colors.BOLD}You: {Colors.ENDC}")
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        history.append({"role": "user", "content": user_input})
        # Call model
        print(f"{Colors.YELLOW}Thinking...{Colors.ENDC}", end="\r")
        response = client.responses.create(
            model="gpt-5-nano",
            input=user_input,
            tools=[{
                "type": "file_search",
                "vector_store_ids": [vector_store_id]
            }]
        )

        answer = "No text response found."
        sources = []

        for item in response.output:
            if item.type == 'message':
                for content_part in item.content:
                    if content_part.type == 'output_text':
                        answer = content_part.text

                        if content_part.annotations:
                            for annotation in content_part.annotations:
                                src_name = getattr(annotation, 'filename', None)
                                if src_name and src_name not in sources:
                                    sources.append(src_name)

                        if sources:
                            answer += "\n\nSources:\n"
                            for src in sources:
                                answer += f"- {src}\n"

                        history.append({"role": "assistant", "content": answer})
                        break

        print(f"\n{Colors.GREEN}Model:{Colors.ENDC} {answer}\n")

if __name__ == "__main__":
    speak()