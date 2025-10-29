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
    
    def test_get_seasons_for_series(self):
        # Create test files for a series with multiple seasons
        test_files = [
            "SeriesA_S01_E01.mkv",
            "SeriesA_S01_E02.mkv",
            "SeriesA_S02_E01.mkv",
            "SeriesA_S02_E02.mkv",
            "SeriesA_S02_E03.mkv",
        ]
        
        for filename in test_files:
            (self.temp_path / filename).touch()
        
        seasons = self.discovery.get_seasons_for_series("SeriesA", self.temp_path)
        
        self.assertEqual(len(seasons), 2)
        self.assertEqual(len(seasons[1]), 2)
        self.assertEqual(len(seasons[2]), 3)
        self.assertIn("SeriesA_S01_E01.mkv", seasons[1])
        self.assertIn("SeriesA_S02_E01.mkv", seasons[2])
    
    def test_is_series_true(self):
        # Create test files
        test_files = [
            "SeriesA_S01_E01.mkv",
            "SeriesA_S01_E02.mkv",
        ]
        
        for filename in test_files:
            (self.temp_path / filename).touch()
        
        result = self.discovery.is_series("SeriesA", self.temp_path)
        self.assertTrue(result)
    
    def test_is_series_false(self):
        # Create test files (regular movie)
        test_files = [
            "MovieA_1080p.mp4",
        ]
        
        for filename in test_files:
            (self.temp_path / filename).touch()
        
        result = self.discovery.is_series("MovieA", self.temp_path)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
