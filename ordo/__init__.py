"""
Ordo - An opinionated Python CLI for movie organization.
"""

__version__ = "0.2.0"
__author__ = "theridwanade"
__email__ = "theridwanade@gmail.com"

from .services.organization import MovieOrganizer
from .core.models import MovieInfo, SourceConfig, MovieTag

__all__ = ["MovieOrganizer", "MovieInfo", "SourceConfig", "MovieTag"]
