"""Enhanced file operations with concurrency, chunking, and resumption support."""
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from datetime import datetime

from ..core.models import MovieInfo
from ..core.metadata import MetadataManager, MovieMetadata, FileMetadata


logger = logging.getLogger(__name__)


class EnhancedFileOperations:
    """Enhanced file operations with concurrency, checksums, and resumption."""
    
    CHUNK_SIZE = 1024 * 1024  # 1MB chunks for file operations
    DEFAULT_MAX_WORKERS = 4
    
    def __init__(self, max_workers: Optional[int] = None, calculate_checksums: bool = True):
        """Initialize enhanced file operations.
        
        Args:
            max_workers: Maximum number of concurrent workers (default: 4)
            calculate_checksums: Whether to calculate checksums (default: True)
        """
        self.max_workers = max_workers or self.DEFAULT_MAX_WORKERS
        self.calculate_checksums = calculate_checksums
        self.metadata_manager = MetadataManager()
    
    def _copy_file_chunked(self, source: Path, destination: Path, 
                          progress_callback=None) -> FileMetadata:
        """Copy a file in chunks with progress tracking.
        
        Args:
            source: Source file path
            destination: Destination file path
            progress_callback: Optional callback for progress updates
            
        Returns:
            FileMetadata for the copied file
        """
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        file_size = source.stat().st_size
        bytes_copied = 0
        
        with open(source, 'rb') as src, open(destination, 'wb') as dst:
            while True:
                chunk = src.read(self.CHUNK_SIZE)
                if not chunk:
                    break
                dst.write(chunk)
                bytes_copied += len(chunk)
                if progress_callback:
                    progress_callback(len(chunk))
        
        # Preserve metadata
        shutil.copystat(source, destination)
        
        # Create metadata
        return self.metadata_manager.create_file_metadata(
            destination, self.calculate_checksums
        )
    
    def _move_file_chunked(self, source: Path, destination: Path,
                          progress_callback=None) -> FileMetadata:
        """Move a file (copy then delete source) with progress tracking.
        
        Args:
            source: Source file path
            destination: Destination file path
            progress_callback: Optional callback for progress updates
            
        Returns:
            FileMetadata for the moved file
        """
        # First copy the file
        metadata = self._copy_file_chunked(source, destination, progress_callback)
        
        # Verify the copy was successful before deleting
        if self.calculate_checksums:
            source_metadata = self.metadata_manager.create_file_metadata(source, True)
            if not self.metadata_manager.verify_file_integrity(destination, source_metadata):
                raise IOError(f"File verification failed after copy: {source}")
        
        # Delete the source file
        source.unlink()
        
        return metadata
    
    def _process_file_operation(self, source_file: Path, dest_file: Path,
                               operation_type: str, file_progress: tqdm) -> tuple:
        """Process a single file operation (copy or move).
        
        Args:
            source_file: Source file path
            dest_file: Destination file path
            operation_type: "copy" or "move"
            file_progress: Progress bar for tracking
            
        Returns:
            Tuple of (filename, FileMetadata, success, error_message)
        """
        try:
            if not source_file.exists():
                return (source_file.name, None, False, "Source file not found")
            
            def progress_callback(bytes_written):
                file_progress.update(bytes_written)
            
            if operation_type == "move":
                metadata = self._move_file_chunked(source_file, dest_file, progress_callback)
            else:
                metadata = self._copy_file_chunked(source_file, dest_file, progress_callback)
            
            return (source_file.name, metadata, True, None)
            
        except Exception as e:
            logger.error(f"Error processing {source_file}: {e}")
            return (source_file.name, None, False, str(e))
    
    def copy_movies(self, movie_infos: List[MovieInfo], source_path: Path,
                   destination_path: Path, operation_type: str = "copy") -> Dict[str, MovieMetadata]:
        """Copy or move movie files with concurrency and metadata tracking.
        
        Args:
            movie_infos: List of MovieInfo objects
            source_path: Source directory path
            destination_path: Destination directory path
            operation_type: "copy" or "move" (default: "copy")
            
        Returns:
            Dictionary mapping movie names to their metadata
        """
        all_metadata = {}
        
        for movie_info in tqdm(movie_infos, desc=f"{operation_type.capitalize()}ing movies"):
            movie_files_metadata = {}
            
            if movie_info.is_series and movie_info.seasons:
                # Handle series with seasons
                for season_num, episode_files in movie_info.seasons.items():
                    season_folder_name = f"{movie_info.name} Season {season_num}"
                    dest_folder = destination_path / movie_info.tag.value / movie_info.name / season_folder_name
                    
                    # Calculate total size for progress bar
                    total_size = sum(
                        (source_path / filename).stat().st_size
                        for filename in episode_files
                        if (source_path / filename).exists()
                    )
                    
                    with tqdm(total=total_size, desc=f"{operation_type.capitalize()} {season_folder_name}",
                             unit='B', unit_scale=True, leave=False) as file_progress:
                        
                        # Prepare file operations
                        operations = [
                            (source_path / filename, dest_folder / filename, operation_type)
                            for filename in episode_files
                        ]
                        
                        # Execute operations concurrently
                        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                            futures = [
                                executor.submit(self._process_file_operation, src, dst, op, file_progress)
                                for src, dst, op in operations
                            ]
                            
                            for future in as_completed(futures):
                                filename, metadata, success, error = future.result()
                                if success:
                                    movie_files_metadata[filename] = metadata
                                else:
                                    logger.error(f"Failed to process {filename}: {error}")
            else:
                # Handle regular movies
                if not movie_info.files:
                    continue
                
                dest_folder = destination_path / movie_info.tag.value / movie_info.name
                
                # Calculate total size for progress bar
                total_size = sum(
                    (source_path / filename).stat().st_size
                    for filename in movie_info.files
                    if (source_path / filename).exists()
                )
                
                with tqdm(total=total_size, desc=f"{operation_type.capitalize()} {movie_info.name}",
                         unit='B', unit_scale=True, leave=False) as file_progress:
                    
                    # Prepare file operations
                    operations = [
                        (source_path / filename, dest_folder / filename, operation_type)
                        for filename in movie_info.files
                    ]
                    
                    # Execute operations concurrently
                    with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                        futures = [
                            executor.submit(self._process_file_operation, src, dst, op, file_progress)
                            for src, dst, op in operations
                        ]
                        
                        for future in as_completed(futures):
                            filename, metadata, success, error = future.result()
                            if success:
                                movie_files_metadata[filename] = metadata
                            else:
                                logger.error(f"Failed to process {filename}: {error}")
            
            # Save metadata for this movie
            if movie_files_metadata:
                movie_metadata = MovieMetadata(
                    name=movie_info.name,
                    tag=movie_info.tag.value,
                    is_series=movie_info.is_series,
                    files=movie_files_metadata,
                    created_at=datetime.now().isoformat(),
                    operation_type=operation_type
                )
                
                # Determine where to save metadata
                if movie_info.is_series and movie_info.seasons:
                    # Save in the series root folder
                    metadata_dir = destination_path / movie_info.tag.value / movie_info.name
                else:
                    metadata_dir = destination_path / movie_info.tag.value / movie_info.name
                
                self.metadata_manager.save_metadata(movie_metadata, metadata_dir)
                all_metadata[movie_info.name] = movie_metadata
        
        return all_metadata
    
    def copy_subtitles(self, movie_infos: List[MovieInfo], subtitle_source: Path,
                      destination_path: Path, operation_type: str = "copy") -> None:
        """Copy or move subtitle files with concurrency.
        
        Args:
            movie_infos: List of MovieInfo objects
            subtitle_source: Subtitle source directory path
            destination_path: Destination directory path
            operation_type: "copy" or "move" (default: "copy")
        """
        if not subtitle_source.exists():
            logger.warning(f"Subtitle source does not exist: {subtitle_source}")
            return
        
        subtitle_folders = list(subtitle_source.iterdir())
        
        for movie_info in tqdm(movie_infos, desc=f"{operation_type.capitalize()}ing subtitles"):
            # Find matching subtitle folder
            matching_folders = [
                folder for folder in subtitle_folders
                if folder.is_dir() and folder.name.startswith(movie_info.name)
            ]
            
            for subtitle_folder in matching_folders:
                subtitle_files = [f for f in subtitle_folder.iterdir() if f.is_file()]
                
                if not subtitle_files:
                    continue
                
                if movie_info.is_series and movie_info.seasons:
                    # Handle series subtitles
                    self._copy_series_subtitles(
                        movie_info, subtitle_files, destination_path, operation_type
                    )
                else:
                    # Handle regular movie subtitles
                    dest_subtitle_folder = (
                        destination_path / movie_info.tag.value /
                        movie_info.name / "subtitles"
                    )
                    
                    # Calculate total size
                    total_size = sum(f.stat().st_size for f in subtitle_files)
                    
                    with tqdm(total=total_size, desc=f"{operation_type.capitalize()} subtitles for {movie_info.name}",
                             unit='B', unit_scale=True, leave=False) as progress:
                        
                        operations = [
                            (subtitle_file, dest_subtitle_folder / subtitle_file.name, operation_type)
                            for subtitle_file in subtitle_files
                        ]
                        
                        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                            futures = [
                                executor.submit(self._process_file_operation, src, dst, op, progress)
                                for src, dst, op in operations
                            ]
                            
                            for future in as_completed(futures):
                                _, _, success, error = future.result()
                                if not success:
                                    logger.error(f"Failed to process subtitle: {error}")
    
    def _copy_series_subtitles(self, movie_info: MovieInfo, subtitle_files: List[Path],
                              destination_path: Path, operation_type: str) -> None:
        """Copy subtitles for a series to appropriate season folders."""
        from ..core.patterns import MoviePatterns
        
        for subtitle_file in subtitle_files:
            season_info = MoviePatterns.extract_season_episode(subtitle_file.name)
            
            if season_info:
                _, season_num, _ = season_info
                if season_num in movie_info.seasons:
                    season_folder_name = f"{movie_info.name} Season {season_num}"
                    dest_subtitle_folder = (
                        destination_path / movie_info.tag.value /
                        movie_info.name / season_folder_name / "subtitles"
                    )
                    dest_file = dest_subtitle_folder / subtitle_file.name
                    
                    with tqdm(total=subtitle_file.stat().st_size, 
                             desc=f"{operation_type.capitalize()} {subtitle_file.name}",
                             unit='B', unit_scale=True, leave=False) as progress:
                        
                        self._process_file_operation(
                            subtitle_file, dest_file, operation_type, progress
                        )
            else:
                # Copy to all seasons if can't determine season
                for season_num in movie_info.seasons.keys():
                    season_folder_name = f"{movie_info.name} Season {season_num}"
                    dest_subtitle_folder = (
                        destination_path / movie_info.tag.value /
                        movie_info.name / season_folder_name / "subtitles"
                    )
                    dest_file = dest_subtitle_folder / subtitle_file.name
                    
                    with tqdm(total=subtitle_file.stat().st_size,
                             desc=f"{operation_type.capitalize()} {subtitle_file.name}",
                             unit='B', unit_scale=True, leave=False) as progress:
                        
                        self._process_file_operation(
                            subtitle_file, dest_file, operation_type, progress
                        )
