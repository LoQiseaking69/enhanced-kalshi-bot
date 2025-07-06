"""
Enhanced Configuration Management for Kalshi Trading Bot

This module provides comprehensive configuration management with environment-based
settings, validation, and dynamic configuration updates.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class TradingConfig:
    """Trading strategy configuration"""
    bankroll: float = 10000.0
    max_position_size_percentage: float = 0.10
    stop_loss_percentage: float = 0.05
    take_profit_percentage: float = 0.15
    max_daily_loss_percentage: float = 0.02
    max_open_positions: int = 10
    correlation_limit: float = 0.7
    trade_interval_seconds: int = 60
    min_confidence_threshold: float = 0.6
    
@dataclass
class MLConfig:
    """Machine Learning model configuration"""
    sentiment_model_path: str = "models/sentiment_model"
    price_prediction_model_path: str = "models/price_prediction"
    ensemble_weights: Dict[str, float] = field(default_factory=lambda: {
        "sentiment": 0.3,
        "technical": 0.4,
        "fundamental": 0.3
    })
    retrain_interval_hours: int = 24
    min_training_samples: int = 1000
    feature_importance_threshold: float = 0.05
    
@dataclass
class DataConfig:
    """Data ingestion and processing configuration"""
    news_sources: List[str] = field(default_factory=lambda: [
        "reuters", "bloomberg", "ap-news", "cnn", "bbc-news"
    ])
    social_media_sources: List[str] = field(default_factory=lambda: [
        "twitter", "reddit"
    ])
    update_frequency_minutes: int = 5
    data_retention_days: int = 90
    cache_ttl_seconds: int = 300
    
@dataclass
class APIConfig:
    """API and external service configuration"""
    kalshi_api_key: str = ""
    kalshi_api_url: str = "https://trading-api.kalshi.com/trade-api/v2"
    news_api_key: str = ""
    twitter_bearer_token: str = ""
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    rate_limit_requests_per_minute: int = 60
    timeout_seconds: int = 30
    
@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = "postgresql://user:password@localhost:5432/kalshi_bot"
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
@dataclass
class RedisConfig:
    """Redis cache configuration"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    socket_timeout: int = 5
    
@dataclass
class TelegramConfig:
    """Telegram bot configuration"""
    bot_token: str = ""
    chat_id: str = ""
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    
@dataclass
class SecurityConfig:
    """Security and authentication configuration"""
    jwt_secret_key: str = ""
    jwt_access_token_expires_hours: int = 24
    api_key_length: int = 32
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    
@dataclass
class MonitoringConfig:
    """Monitoring and alerting configuration"""
    prometheus_port: int = 8000
    log_level: str = "INFO"
    sentry_dsn: Optional[str] = None
    alert_email: Optional[str] = None
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "daily_loss": 0.02,
        "position_loss": 0.10,
        "api_error_rate": 0.05
    })

