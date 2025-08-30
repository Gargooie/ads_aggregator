"""
Модуль клиентов рекламных платформ.
"""

from .base_client import BaseAdsClient
from .meta_ads_client import MetaAdsClient
from .google_ads_client import GoogleAdsClient

__all__ = ["BaseAdsClient", "MetaAdsClient", "GoogleAdsClient"]
