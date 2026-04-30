"""
Public package interface for the EPL scraper.
"""

from .config import ScraperConfig
from .models import TeamData
from .parser import TableParser
from .scraper import FBrefScraper

__all__ = [
    "ScraperConfig",
    "TeamData",
    "TableParser",
    "FBrefScraper",
]
