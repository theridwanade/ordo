import unittest
from pathlib import Path
import tempfile
import os
from ordo.services.discovery import MovieDiscovery

class TestMovieDiscovery(unittest.TestCase):
    
    def setUp(self):
        self.discovery = MovieDiscovery()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_discover_movies_with_valid_files(self):
        # Create test files
        test_files = [
            "MovieA_1080p.mp4",
            "MovieB_S01_E01.mkv", 
            "MovieB_S01_E02.mkv",
            "MovieC.mov"
        ]
        
        for filename in test_files:
            (self.temp_path / filename).touch()
        
        discovered_movies = self.discovery.discover_movies(self.temp_path)
        
        expected_movies = {"MovieA", "MovieB", "MovieC"}
        self.assertEqual(discovered_movies, expected_movies)
    
    def test_get_movie_files(self):
        # Create test files
        test_files = [
            "MovieA_1080p.mp4",
            "MovieB_S01_E01.mkv", 
            "MovieB_S01_E02.mkv",
            "Other_File.txt"
        ]
        
        for filename in test_files:
            (self.temp_path / filename).touch()
        
        movie_b_files = self.discovery.get_movie_files("MovieB", self.temp_path)
        expected_files = ["MovieB_S01_E01.mkv", "MovieB_S01_E02.mkv"]
        
        self.assertEqual(sorted(movie_b_files), sorted(expected_files))

if __name__ == '__main__':
    unittest.main()
