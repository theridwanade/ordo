import shutil
from pathlib import Path
from typing import List
from tqdm import tqdm
from ..core.models import MovieInfo

class FileOperations:
    """Handles file copy and move operations."""
    
    @staticmethod
    def copy_movies(movie_infos: List[MovieInfo], source_path: Path, 
                   destination_path: Path) -> None:
        """Copy movie files to organized destination folders.
        
        For series with multiple seasons, creates structure:
        DESTINATION/<tag>/<series_name>/<series_name> Season X/episode_files
        
        For regular movies, creates structure:
        DESTINATION/<tag>/<movie_name>/movie_files
        """
        
        for movie_info in tqdm(movie_infos, desc="Organizing movies"):
            if movie_info.is_series and movie_info.seasons:
                # Handle series with seasons
                for season_num, episode_files in movie_info.seasons.items():
                    # Create season folder: SeriesName/SeriesName Season X
                    season_folder_name = f"{movie_info.name} Season {season_num}"
                    dest_folder = destination_path / movie_info.tag.value / movie_info.name / season_folder_name
                    dest_folder.mkdir(parents=True, exist_ok=True)
                    
                    # Copy each episode file
                    for filename in tqdm(episode_files, desc=f"Copying {season_folder_name}", leave=False):
                        source_file = source_path / filename
                        dest_file = dest_folder / filename
                        
                        if source_file.exists():
                            shutil.copy2(source_file, dest_file)
            else:
                # Handle regular movies
                if not movie_info.files:
                    continue
                    
                # Create destination folder
                dest_folder = destination_path / movie_info.tag.value / movie_info.name
                dest_folder.mkdir(parents=True, exist_ok=True)
                
                # Copy each file
                for filename in tqdm(movie_info.files, desc=f"Copying {movie_info.name}", leave=False):
                    source_file = source_path / filename
                    dest_file = dest_folder / filename
                    
                    if source_file.exists():
                        shutil.copy2(source_file, dest_file)
    
    @staticmethod
    def copy_subtitles(movie_infos: List[MovieInfo], subtitle_source: Path,
                      destination_path: Path) -> None:
        """Copy subtitle files to organized destination folders.
        
        For series with multiple seasons, places subtitles in season-specific folders.
        For regular movies, places subtitles in a 'subtitles' subfolder.
        """
        
        if not subtitle_source.exists():
            print(f"Warning: Subtitle source does not exist: {subtitle_source}")
            return
            
        subtitle_folders = list(subtitle_source.iterdir())
        
        for movie_info in tqdm(movie_infos, desc="Copying subtitles"):
            # Find matching subtitle folder
            matching_folders = [
                folder for folder in subtitle_folders 
                if folder.is_dir() and folder.name.startswith(movie_info.name)
            ]
            
            for subtitle_folder in matching_folders:
                if movie_info.is_series and movie_info.seasons:
                    # For series, try to match subtitles to seasons
                    # Look for season indicators in subtitle filenames
                    for subtitle_file in subtitle_folder.iterdir():
                        if not subtitle_file.is_file():
                            continue
                        
                        # Try to determine which season this subtitle belongs to
                        from ..core.patterns import MoviePatterns
                        season_info = MoviePatterns.extract_season_episode(subtitle_file.name)
                        
                        if season_info:
                            _, season_num, _ = season_info
                            if season_num in movie_info.seasons:
                                # Place in appropriate season folder
                                season_folder_name = f"{movie_info.name} Season {season_num}"
                                dest_subtitle_folder = (
                                    destination_path / movie_info.tag.value / 
                                    movie_info.name / season_folder_name / "subtitles"
                                )
                                dest_subtitle_folder.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(subtitle_file, dest_subtitle_folder)
                        else:
                            # If we can't determine season, copy to all seasons
                            for season_num in movie_info.seasons.keys():
                                season_folder_name = f"{movie_info.name} Season {season_num}"
                                dest_subtitle_folder = (
                                    destination_path / movie_info.tag.value / 
                                    movie_info.name / season_folder_name / "subtitles"
                                )
                                dest_subtitle_folder.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(subtitle_file, dest_subtitle_folder)
                else:
                    # For regular movies, use simple subtitle folder
                    dest_subtitle_folder = (
                        destination_path / movie_info.tag.value / 
                        movie_info.name / "subtitles"
                    )
                    dest_subtitle_folder.mkdir(parents=True, exist_ok=True)
                    
                    # Copy all subtitle files
                    for subtitle_file in subtitle_folder.iterdir():
                        if subtitle_file.is_file():
                            shutil.copy2(subtitle_file, dest_subtitle_folder)
