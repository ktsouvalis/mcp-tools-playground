
import argparse
import os, sys
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

def create_file(client, file_path):
    """Uploads a file to the OpenAI API and returns the file ID."""
    try:
        with open(file_path, "rb") as file_content:
            result =  client.files.create(
                file=file_content,
                purpose="assistants"
            )
        return result.id
    except Exception as e:
        print(f"{Colors.RED}Error uploading file: {e}{Colors.ENDC}")
        return None

def create_vector_store(client, store_name):
    """Creates a vector store with the given name."""
    try:
        vector_store = client.vector_stores.create(
            name=store_name
        )
        return vector_store.id
    except Exception as e:
        print(f"{Colors.RED}Error creating vector store: {e}{Colors.ENDC}")
        return None

def add_file_to_vector_store(client, vector_store_id, file_id):
    """Adds the uploaded file to the specified vector store."""
    try:
        result = client.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=file_id
        )
        return result
    except Exception as e:
        print(f"{Colors.RED}Error adding file to vector store: {e}{Colors.ENDC}")
        return None

def vector_store_exists(client, store_name):
    """Checks if a vector store with the given name exists."""
    try:
        existing_stores = client.vector_stores.list()
        for store in existing_stores.data:
            if store.name == store_name:
                return True, store.id
        return False, None
    except Exception as e:
        print(f"{Colors.RED}Error checking vector store existence: {e}{Colors.ENDC}")
        return False, None

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Upload a file to OpenAI API")
    ap.add_argument("--file", type=str, help="Path to the file to upload", required=True)
    ap.add_argument("--store", type=str, help="Name of the vector store to create", required=True)

    # Create the file
    args = ap.parse_args()
    file_id = create_file(client, args.file)
    if not file_id:
        print(f"{Colors.RED}File upload failed.{Colors.ENDC}")
        exit(1)

    print(f"{Colors.GREEN}File uploaded successfully. File ID: {file_id}{Colors.ENDC}")

    # Check if the vector store exists
    exists, vector_store_id = vector_store_exists(client, args.store)
    if not exists:
        vector_store_id = create_vector_store(client, args.store)
        if not vector_store_id:
            print(f"{Colors.RED}Vector store creation failed.{Colors.ENDC}")
            exit(1)
        print(f"{Colors.GREEN}Vector store '{args.store}' created with ID: {vector_store_id}{Colors.ENDC}")
    else:
        print(f"{Colors.GREEN}Vector store '{args.store}' already exists with ID: {vector_store_id}{Colors.ENDC}")

    # Add the file to the vector store
    add_result = add_file_to_vector_store(client, vector_store_id, file_id)
    if not add_result:
        print(f"{Colors.RED}Failed to add file to vector store.{Colors.ENDC}")
        exit(1)
    print(f"{Colors.GREEN}File added to vector store successfully.{Colors.ENDC}")

    # Check if the uploaded file is processed by the vector store
    print(f"{Colors.YELLOW}Vector store is processing the file...{Colors.ENDC}")
    while True:
        response = client.vector_stores.files.list(vector_store_id=vector_store_id)
        files = response.data or []
        statuses = [f.status for f in files if f.id == file_id]

        if any(s == "failed" for s in statuses):
            print(f"{Colors.RED}File processing in vector store failed.{Colors.ENDC}")
            exit(1)
        if any(s == "completed" for s in statuses):
            break

    print(f"{Colors.GREEN}File processed into vector store successfully.{Colors.ENDC}")

    print(f"{Colors.GREEN}File processed into vector store successfully.{Colors.ENDC}")
    print(f"{Colors.GREEN}All operations completed successfully.{Colors.ENDC}")
    print(f"{Colors.GREEN}You can continue with 10_client.py to interact with the vector store.{Colors.ENDC}")



