"""Tests for metadata handling functionality."""
import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from ordo.core.metadata import (
    FileMetadata, MovieMetadata, MetadataManager
)


class TestMetadata(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.manager = MetadataManager()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_file_metadata_creation(self):
        # Create a test file
        test_file = self.temp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        # Create metadata without checksums
        metadata = self.manager.create_file_metadata(test_file, calculate_checksums=False)
        
        self.assertEqual(metadata.filename, "test.txt")
        self.assertEqual(metadata.size_bytes, 13)
        self.assertIsNotNone(metadata.modified_time)
        self.assertIsNone(metadata.md5_checksum)
        self.assertIsNone(metadata.sha256_checksum)
    
    def test_file_metadata_with_checksums(self):
        # Create a test file
        test_file = self.temp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        # Create metadata with checksums
        metadata = self.manager.create_file_metadata(test_file, calculate_checksums=True)
        
        self.assertEqual(metadata.filename, "test.txt")
        self.assertIsNotNone(metadata.md5_checksum)
        self.assertIsNotNone(metadata.sha256_checksum)
        # Known MD5 for "Hello, World!"
        self.assertEqual(metadata.md5_checksum, "65a8e27d8879283831b664bd8b7f0ad4")
    
    def test_calculate_md5(self):
        test_file = self.temp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        md5 = self.manager.calculate_md5(test_file)
        self.assertEqual(md5, "65a8e27d8879283831b664bd8b7f0ad4")
    
    def test_calculate_sha256(self):
        test_file = self.temp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        sha256 = self.manager.calculate_sha256(test_file)
        self.assertEqual(
            sha256, 
            "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"
        )
    
    def test_movie_metadata_serialization(self):
        # Create file metadata
        file_meta = FileMetadata(
            filename="movie.mp4",
            size_bytes=1000,
            modified_time="2024-01-01T00:00:00",
            md5_checksum="abc123",
            sha256_checksum="def456"
        )
        
        # Create movie metadata
        movie_meta = MovieMetadata(
            name="TestMovie",
            tag="Anime",
            is_series=False,
            files={"movie.mp4": file_meta},
            created_at="2024-01-01T00:00:00",
            operation_type="copy"
        )
        
        # Convert to dict and back
        meta_dict = movie_meta.to_dict()
        restored_meta = MovieMetadata.from_dict(meta_dict)
        
        self.assertEqual(restored_meta.name, "TestMovie")
        self.assertEqual(restored_meta.tag, "Anime")
        self.assertEqual(len(restored_meta.files), 1)
        self.assertEqual(restored_meta.files["movie.mp4"].filename, "movie.mp4")
    
    def test_save_and_load_metadata(self):
        # Create metadata
        file_meta = FileMetadata(
            filename="movie.mp4",
            size_bytes=1000,
            modified_time="2024-01-01T00:00:00",
            md5_checksum="abc123",
            sha256_checksum="def456"
        )
        
        movie_meta = MovieMetadata(
            name="TestMovie",
            tag="Anime",
            is_series=False,
            files={"movie.mp4": file_meta},
            created_at="2024-01-01T00:00:00",
            operation_type="copy"
        )
        
        # Save metadata
        self.manager.save_metadata(movie_meta, self.temp_path)
        
        # Check file exists
        metadata_file = self.temp_path / ".ordo_metadata.json"
        self.assertTrue(metadata_file.exists())
        
        # Load metadata
        loaded_meta = self.manager.load_metadata(self.temp_path)
        
        self.assertIsNotNone(loaded_meta)
        self.assertEqual(loaded_meta.name, "TestMovie")
        self.assertEqual(loaded_meta.tag, "Anime")
        self.assertEqual(len(loaded_meta.files), 1)
    
    def test_verify_file_integrity_success(self):
        # Create a test file
        test_file = self.temp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        # Create metadata
        metadata = self.manager.create_file_metadata(test_file, calculate_checksums=True)
        
        # Verify integrity
        is_valid = self.manager.verify_file_integrity(test_file, metadata)
        self.assertTrue(is_valid)
    
    def test_verify_file_integrity_failure_modified(self):
        # Create a test file
        test_file = self.temp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        # Create metadata
        metadata = self.manager.create_file_metadata(test_file, calculate_checksums=True)
        
        # Modify the file
        test_file.write_text("Modified content")
        
        # Verify integrity should fail
        is_valid = self.manager.verify_file_integrity(test_file, metadata)
        self.assertFalse(is_valid)
    
    def test_verify_file_integrity_missing_file(self):
        # Create metadata for non-existent file
        metadata = FileMetadata(
            filename="missing.txt",
            size_bytes=100,
            modified_time="2024-01-01T00:00:00",
            md5_checksum="abc123",
            sha256_checksum="def456"
        )
        
        missing_file = self.temp_path / "missing.txt"
        
        # Verify should fail
        is_valid = self.manager.verify_file_integrity(missing_file, metadata)
        self.assertFalse(is_valid)


if __name__ == '__main__':
    unittest.main()
