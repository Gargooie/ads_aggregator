"""
Система агрегации рекламных данных из различных источников.

Основные компоненты:
- BaseAdsClient: базовый класс для клиентов рекламных платформ
- MetaAdsClient: клиент для Meta Ads API
- GoogleAdsClient: клиент для Google Ads API  
- AdsAggregator: агрегатор данных
- CreativeRotator: система ротации креативов
"""

__version__ = "1.0.0"
__author__ = "Python Backend Developer"
__email__ = "developer@example.com"

# Основные классы для импорта
from .aggregator import AdsAggregator
from .rotator import CreativeRotator, RotationStrategy
from .exceptions import (
    AdsAPIError,
    AuthenticationError, 
    RateLimitError,
    DataNotFoundError,
    InvalidTokenError
)

# Клиенты
from .clients.base_client import BaseAdsClient
from .clients.meta_ads_client import MetaAdsClient
from .clients.google_ads_client import GoogleAdsClient

__all__ = [
    "AdsAggregator",
    "CreativeRotator", 
    "RotationStrategy",
    "BaseAdsClient",
    "MetaAdsClient",
    "GoogleAdsClient",
    "AdsAPIError",
    "AuthenticationError",
    "RateLimitError", 
    "DataNotFoundError",
    "InvalidTokenError"
]
