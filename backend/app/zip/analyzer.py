"""Zip file analysis module"""
import base64
import shutil
import tempfile
from pathlib import Path
from typing import Optional
import patoolib

from ..models.schemas import ZipInput, ProjectInfo
from ..detection import detect_project


class ZipAnalyzer:
    """Analyzes zip files for Dockerfile generation"""
    
    def __init__(self, max_size_mb: int = 100):
        self.max_size_mb = max_size_mb
    
    def analyze(self, zip_input: ZipInput) -> ProjectInfo:
        """Analyze zip file and return project info"""
        # Decode base64 content
        zip_bytes = base64.b64decode(zip_input.content_base64)
        
        # Check size
        size_mb = len(zip_bytes) / (1024 * 1024)
        if size_mb > self.max_size_mb:
            raise ValueError(f"Zip file too large: {size_mb:.1f}MB > {self.max_size_mb}MB")
        
        # Extract to temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            extract_path = Path(tmpdir) / "extracted"
            extract_path.mkdir()
            
            # Write zip file
            zip_path = Path(tmpdir) / zip_input.filename
            zip_path.write_bytes(zip_bytes)
            
            # Extract using patoolib (handles multiple formats)
            try:
                patoolib.extract_archive(str(zip_path), outdir=str(extract_path))
            except Exception as e:
                raise ValueError(f"Failed to extract archive: {e}")
            
            # Find project root (handle nested directories)
            project_root = self._find_project_root(extract_path)
            
            return detect_project(project_root)
    
    def _find_project_root(self, extract_path: Path) -> Path:
        """Find the actual project root (skip single top-level directory)"""
        items = list(extract_path.iterdir())
        
        # If there's only one directory, it's likely the project root
        if len(items) == 1 and items[0].is_dir():
            return items[0]
        
        return extract_path


class ZipValidator:
    """Validates zip file before processing"""
    
    def __init__(self, max_size_mb: int = 100):
        self.max_size_mb = max_size_mb
    
    def validate(self, zip_input: ZipInput) -> dict:
        """Validate zip file"""
        try:
            zip_bytes = base64.b64decode(zip_input.content_base64)
            size_mb = len(zip_bytes) / (1024 * 1024)
            
            if size_mb > self.max_size_mb:
                return {
                    "valid": False,
                    "error": f"File too large: {size_mb:.1f}MB > {self.max_size_mb}MB",
                    "size_mb": size_mb,
                }
            
            # Try to extract to verify it's a valid archive
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_path = Path(tmpdir) / zip_input.filename
                zip_path.write_bytes(zip_bytes)
                
                try:
                    patoolib.extract_archive(str(zip_path), outdir=str(Path(tmpdir) / "test"))
                    return {
                        "valid": True,
                        "size_mb": size_mb,
                        "filename": zip_input.filename,
                    }
                except Exception as e:
                    return {
                        "valid": False,
                        "error": f"Invalid archive: {e}",
                        "size_mb": size_mb,
                    }
        
        except Exception as e:
            return {
                "valid": False,
                "error": f"Invalid base64 content: {e}",
            }


def analyze_zip_file(zip_input: ZipInput, max_size_mb: int = 100) -> ProjectInfo:
    """Convenience function to analyze a zip file"""
    analyzer = ZipAnalyzer(max_size_mb)
    return analyzer.analyze(zip_input)


def validate_zip_file(zip_input: ZipInput, max_size_mb: int = 100) -> dict:
    """Convenience function to validate a zip file"""
    validator = ZipValidator(max_size_mb)
    return validator.validate(zip_input)