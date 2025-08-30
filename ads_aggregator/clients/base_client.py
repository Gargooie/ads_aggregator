from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime, date


class BaseAdsClient(ABC):
    """
    Абстрактный базовый класс для всех клиентов рекламных платформ.

    Определяет интерфейс для получения данных о кампаниях и объявлениях.
    """

    def __init__(self, credentials: Dict[str, str]):
        """
        Инициализация клиента.

        Args:
            credentials: Словарь с учетными данными для API
        """
        self.credentials = credentials
        self.platform_name = self._get_platform_name()

    @abstractmethod
    def _get_platform_name(self) -> str:
        """Возвращает название платформы."""
        pass

    @abstractmethod
    def fetch_campaigns(self, start_date: date, end_date: date) -> List[Dict]:
        """
        Получает список кампаний за заданный период.

        Args:
            start_date: Дата начала периода
            end_date: Дата окончания периода

        Returns:
            Список словарей с данными кампаний

        Raises:
            AdsAPIError: При ошибке запроса к API
        """
        pass

    @abstractmethod
    def fetch_ads(self, campaign_id: str, start_date: date, end_date: date) -> List[Dict]:
        """
        Получает список объявлений для кампании за заданный период.

        Args:
            campaign_id: ID кампании
            start_date: Дата начала периода
            end_date: Дата окончания периода

        Returns:
            Список словарей с данными объявлений

        Raises:
            AdsAPIError: При ошибке запроса к API
        """
        pass

    def _calculate_ctr(self, impressions: int, clicks: int) -> float:
        """Вычисляет CTR (Click Through Rate)."""
        if impressions == 0:
            return 0.0
        return round((clicks / impressions) * 100, 2)

    def _calculate_cpc(self, spend: float, clicks: int) -> float:
        """Вычисляет CPC (Cost Per Click)."""
        if clicks == 0:
            return 0.0
        return round(spend / clicks, 2)

    def _validate_date_range(self, start_date: date, end_date: date) -> None:
        """Валидирует диапазон дат."""
        if start_date > end_date:
            raise ValueError("start_date не может быть больше end_date")

        if start_date > date.today():
            raise ValueError("start_date не может быть в будущем")
