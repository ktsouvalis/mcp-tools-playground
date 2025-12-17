import time
import docker
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize Server
mcp = FastMCP("sysadmin_dashboard")

# --- TOOL 1: Fast Website Checker ---
@mcp.tool()
async def check_website_status(url: str) -> str:
    """Checks if a website is reachable. Fast timeout (3s).
    
    Args:
        url: The URL to check (e.g. 'upatras.gr' or 'uop.gr').
    """
    target = url.strip()
    if not target.startswith("http"):
        target = f"https://{target}"
    
    try:
        async with httpx.AsyncClient(verify=False) as client:
            start_time = time.time()
            response = await client.get(target, timeout=3.0)
            duration = time.time() - start_time
            
            return (f"✅ Site: {target}\n"
                    f"   Status: {response.status_code} {response.reason_phrase}\n"
                    f"   Time: {duration:.2f}s")
    except httpx.TimeoutException:
        return f"❌ Site: {target} - TIMEOUT (exceeded 3s)"
    except Exception as e:
        return f"❌ Site: {target} - ERROR: {str(e)}"

# --- TOOL 2: Docker Inspector ---
@mcp.tool()
def list_docker_containers() -> str:
    """Lists all running Docker containers on the host machine."""
    try:
        client = docker.from_env()
        containers = client.containers.list()
        
        if not containers:
            return "No containers are currently running."
        
        report = "🐳 Running Containers:\n"
        for c in containers:
            report += f"- [{c.short_id}] {c.name} (Image: {c.image.tags[0] if c.image.tags else 'none'})\n"
            report += f"  Status: {c.status} | Ports: {c.ports}\n"
            
        return report
    except Exception as e:
        return f"Error connecting to Docker: {e}"

@mcp.tool()
def get_container_logs(container_name_or_id: str) -> str:
    """Fetches the last 20 lines of logs from a specific container.
    
    Args:
        container_name_or_id: The name or short ID of the container.
    """
    try:
        client = docker.from_env()
        container = client.containers.get(container_name_or_id)
        logs = container.logs(tail=20).decode('utf-8', errors='ignore')
        return f"📋 Logs for {container.name}:\n{logs}"
    except docker.errors.NotFound:
        return f"Container '{container_name_or_id}' not found."
    except Exception as e:
        return f"Error reading logs: {e}"

if __name__ == "__main__":
    mcp.run()