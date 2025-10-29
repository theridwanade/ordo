import re
from typing import Optional, Tuple

class MoviePatterns:
    """Regex patterns for identifying different movie file formats."""
    
    SERIES_PATTERN = re.compile(
        r"^(?P<name>.+?)(?:_\d+p)?_S(?P<season>\d{1,2})_E(?P<episode>\d{1,2})\.(mp4|avi|mkv|mov)$",
        re.IGNORECASE
    )
    
    MOVIE_PATTERN = re.compile(
        r"^(?P<name>.+?)(?:_\d+p)?\.(mp4|avi|mkv|mov)$", 
        re.IGNORECASE
    )
    
    @classmethod
    def extract_movie_name(cls, filename: str) -> Optional[str]:
        """Extract movie name from filename using regex patterns."""
        # Try series pattern first
        match = cls.SERIES_PATTERN.match(filename)
        if match:
            return match.group("name")
            
        # Try movie pattern
        match = cls.MOVIE_PATTERN.match(filename)
        if match:
            return match.group("name")
            
        return None
    
    @classmethod
    def extract_season_episode(cls, filename: str) -> Optional[Tuple[str, int, int]]:
        """Extract series name, season number, and episode number from filename.
        
        Returns:
            Tuple of (series_name, season_number, episode_number) or None if not a series file.
        """
        match = cls.SERIES_PATTERN.match(filename)
        if match:
            return (
                match.group("name"),
                int(match.group("season")),
                int(match.group("episode"))
            )
        return None
    
    @classmethod
    def is_series(cls, filename: str) -> bool:
        """Check if filename represents a series episode."""
        return cls.SERIES_PATTERN.match(filename) is not None
