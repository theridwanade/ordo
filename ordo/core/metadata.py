"""Metadata handling for movie files."""
import hashlib
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict


@dataclass
class FileMetadata:
    """Metadata for a single file."""
    filename: str
    size_bytes: int
    modified_time: str
    md5_checksum: Optional[str] = None
    sha256_checksum: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert metadata to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FileMetadata':
        """Create metadata from dictionary."""
        return cls(**data)


@dataclass
class MovieMetadata:
    """Metadata for a movie or series."""
    name: str
    tag: str
    is_series: bool
    files: Dict[str, FileMetadata]  # filename -> metadata
    created_at: str
    operation_type: str  # "copy" or "move"
    
    def to_dict(self) -> dict:
        """Convert metadata to dictionary."""
        return {
            "name": self.name,
            "tag": self.tag,
            "is_series": self.is_series,
            "files": {k: v.to_dict() for k, v in self.files.items()},
            "created_at": self.created_at,
            "operation_type": self.operation_type
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MovieMetadata':
        """Create metadata from dictionary."""
        files = {k: FileMetadata.from_dict(v) for k, v in data["files"].items()}
        return cls(
            name=data["name"],
            tag=data["tag"],
            is_series=data["is_series"],
            files=files,
            created_at=data["created_at"],
            operation_type=data["operation_type"]
        )


class MetadataManager:
    """Manages metadata operations for movie files."""
    
    METADATA_FILENAME = ".ordo_metadata.json"
    CHUNK_SIZE = 8192  # 8KB chunks for checksum calculation
    
    @staticmethod
    def calculate_md5(file_path: Path) -> str:
        """Calculate MD5 checksum for a file."""
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(MetadataManager.CHUNK_SIZE), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    
    @staticmethod
    def calculate_sha256(file_path: Path) -> str:
        """Calculate SHA256 checksum for a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(MetadataManager.CHUNK_SIZE), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    @staticmethod
    def create_file_metadata(file_path: Path, calculate_checksums: bool = True) -> FileMetadata:
        """Create metadata for a single file."""
        stat = file_path.stat()
        metadata = FileMetadata(
            filename=file_path.name,
            size_bytes=stat.st_size,
            modified_time=datetime.fromtimestamp(stat.st_mtime).isoformat()
        )
        
        if calculate_checksums:
            metadata.md5_checksum = MetadataManager.calculate_md5(file_path)
            metadata.sha256_checksum = MetadataManager.calculate_sha256(file_path)
        
        return metadata
    
    @staticmethod
    def save_metadata(metadata: MovieMetadata, destination_dir: Path) -> None:
        """Save metadata to a JSON file in the destination directory."""
        metadata_file = destination_dir / MetadataManager.METADATA_FILENAME
        with open(metadata_file, 'w') as f:
            json.dump(metadata.to_dict(), f, indent=2)
    
    @staticmethod
    def load_metadata(destination_dir: Path) -> Optional[MovieMetadata]:
        """Load metadata from a JSON file in the destination directory."""
        metadata_file = destination_dir / MetadataManager.METADATA_FILENAME
        if not metadata_file.exists():
            return None
        
        with open(metadata_file, 'r') as f:
            data = json.load(f)
        
        return MovieMetadata.from_dict(data)
    
    @staticmethod
    def verify_file_integrity(file_path: Path, expected_metadata: FileMetadata) -> bool:
        """Verify file integrity against expected metadata."""
        if not file_path.exists():
            return False
        
        # Check file size
        if file_path.stat().st_size != expected_metadata.size_bytes:
            return False
        
        # Verify checksums if available
        if expected_metadata.md5_checksum:
            actual_md5 = MetadataManager.calculate_md5(file_path)
            if actual_md5 != expected_metadata.md5_checksum:
                return False
        
        if expected_metadata.sha256_checksum:
            actual_sha256 = MetadataManager.calculate_sha256(file_path)
            if actual_sha256 != expected_metadata.sha256_checksum:
                return False
        
        return True
