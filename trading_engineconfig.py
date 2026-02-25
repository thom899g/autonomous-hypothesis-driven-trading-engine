"""
Configuration management for the Autonomous Hypothesis-Driven Trading Engine.
Centralizes all configuration with environment variable fallbacks and type validation.
"""
import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path
import json
from datetime import timedelta

@dataclass
class FirebaseConfig:
    """Firebase configuration with validation."""
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    token_uri: str = "https://oauth2.googleapis.com/token"
    
    @classmethod
    def from_env(cls) -> Optional['FirebaseConfig']:
        """Initialize from environment variables."""
        try:
            return cls(
                project_id=os.getenv('FIREBASE_PROJECT_ID', ''),
                private_key_id=os.getenv('FIREBASE_PRIVATE_KEY_ID', ''),
                private_key=os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                client_email=os.getenv('FIREBASE_CLIENT_EMAIL', '')
            )
        except Exception as e:
            print(f"Failed to load Firebase config: {e}")
            return None

@dataclass
class ExchangeConfig:
    """Exchange API configuration."""
    name: str = 'binance'
    api_key: str = ''
    api_secret: str = ''
    testnet: bool = True
    rate_limit: int = 10  # requests per second
    
    @classmethod
    def from_env(cls) -> 'ExchangeConfig':
        """Initialize from environment variables."""
        return cls(
            api_key=os.getenv('EXCHANGE_API_KEY', ''),
            api_secret=os.getenv('EXCHANGE_API_SECRET', '')
        )

@dataclass
class TradingConfig:
    """Trading parameters and limits."""
    initial_capital: float = 10000.0
    max_position_size: float = 0.1  # 10% of capital
    max_daily_loss: float = 0.02  # 2%
    min_confidence_threshold: float = 0.65
    max_open_positions: int = 5
    slippage_tolerance: float = 0.001  # 0.1%

@dataclass
class HypothesisConfig:
    """Hypothesis generation and testing parameters."""
    lookback_periods: list[int] = (60, 240, 1440)  # 1h, 4h, 1d in minutes
    min_test_period: int = 100  # bars
    max_hypotheses_per_cycle: int = 50
    hypothesis_timeout: int = 300  # seconds
    backtest_warmup: int = 1000  # bars

@dataclass
class ModelConfig:
    """Machine learning model parameters."""
    feature_window: int = 50
    target_horizon: int = 5
    train_test_split: float = 0.8
    min_training_samples: int = 1000
    model_retrain_interval: int = 100  # trades

class Config:
    """Main configuration class."""
    
    def __init__(self):
        self.firebase = FirebaseConfig.from_env()
        self.exchange = ExchangeConfig.from_env()
        self.trading = TradingConfig()
        self.hypothesis = HypothesisConfig()
        self.model = ModelConfig()
        
        # Runtime configurations
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.data_cache_ttl = timedelta(minutes=5)
        self.hypothesis_cache_size = 1000
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
        
        # File paths
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / 'data'
        self.models_dir = self.base_dir / 'models'
        self.logs_dir = self.base_dir / 'logs'
        
        self._validate()
        self._create_directories()
    
    def _validate(self) -> None:
        """Validate configuration."""
        if not self.firebase:
            raise ValueError("Firebase configuration is required")
        if not self.exchange.api_key or not self.exchange.api_secret:
            print("WARNING: Exchange API credentials not set - using paper trading mode")
        if self.trading.initial_capital <= 0:
            raise ValueError("Initial capital must be positive")
    
    def _create_directories(self) -> None:
        """Create necessary directories."""
        self.data_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary (without secrets)."""
        return {
            'exchange': {'name': self.exchange.name, 'testnet': self.exchange.testnet},
            'trading': self.trading.__dict__,
            'hypothesis': self.hypothesis.__dict__,
            'model': self.model.__dict__
        }

# Global config instance
config = Config()