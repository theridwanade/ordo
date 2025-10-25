import shutil
from pathlib import Path
from typing import List
from tqdm import tqdm
from ..core.models import MovieInfo

class FileOperations:
    """Handles file copy and move operations."""
    
    @staticmethod
    def copy_movies(movie_infos: List[MovieInfo], source_path: Path, 
                   destination_path: Path, movie_files_map: dict) -> None:
        """Copy movie files to organized destination folders."""
        
        for movie_info in tqdm(movie_infos, desc="Organizing movies"):
            movie_files = movie_files_map.get(movie_info.name, [])
            
            if not movie_files:
                continue
                
            # Create destination folder
            dest_folder = destination_path / movie_info.tag.value / movie_info.name
            dest_folder.mkdir(parents=True, exist_ok=True)
            
            # Copy each file
            for filename in tqdm(movie_files, desc=f"Copying {movie_info.name}", leave=False):
                source_file = source_path / filename
                dest_file = dest_folder / filename
                
                if source_file.exists():
                    shutil.copy2(source_file, dest_file)
    
    @staticmethod
    def copy_subtitles(movie_infos: List[MovieInfo], subtitle_source: Path,
                      destination_path: Path) -> None:
        """Copy subtitle files to organized destination folders."""
        
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
                dest_subtitle_folder = (
                    destination_path / movie_info.tag.value / 
                    movie_info.name / "subtitles"
                )
                dest_subtitle_folder.mkdir(parents=True, exist_ok=True)
                
                # Copy all subtitle files
                for subtitle_file in subtitle_folder.iterdir():
                    if subtitle_file.is_file():
                        shutil.copy2(subtitle_file, dest_subtitle_folder)
