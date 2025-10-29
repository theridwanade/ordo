import unittest
from pathlib import Path
import tempfile
import shutil
from ordo.services.file_operations import FileOperations
from ordo.core.models import MovieInfo, MovieTag

class TestFileOperations(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.source_path = self.temp_path / "source"
        self.dest_path = self.temp_path / "dest"
        self.subtitle_source = self.temp_path / "subtitles"
        
        self.source_path.mkdir()
        self.dest_path.mkdir()
        self.subtitle_source.mkdir()
        
        self.file_ops = FileOperations()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_copy_series_with_multiple_seasons(self):
        # Create test series files
        test_files = [
            "SeriesA_S01_E01.mkv",
            "SeriesA_S01_E02.mkv",
            "SeriesA_S02_E01.mkv",
            "SeriesA_S02_E02.mkv",
        ]
        
        for filename in test_files:
            (self.source_path / filename).write_text(f"content of {filename}")
        
        # Create MovieInfo for series
        movie_info = MovieInfo(
            name="SeriesA",
            tag=MovieTag.ANIME,
            files=[],
            is_series=True,
            seasons={
                1: ["SeriesA_S01_E01.mkv", "SeriesA_S01_E02.mkv"],
                2: ["SeriesA_S02_E01.mkv", "SeriesA_S02_E02.mkv"]
            }
        )
        
        # Copy movies
        self.file_ops.copy_movies([movie_info], self.source_path, self.dest_path)
        
        # Verify folder structure
        season1_folder = self.dest_path / "Anime" / "SeriesA" / "SeriesA Season 1"
        season2_folder = self.dest_path / "Anime" / "SeriesA" / "SeriesA Season 2"
        
        self.assertTrue(season1_folder.exists())
        self.assertTrue(season2_folder.exists())
        
        # Verify files are in correct season folders
        self.assertTrue((season1_folder / "SeriesA_S01_E01.mkv").exists())
        self.assertTrue((season1_folder / "SeriesA_S01_E02.mkv").exists())
        self.assertTrue((season2_folder / "SeriesA_S02_E01.mkv").exists())
        self.assertTrue((season2_folder / "SeriesA_S02_E02.mkv").exists())
    
    def test_copy_regular_movie(self):
        # Create test movie file
        (self.source_path / "MovieA_1080p.mp4").write_text("movie content")
        
        # Create MovieInfo for regular movie
        movie_info = MovieInfo(
            name="MovieA",
            tag=MovieTag.AMERICAN_ARCHIVE,
            files=["MovieA_1080p.mp4"],
            is_series=False
        )
        
        # Copy movie
        self.file_ops.copy_movies([movie_info], self.source_path, self.dest_path)
        
        # Verify folder structure
        movie_folder = self.dest_path / "American archive" / "MovieA"
        
        self.assertTrue(movie_folder.exists())
        self.assertTrue((movie_folder / "MovieA_1080p.mp4").exists())
    
    def test_copy_subtitles_for_series(self):
        # Create subtitle folder and files for series
        subtitle_folder = self.subtitle_source / "SeriesA"
        subtitle_folder.mkdir()
        (subtitle_folder / "SeriesA_S01_E01.srt").write_text("subtitle content")
        (subtitle_folder / "SeriesA_S02_E01.srt").write_text("subtitle content")
        
        # Create MovieInfo for series
        movie_info = MovieInfo(
            name="SeriesA",
            tag=MovieTag.ANIME,
            files=[],
            is_series=True,
            seasons={
                1: ["SeriesA_S01_E01.mkv"],
                2: ["SeriesA_S02_E01.mkv"]
            }
        )
        
        # Copy subtitles
        self.file_ops.copy_subtitles([movie_info], self.subtitle_source, self.dest_path)
        
        # Verify subtitles are in correct season folders
        season1_subtitles = self.dest_path / "Anime" / "SeriesA" / "SeriesA Season 1" / "subtitles"
        season2_subtitles = self.dest_path / "Anime" / "SeriesA" / "SeriesA Season 2" / "subtitles"
        
        self.assertTrue(season1_subtitles.exists())
        self.assertTrue(season2_subtitles.exists())
        self.assertTrue((season1_subtitles / "SeriesA_S01_E01.srt").exists())
        self.assertTrue((season2_subtitles / "SeriesA_S02_E01.srt").exists())
    
    def test_copy_subtitles_for_movie(self):
        # Create subtitle folder and files for movie
        subtitle_folder = self.subtitle_source / "MovieA"
        subtitle_folder.mkdir()
        (subtitle_folder / "MovieA_eng.srt").write_text("subtitle content")
        (subtitle_folder / "MovieA_spa.srt").write_text("subtitle content")
        
        # Create MovieInfo for regular movie
        movie_info = MovieInfo(
            name="MovieA",
            tag=MovieTag.AMERICAN_ARCHIVE,
            files=["MovieA_1080p.mp4"],
            is_series=False
        )
        
        # Copy subtitles
        self.file_ops.copy_subtitles([movie_info], self.subtitle_source, self.dest_path)
        
        # Verify subtitles are in movie folder
        subtitles_folder = self.dest_path / "American archive" / "MovieA" / "subtitles"
        
        self.assertTrue(subtitles_folder.exists())
        self.assertTrue((subtitles_folder / "MovieA_eng.srt").exists())
        self.assertTrue((subtitles_folder / "MovieA_spa.srt").exists())

if __name__ == '__main__':
    unittest.main()
