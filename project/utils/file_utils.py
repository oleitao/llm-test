import os
from pathlib import Path

def get_resource_path(relative_path):
    """
    Get absolute path for a resource, handling different running environments
    (local development, Docker container, etc.)
    """
    # Try direct access from current directory
    if Path(relative_path).exists():
        return str(Path(relative_path).resolve())
    
    # Try from the script's directory
    script_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
    path = script_dir / relative_path
    if path.exists():
        return str(path)
    
    # Try from Docker /app directory (if we're in a container)
    docker_path = Path('/app') / relative_path
    if docker_path.exists():
        return str(docker_path)
        
    # Return the original path if all else fails
    return relative_path
