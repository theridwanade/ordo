from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from enum import Enum

class MovieTag(Enum):
    CHINESE_ARCHIVE = "Chinese archive"
    AMERICAN_ARCHIVE = "American archive" 
    KOREAN_ARCHIVE = "Korean archive"
    ANIME = "Anime"
    IGNORE = "Ignore"

@dataclass
class MovieInfo:
    name: str
    tag: MovieTag
    files: List[str]

@dataclass
class SourceConfig:
    movies_source: Path
    subtitle_source: Path
    destination: Path
    
    def to_dict(self) -> dict:
        return {
            "movies_source": str(self.movies_source),
            "subtitle_source": str(self.subtitle_source), 
            "destination": str(self.destination)
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SourceConfig':
        return cls(
            movies_source=Path(data["movies_source"]),
            subtitle_source=Path(data["subtitle_source"]),
            destination=Path(data["destination"])
        )
