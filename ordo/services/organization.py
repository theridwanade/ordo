import logging
from pathlib import Path
from typing import List
from ..core.config import ConfigManager
from ..core.models import SourceConfig, MovieInfo
from ..ui.prompts import UserPrompts
from .discovery import MovieDiscovery
from .file_operations import FileOperations
from .enhanced_file_operations import EnhancedFileOperations

logger = logging.getLogger(__name__)

class MovieOrganizer:
    """Main service for organizing movies."""
    
    def __init__(self, use_enhanced_operations: bool = True):
        self.config_manager = ConfigManager()
        self.discovery = MovieDiscovery()
        self.file_ops = FileOperations()
        self.enhanced_file_ops = None
        self.use_enhanced = use_enhanced_operations
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
        
        # Get operation type (copy or move)
        operation_type = self.prompts.select_operation_type()
        
        # Get checksum option
        calculate_checksums = self.prompts.select_checksum_option()
        
        # Initialize enhanced file operations if using them
        if self.use_enhanced:
            self.enhanced_file_ops = EnhancedFileOperations(
                max_workers=4,
                calculate_checksums=calculate_checksums
            )
        
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
        
        # Copy or move movies and subtitles
        if self.use_enhanced and self.enhanced_file_ops:
            logger.info(f"Using enhanced file operations with {operation_type}")
            metadata = self.enhanced_file_ops.copy_movies(
                movie_infos, config.movies_source, config.destination, operation_type
            )
            self.enhanced_file_ops.copy_subtitles(
                movie_infos, config.subtitle_source, config.destination, operation_type
            )
            
            # Print summary
            total_files = sum(len(m.files) for m in metadata.values())
            total_size = sum(
                f.size_bytes for m in metadata.values() 
                for f in m.files.values()
            )
            print(f"\n{'=' * 60}")
            print(f"Operation completed successfully!")
            print(f"Operation type: {operation_type}")
            print(f"Movies processed: {len(movie_infos)}")
            print(f"Total files: {total_files}")
            print(f"Total size: {total_size / (1024**3):.2f} GB")
            print(f"Checksums calculated: {calculate_checksums}")
            print(f"{'=' * 60}\n")
        else:
            logger.info("Using legacy file operations (copy only)")
            self.file_ops.copy_movies(
                movie_infos, config.movies_source, config.destination
            )
            self.file_ops.copy_subtitles(
                movie_infos, config.subtitle_source, config.destination
            )
            print(f"Successfully organized {len(movie_infos)} movies!")
