"""Tests for enhanced file operations with concurrency."""
import unittest
import tempfile
import shutil
from pathlib import Path
import time

from ordo.services.enhanced_file_operations import EnhancedFileOperations
from ordo.core.models import MovieInfo, MovieTag


class TestEnhancedFileOperations(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.source_path = self.temp_path / "source"
        self.dest_path = self.temp_path / "dest"
        self.subtitle_source = self.temp_path / "subtitles"
        
        self.source_path.mkdir()
        self.dest_path.mkdir()
        self.subtitle_source.mkdir()
        
        # Use fast operations for testing (no checksums)
        self.file_ops = EnhancedFileOperations(
            max_workers=2, 
            calculate_checksums=False
        )
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_copy_regular_movie_concurrent(self):
        # Create test movie files
        test_files = [
            "MovieA_1080p.mp4",
            "MovieA_720p.mp4",
            "MovieA.nfo"
        ]
        
        for filename in test_files:
            (self.source_path / filename).write_text(f"content of {filename}")
        
        # Create MovieInfo
        movie_info = MovieInfo(
            name="MovieA",
            tag=MovieTag.AMERICAN_ARCHIVE,
            files=test_files,
            is_series=False
        )
        
        # Copy movies
        metadata = self.file_ops.copy_movies(
            [movie_info], self.source_path, self.dest_path, "copy"
        )
        
        # Verify folder structure
        movie_folder = self.dest_path / "American archive" / "MovieA"
        self.assertTrue(movie_folder.exists())
        
        # Verify all files copied
        for filename in test_files:
            self.assertTrue((movie_folder / filename).exists())
        
        # Verify metadata was created
        self.assertIn("MovieA", metadata)
        self.assertEqual(len(metadata["MovieA"].files), 3)
        
        # Verify metadata file was saved
        metadata_file = movie_folder / ".ordo_metadata.json"
        self.assertTrue(metadata_file.exists())
    
    def test_move_regular_movie(self):
        # Create test movie file
        test_file = "MovieB_1080p.mp4"
        source_file = self.source_path / test_file
        source_file.write_text("movie content")
        
        # Create MovieInfo
        movie_info = MovieInfo(
            name="MovieB",
            tag=MovieTag.ANIME,
            files=[test_file],
            is_series=False
        )
        
        # Move movie
        metadata = self.file_ops.copy_movies(
            [movie_info], self.source_path, self.dest_path, "move"
        )
        
        # Verify destination exists
        dest_file = self.dest_path / "Anime" / "MovieB" / test_file
        self.assertTrue(dest_file.exists())
        
        # Verify source was deleted
        self.assertFalse(source_file.exists())
        
        # Verify metadata
        self.assertIn("MovieB", metadata)
        self.assertEqual(metadata["MovieB"].operation_type, "move")
    
    def test_copy_series_with_seasons_concurrent(self):
        # Create test series files
        test_files = [
            "SeriesA_S01_E01.mkv",
            "SeriesA_S01_E02.mkv",
            "SeriesA_S01_E03.mkv",
            "SeriesA_S02_E01.mkv",
            "SeriesA_S02_E02.mkv",
        ]
        
        for filename in test_files:
            (self.source_path / filename).write_text(f"content of {filename}")
        
        # Create MovieInfo
        movie_info = MovieInfo(
            name="SeriesA",
            tag=MovieTag.KOREAN_ARCHIVE,
            files=[],
            is_series=True,
            seasons={
                1: ["SeriesA_S01_E01.mkv", "SeriesA_S01_E02.mkv", "SeriesA_S01_E03.mkv"],
                2: ["SeriesA_S02_E01.mkv", "SeriesA_S02_E02.mkv"]
            }
        )
        
        # Copy series
        metadata = self.file_ops.copy_movies(
            [movie_info], self.source_path, self.dest_path, "copy"
        )
        
        # Verify folder structure
        season1_folder = self.dest_path / "Korean archive" / "SeriesA" / "SeriesA Season 1"
        season2_folder = self.dest_path / "Korean archive" / "SeriesA" / "SeriesA Season 2"
        
        self.assertTrue(season1_folder.exists())
        self.assertTrue(season2_folder.exists())
        
        # Verify files are in correct season folders
        self.assertTrue((season1_folder / "SeriesA_S01_E01.mkv").exists())
        self.assertTrue((season1_folder / "SeriesA_S01_E03.mkv").exists())
        self.assertTrue((season2_folder / "SeriesA_S02_E01.mkv").exists())
        
        # Verify metadata
        self.assertIn("SeriesA", metadata)
        self.assertEqual(len(metadata["SeriesA"].files), 5)
    
    def test_copy_with_checksums(self):
        # Create file operations with checksum enabled
        file_ops_with_checksum = EnhancedFileOperations(
            max_workers=2,
            calculate_checksums=True
        )
        
        # Create test file
        test_file = "MovieC_1080p.mp4"
        (self.source_path / test_file).write_text("test content for checksum")
        
        # Create MovieInfo
        movie_info = MovieInfo(
            name="MovieC",
            tag=MovieTag.CHINESE_ARCHIVE,
            files=[test_file],
            is_series=False
        )
        
        # Copy with checksums
        metadata = file_ops_with_checksum.copy_movies(
            [movie_info], self.source_path, self.dest_path, "copy"
        )
        
        # Verify checksums were calculated
        self.assertIn("MovieC", metadata)
        file_metadata = metadata["MovieC"].files[test_file]
        self.assertIsNotNone(file_metadata.md5_checksum)
        self.assertIsNotNone(file_metadata.sha256_checksum)
    
    def test_copy_subtitles_concurrent(self):
        # Create subtitle folder and files
        subtitle_folder = self.subtitle_source / "MovieD"
        subtitle_folder.mkdir()
        
        subtitle_files = [
            "MovieD_eng.srt",
            "MovieD_spa.srt",
            "MovieD_fra.srt"
        ]
        
        for filename in subtitle_files:
            (subtitle_folder / filename).write_text("subtitle content")
        
        # Create MovieInfo
        movie_info = MovieInfo(
            name="MovieD",
            tag=MovieTag.AMERICAN_ARCHIVE,
            files=["MovieD_1080p.mp4"],
            is_series=False
        )
        
        # Copy subtitles
        self.file_ops.copy_subtitles(
            [movie_info], self.subtitle_source, self.dest_path, "copy"
        )
        
        # Verify subtitles copied
        subtitles_folder = self.dest_path / "American archive" / "MovieD" / "subtitles"
        self.assertTrue(subtitles_folder.exists())
        
        for filename in subtitle_files:
            self.assertTrue((subtitles_folder / filename).exists())
    
    def test_chunked_copy_large_file(self):
        # Create a larger test file
        test_file = "LargeMovie_1080p.mp4"
        large_content = "X" * (2 * 1024 * 1024)  # 2MB file
        (self.source_path / test_file).write_text(large_content)
        
        # Create MovieInfo
        movie_info = MovieInfo(
            name="LargeMovie",
            tag=MovieTag.ANIME,
            files=[test_file],
            is_series=False
        )
        
        # Copy movie
        metadata = self.file_ops.copy_movies(
            [movie_info], self.source_path, self.dest_path, "copy"
        )
        
        # Verify file copied correctly
        dest_file = self.dest_path / "Anime" / "LargeMovie" / test_file
        self.assertTrue(dest_file.exists())
        self.assertEqual(dest_file.stat().st_size, len(large_content))
        
        # Verify metadata has correct size
        file_metadata = metadata["LargeMovie"].files[test_file]
        self.assertEqual(file_metadata.size_bytes, len(large_content))


if __name__ == '__main__':
    unittest.main()
