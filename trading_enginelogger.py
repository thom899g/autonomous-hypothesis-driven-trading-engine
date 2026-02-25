"""
Production logging system with structured logging and Firebase integration.
"""
import logging
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from typing import Dict, Any, Optional
import json
from pathlib import Path

from .config import config
from .firebase_client import FirebaseClient

class StructuredFormatter(logging.Formatter):
    """JSON-structured log formatter for machine readability."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'module':