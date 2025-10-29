import unittest
from ordo.core.patterns import MoviePatterns

class TestMoviePatterns(unittest.TestCase):
    
    def test_extract_movie_name_from_series(self):
        filename = "MovieB_S01_E01.mkv"
        result = MoviePatterns.extract_movie_name(filename)
        self.assertEqual(result, "MovieB")
    
    def test_extract_movie_name_from_movie(self):
        filename = "MovieA_1080p.mp4"
        result = MoviePatterns.extract_movie_name(filename)
        self.assertEqual(result, "MovieA")
    
    def test_extract_movie_name_invalid_format(self):
        filename = "InvalidFile.txt"
        result = MoviePatterns.extract_movie_name(filename)
        self.assertIsNone(result)
    
    def test_extract_season_episode(self):
        filename = "SeriesA_S01_E05.mkv"
        result = MoviePatterns.extract_season_episode(filename)
        self.assertEqual(result, ("SeriesA", 1, 5))
    
    def test_extract_season_episode_with_quality(self):
        filename = "SeriesB_1080p_S02_E10.mp4"
        result = MoviePatterns.extract_season_episode(filename)
        self.assertEqual(result, ("SeriesB", 2, 10))
    
    def test_extract_season_episode_non_series(self):
        filename = "Movie_1080p.mp4"
        result = MoviePatterns.extract_season_episode(filename)
        self.assertIsNone(result)
    
    def test_is_series_true(self):
        filename = "SeriesA_S01_E01.mkv"
        result = MoviePatterns.is_series(filename)
        self.assertTrue(result)
    
    def test_is_series_false(self):
        filename = "Movie_1080p.mp4"
        result = MoviePatterns.is_series(filename)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
