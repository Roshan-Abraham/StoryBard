import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
import shutil

class FileManager:
    def __init__(self, base_dir: str = "sessions"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
    def get_session_dir(self, thread_id: str) -> Path:
        """Get or create session directory"""
        session_dir = self.base_dir / thread_id
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir
        
    def write_file(self, thread_id: str, filename: str, content: Union[str, Dict, bytes],
                   subfolder: Optional[str] = None) -> str:
        """Write content to a file in the session directory"""
        session_dir = self.get_session_dir(thread_id)
        if subfolder:
            file_path = session_dir / subfolder / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            file_path = session_dir / filename
            
        if isinstance(content, bytes):
            file_path.write_bytes(content)
        elif isinstance(content, (dict, list)):
            if filename.endswith('.json'):
                file_path.write_text(json.dumps(content, indent=2))
            elif filename.endswith(('.yml', '.yaml')):
                file_path.write_text(yaml.dump(content))
        else:
            file_path.write_text(str(content))
            
        return str(file_path)
        
    def read_file(self, thread_id: str, filename: str, 
                  subfolder: Optional[str] = None) -> Union[str, Dict, bytes]:
        """Read content from a file in the session directory"""
        session_dir = self.get_session_dir(thread_id)
        if subfolder:
            file_path = session_dir / subfolder / filename
        else:
            file_path = session_dir / filename
            
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if file_path.suffix in ['.json']:
            return json.loads(file_path.read_text())
        elif file_path.suffix in ['.yml', '.yaml']:
            return yaml.safe_load(file_path.read_text())
        elif file_path.suffix in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
            return file_path.read_bytes()
        else:
            return file_path.read_text()
            
    def list_files(self, thread_id: str, subfolder: Optional[str] = None) -> list:
        """List all files in the session directory"""
        session_dir = self.get_session_dir(thread_id)
        if subfolder:
            search_dir = session_dir / subfolder
        else:
            search_dir = session_dir
        return [f.name for f in search_dir.glob('*') if f.is_file()]
