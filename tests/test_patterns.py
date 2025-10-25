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

if __name__ == '__main__':
    unittest.main()
