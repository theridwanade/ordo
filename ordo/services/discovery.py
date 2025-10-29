import os
from pathlib import Path
from typing import List, Set, Dict
from ..core.patterns import MoviePatterns

class MovieDiscovery:
    """Service for discovering and parsing movie files."""
    
    def __init__(self):
        self.patterns = MoviePatterns()
    
    def discover_movies(self, source_path: Path) -> Set[str]:
        """Discover unique movie names from source directory."""
        if not source_path.exists():
            raise FileNotFoundError(f"Source path does not exist: {source_path}")
            
        movie_names = set()
        
        for filename in os.listdir(source_path):
            movie_name = self.patterns.extract_movie_name(filename)
            if movie_name:
                movie_names.add(movie_name)
            else:
                print(f"Warning: Unrecognized file format: {filename}")
        
        return movie_names
    
    def get_movie_files(self, movie_name: str, source_path: Path) -> List[str]:
        """Get all files belonging to a specific movie."""
        if not source_path.exists():
            return []
            
        return [
            f for f in os.listdir(source_path) 
            if f.startswith(movie_name)
        ]
    
    def get_seasons_for_series(self, movie_name: str, source_path: Path) -> Dict[int, List[str]]:
        """Get episodes grouped by season for a series.
        
        Returns:
            Dictionary mapping season numbers to lists of episode filenames.
        """
        if not source_path.exists():
            return {}
        
        seasons = {}
        for filename in os.listdir(source_path):
            season_info = self.patterns.extract_season_episode(filename)
            if season_info:
                series_name, season_num, episode_num = season_info
                if series_name == movie_name:
                    if season_num not in seasons:
                        seasons[season_num] = []
                    seasons[season_num].append(filename)
        
        return seasons
    
    def is_series(self, movie_name: str, source_path: Path) -> bool:
        """Check if a movie is actually a series with episodes."""
        if not source_path.exists():
            return False
        
        for filename in os.listdir(source_path):
            if filename.startswith(movie_name) and self.patterns.is_series(filename):
                return True
        
        return False
