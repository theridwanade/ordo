from pathlib import Path
from typing import List
from ..core.config import ConfigManager
from ..core.models import SourceConfig, MovieInfo
from ..ui.prompts import UserPrompts
from .discovery import MovieDiscovery
from .file_operations import FileOperations

class MovieOrganizer:
    """Main service for organizing movies."""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.discovery = MovieDiscovery()
        self.file_ops = FileOperations()
        self.prompts = UserPrompts()
    
    def get_sources(self) -> SourceConfig:
        """Get source configuration from user or saved config."""
        # Try to load last sources
        last_config = self.config_manager.load_last_sources()
        
        if last_config and self.prompts.confirm_last_sources(last_config):
            return last_config
        
        # Get new sources from user
        config = self.prompts.get_source_paths()
        self.config_manager.save_sources(config)
        return config
    
    def organize_movies(self) -> None:
        """Main movie organization workflow."""
        # Get source paths
        config = self.get_sources()
        
        # Discover movies
        movie_names = self.discovery.discover_movies(config.movies_source)
        if not movie_names:
            print("No movies found in source directory")
            return
        
        # Get user tags for movies
        movie_infos = self.prompts.select_movie_tags(list(movie_names))
        if not movie_infos:
            print("No movies selected for organization")
            return
        
        # Enhance movie info with files and season information
        for movie_info in movie_infos:
            # Check if it's a series
            is_series = self.discovery.is_series(movie_info.name, config.movies_source)
            movie_info.is_series = is_series
            
            if is_series:
                # Get episodes grouped by season
                movie_info.seasons = self.discovery.get_seasons_for_series(
                    movie_info.name, config.movies_source
                )
            else:
                # Get all movie files
                movie_info.files = self.discovery.get_movie_files(
                    movie_info.name, config.movies_source
                )
        
        # Copy movies and subtitles
        self.file_ops.copy_movies(
            movie_infos, config.movies_source, config.destination
        )
        self.file_ops.copy_subtitles(
            movie_infos, config.subtitle_source, config.destination
        )
        
        print(f"Successfully organized {len(movie_infos)} movies!")
