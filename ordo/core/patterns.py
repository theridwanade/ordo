import re
from typing import Optional

class MoviePatterns:
    """Regex patterns for identifying different movie file formats."""
    
    SERIES_PATTERN = re.compile(
        r"^(?P<name>.+?)(?:_\d+p)?_S\d{1,2}_E\d{1,2}\.(mp4|avi|mkv|mov)$",
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
