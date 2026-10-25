"""Language and framework detection module"""
from .detector import LanguageDetector, detect_project, DetectionSignal

__all__ = ["LanguageDetector", "detect_project", "DetectionSignal"]