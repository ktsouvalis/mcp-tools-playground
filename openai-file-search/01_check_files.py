import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from helpers import Colors

# Load environment variables from .env file
BASE = os.path.dirname(os.path.dirname(__file__)) if "__file__" in globals() else os.getcwd()
load_dotenv(dotenv_path=os.path.join(BASE, '.env'), verbose=True)
api_key = os.getenv("OPENAI_API_KEY")
client=OpenAI(api_key=api_key)
VECTOR_STORE_ID = os.getenv("OPENAI_VECTOR_STORE_ID")

def check_vector_store():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print(f"{Colors.RED}Error: OPENAI_API_KEY not found in .env{Colors.ENDC}")
        return

    client = OpenAI(api_key=api_key)

    print(f"{Colors.HEADER}--- Checking Vector Store: {VECTOR_STORE_ID} ---{Colors.ENDC}\n")

    try:
        vs = client.vector_stores.retrieve(vector_store_id=VECTOR_STORE_ID)
        print(f"Store Name: {Colors.BOLD}{vs.name}{Colors.ENDC}")
        print(f"Status:     {vs.status}")
        print(f"File Count: {vs.file_counts.total}")
        print("-" * 50)

        vs_files = client.vector_stores.files.list(vector_store_id=VECTOR_STORE_ID)

        found_files = list(vs_files)

        if not found_files:
            print(f"{Colors.YELLOW}No files found in this Vector Store.{Colors.ENDC}")
            return

        print(f"\n{Colors.BLUE}File List:{Colors.ENDC}")
        print(f"{'Filename':<40} | {'Status':<15} | {'Size (Bytes)':<15}")
        print("-" * 75)

        for vs_file in found_files:
            try:
                file_details = client.files.retrieve(vs_file.id)
                filename = file_details.filename
            except Exception:
                filename = "Unknown Filename"

            status_color = Colors.GREEN if vs_file.status == 'completed' else Colors.RED
            if vs_file.status == 'in_progress': status_color = Colors.YELLOW

            print(f"{filename:<40} | {status_color}{vs_file.status:<15}{Colors.ENDC} | {vs_file.usage_bytes}")

            if vs_file.status == 'failed':
                print(f"{Colors.RED}  -> Error: {vs_file.last_error}{Colors.ENDC}")

        print("\n" + "-" * 50)

        if all(f.status == 'completed' for f in found_files):
             print(f"{Colors.GREEN}✔ All files are ready for search.{Colors.ENDC}")
        else:
             print(f"{Colors.RED}✘ Some files are not ready or failed.{Colors.ENDC}")

    except Exception as e:
        print(f"{Colors.RED}Critical Error: {e}{Colors.ENDC}")

if __name__ == "__main__":
    check_vector_store()