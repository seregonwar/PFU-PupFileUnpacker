import os
import hashlib
from typing import Optional

def calculate_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
    """calculate file hash"""
    hash_func = getattr(hashlib, algorithm)()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def ensure_directory(directory: str) -> None:
    """create directory if not exists"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_file_info(file_path: str) -> dict:
    """return detailed file information"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    stats = os.stat(file_path)
    return {
        'path': file_path,
        'size': stats.st_size,
        'created': stats.st_ctime,
        'modified': stats.st_mtime,
        'is_file': os.path.isfile(file_path),
        'is_dir': os.path.isdir(file_path)
    }

def safe_write_file(file_path: str, data: bytes, backup: bool = True) -> None:
    """write data to file in safe mode with backup option"""
    if backup and os.path.exists(file_path):
        backup_path = f"{file_path}.bak"
        os.rename(file_path, backup_path)
        
    with open(file_path, 'wb') as f:
        f.write(data)
        
def find_files_by_extension(directory: str, extension: str) -> list:
    """find all files with a specific extension"""
    matching_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                matching_files.append(os.path.join(root, file))
    return matching_files 