class ConfigManager:
    """
    Centralized configuration management with environment variable support,
    validation, and dynamic updates.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or os.getenv("CONFIG_FILE", "config/config.json")
        self.logger = logging.getLogger(__name__)
        
        # Initialize configurations
        self.trading = TradingConfig()
        self.ml = MLConfig()
        self.data = DataConfig()
        self.api = APIConfig()
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.telegram = TelegramConfig()
        self.security = SecurityConfig()
        self.monitoring = MonitoringConfig()
        
        self._load_from_environment()
        self._load_from_file()
        self._validate_config()
        
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        # Trading configuration
        self.trading.bankroll = float(os.getenv("BANKROLL", self.trading.bankroll))
        self.trading.max_position_size_percentage = float(
            os.getenv("MAX_POSITION_SIZE_PERCENTAGE", self.trading.max_position_size_percentage)
        )
        self.trading.stop_loss_percentage = float(
            os.getenv("STOP_LOSS_PERCENTAGE", self.trading.stop_loss_percentage)
        )
        
        # API configuration
        self.api.kalshi_api_key = os.getenv("KALSHI_API_KEY", "")
        self.api.news_api_key = os.getenv("NEWS_API_KEY", "")
        self.api.twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN", "")
        
        # Database configuration
        self.database.url = os.getenv("DATABASE_URL", self.database.url)
        
        # Redis configuration
        self.redis.host = os.getenv("REDIS_HOST", self.redis.host)
        self.redis.port = int(os.getenv("REDIS_PORT", self.redis.port))
        self.redis.password = os.getenv("REDIS_PASSWORD")
        
        # Telegram configuration
        self.telegram.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram.chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        
        # Security configuration
        self.security.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "")
        
        # Monitoring configuration
        self.monitoring.log_level = os.getenv("LOG_LEVEL", self.monitoring.log_level)
        self.monitoring.sentry_dsn = os.getenv("SENTRY_DSN")
        
    def _load_from_file(self):
        """Load configuration from JSON file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    
                # Update configurations from file
                for section, data in config_data.items():
                    if hasattr(self, section):
                        config_obj = getattr(self, section)
                        for key, value in data.items():
                            if hasattr(config_obj, key):
                                setattr(config_obj, key, value)
                                
            except Exception as e:
                self.logger.warning(f"Failed to load config file {self.config_file}: {e}")
                
    def _validate_config(self):
        """Validate configuration values"""
        errors = []
        
        # Validate trading configuration
        if self.trading.bankroll <= 0:
            errors.append("Bankroll must be positive")
            
        if not 0 < self.trading.max_position_size_percentage <= 1:
            errors.append("Max position size percentage must be between 0 and 1")
            
        if not 0 < self.trading.stop_loss_percentage <= 1:
            errors.append("Stop loss percentage must be between 0 and 1")
            
        # Validate API keys
        if not self.api.kalshi_api_key:
            errors.append("Kalshi API key is required")
            
        if not self.telegram.bot_token:
            errors.append("Telegram bot token is required")
            
        if not self.security.jwt_secret_key:
            errors.append("JWT secret key is required")
            
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
            
    def save_to_file(self, file_path: Optional[str] = None):
        """Save current configuration to file"""
        file_path = file_path or self.config_file
        
        config_data = {
            "trading": self.trading.__dict__,
            "ml": self.ml.__dict__,
            "data": self.data.__dict__,
            "api": {k: v for k, v in self.api.__dict__.items() if not k.endswith("_key") and not k.endswith("_token")},
            "database": {k: v for k, v in self.database.__dict__.items() if k != "url"},
            "redis": {k: v for k, v in self.redis.__dict__.items() if k != "password"},
            "telegram": {k: v for k, v in self.telegram.__dict__.items() if not k.endswith("_token")},
            "security": {k: v for k, v in self.security.__dict__.items() if not k.endswith("_key")},
            "monitoring": self.monitoring.__dict__
        }
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(config_data, f, indent=2)
            
    def update_config(self, section: str, updates: Dict[str, Any]):
        """Update configuration section with new values"""
        if not hasattr(self, section):
            raise ValueError(f"Unknown configuration section: {section}")
            
        config_obj = getattr(self, section)
        for key, value in updates.items():
            if hasattr(config_obj, key):
                setattr(config_obj, key, value)
            else:
                self.logger.warning(f"Unknown configuration key: {section}.{key}")
                
        self._validate_config()
        
    def get_config_dict(self) -> Dict[str, Any]:
        """Get complete configuration as dictionary"""
        return {
            "trading": self.trading.__dict__,
            "ml": self.ml.__dict__,
            "data": self.data.__dict__,
            "api": self.api.__dict__,
            "database": self.database.__dict__,
            "redis": self.redis.__dict__,
            "telegram": self.telegram.__dict__,
            "security": self.security.__dict__,
            "monitoring": self.monitoring.__dict__
        }

# Global configuration instance
config = ConfigManager()

# Convenience functions for accessing configuration
def get_trading_config() -> TradingConfig:
    return config.trading

def get_ml_config() -> MLConfig:
    return config.ml

def get_data_config() -> DataConfig:
    return config.data

def get_api_config() -> APIConfig:
    return config.api

def get_database_config() -> DatabaseConfig:
    return config.database

def get_redis_config() -> RedisConfig:
    return config.redis

def get_telegram_config() -> TelegramConfig:
    return config.telegram

def get_security_config() -> SecurityConfig:
    return config.security

def get_monitoring_config() -> MonitoringConfig:
    return config.monitoring

