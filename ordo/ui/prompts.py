import questionary
from pathlib import Path
from typing import List, Optional
from ..core.models import SourceConfig, MovieTag, MovieInfo

class UserPrompts:
    """Handles all user interaction prompts."""
    
    @staticmethod
    def confirm_last_sources(config: SourceConfig) -> bool:
        """Ask user if they want to use last saved sources."""
        message = (
            f"Do you want to use the last sources?\n"
            f"Movies: {config.movies_source}\n"
            f"Subtitle: {config.subtitle_source}\n"
            f"Destination: {config.destination}\n"
        )
        return questionary.confirm(message).ask()
    
    @staticmethod
    def get_source_paths() -> SourceConfig:
        """Prompt user for source paths."""
        movies_source = questionary.path("What's the path to the movies").ask()
        subtitle_source = questionary.path("What's the path to the movies subtitle").ask()
        destination = questionary.path("What's the path to the destination").ask()
        
        if not all([movies_source, subtitle_source, destination]):
            raise ValueError("All paths are required")
            
        return SourceConfig(
            movies_source=Path(movies_source),
            subtitle_source=Path(subtitle_source),
            destination=Path(destination)
        )
    
    @staticmethod
    def select_movie_tags(movie_names: List[str]) -> List[MovieInfo]:
        """Prompt user to select tags for each movie."""
        movie_infos = []
        tag_choices = [tag.value for tag in MovieTag]
        
        for movie_name in movie_names:
            tag = questionary.select(
                f"Select a tag for {movie_name}:",
                choices=tag_choices
            ).ask()
            
            if tag and tag != MovieTag.IGNORE.value:
                movie_infos.append(MovieInfo(
                    name=movie_name,
                    tag=MovieTag(tag),
                    files=[]
                ))
        
        return movie_infos
    
    @staticmethod
    def select_operation_type() -> str:
        """Prompt user to select operation type (copy or move)."""
        operation = questionary.select(
            "Select operation type:",
            choices=["copy", "move"]
        ).ask()
        return operation or "copy"
    
    @staticmethod
    def select_checksum_option() -> bool:
        """Prompt user whether to calculate checksums."""
        return questionary.confirm(
            "Calculate checksums for file verification? (slower but ensures integrity)",
            default=True
        ).ask()
