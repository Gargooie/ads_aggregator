import time
import random
from typing import List, Dict, Optional
from datetime import datetime, date
from .base_client import BaseAdsClient
from ..exceptions import AuthenticationError, RateLimitError, DataNotFoundError, InvalidTokenError


class GoogleAdsClient(BaseAdsClient):
    """
    Клиент для работы с Google Ads API.

    Использует Google Ads Python Client Library для получения данных.
    """

    def __init__(self, credentials: Dict[str, str]):
        """
        Инициализация Google Ads клиента.

        Args:
            credentials: Словарь с ключами:
                - developer_token: Токен разработчика
                - client_id: OAuth2 Client ID
                - client_secret: OAuth2 Client Secret
                - refresh_token: OAuth2 Refresh Token
                - customer_id: ID рекламного аккаунта
        """
        super().__init__(credentials)
        self.developer_token = credentials.get('developer_token')
        self.client_id = credentials.get('client_id')
        self.client_secret = credentials.get('client_secret')
        self.refresh_token = credentials.get('refresh_token')
        self.customer_id = credentials.get('customer_id')

        # Валидация обязательных параметров
        required_fields = [
            self.developer_token, self.client_id, 
            self.client_secret, self.refresh_token, self.customer_id
        ]
        if not all(required_fields):
            raise InvalidTokenError("Отсутствуют обязательные параметры для Google Ads API")

    def _get_platform_name(self) -> str:
        return "google"

    def fetch_campaigns(self, start_date: date, end_date: date) -> List[Dict]:
        """
        Получает кампании из Google Ads API.

        В реальной реализации используется Google Ads Client:
        from google.ads.googleads.client import GoogleAdsClient

        GAQL запрос:
        SELECT campaign.id, campaign.name, metrics.impressions, 
               metrics.clicks, metrics.cost_micros
        FROM campaign 
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'

        Args:
            start_date: Дата начала
            end_date: Дата окончания

        Returns:
            Список кампаний с метриками
        """
        self._validate_date_range(start_date, end_date)

        try:
            # Имитируем возможные ошибки API
            if random.random() < 0.1:  # 10% вероятность ошибки токена
                raise AuthenticationError("Неверный developer token Google Ads")

            if random.random() < 0.05:  # 5% вероятность quota exceeded
                raise RateLimitError("Превышена квота запросов Google Ads API")

            # Симуляция задержки API
            time.sleep(0.1)

            # Мок данные кампаний
            campaigns = []
            for i in range(4):  # 4 кампании для примера
                # Google Ads возвращает cost в микро-долларах (умножить на 1,000,000)
                cost_micros = random.randint(50000000, 500000000)  # 50-500 долларов
                spend = cost_micros / 1000000  # Конвертируем в доллары

                campaign = {
                    "campaign_id": f"google_campaign_{i+1}",
                    "name": f"Google Campaign {i+1}",
                    "impressions": random.randint(1500, 12000),
                    "clicks": random.randint(75, 600),
                    "spend": round(spend, 2)
                }
                campaigns.append(campaign)

            return campaigns

        except Exception as e:
            if isinstance(e, (AuthenticationError, RateLimitError)):
                raise
            raise DataNotFoundError(f"Ошибка получения кампаний Google: {str(e)}")

    def fetch_ads(self, campaign_id: str, start_date: date, end_date: date) -> List[Dict]:
        """
        Получает объявления для кампании из Google Ads API.

        В реальной реализации GAQL запрос:
        SELECT ad_group_ad.ad.id, ad_group_ad.ad.name, 
               metrics.impressions, metrics.clicks, metrics.cost_micros
        FROM ad_group_ad 
        WHERE campaign.id = {campaign_id}
        AND segments.date BETWEEN '{start_date}' AND '{end_date}'

        Args:
            campaign_id: ID кампании
            start_date: Дата начала
            end_date: Дата окончания

        Returns:
            Список объявлений с метриками и рассчитанными CTR/CPC
        """
        self._validate_date_range(start_date, end_date)

        try:
            # Имитация ошибок API
            if random.random() < 0.1:
                raise AuthenticationError("Refresh token истек")

            # Симуляция задержки API
            time.sleep(0.1)

            # Мок данные объявлений
            ads = []
            num_ads = random.randint(2, 6)  # 2-6 объявлений на кампанию

            for i in range(num_ads):
                impressions = random.randint(400, 4000)
                clicks = random.randint(15, impressions // 8)
                cost_micros = random.randint(10000000, 100000000)  # 10-100 долларов
                spend = round(cost_micros / 1000000, 2)

                ad = {
                    "ad_id": f"{campaign_id}_ad_{i+1}",
                    "ad_name": f"Google Ad {i+1}",
                    "impressions": impressions,
                    "clicks": clicks,
                    "spend": spend,
                    "ctr": self._calculate_ctr(impressions, clicks),
                    "cpc": self._calculate_cpc(spend, clicks)
                }
                ads.append(ad)

            return ads

        except Exception as e:
            if isinstance(e, AuthenticationError):
                raise
            raise DataNotFoundError(f"Ошибка получения объявлений Google: {str(e)}")

    def _build_gaql_query(self, query_type: str, **kwargs) -> str:
        """
        Строит GAQL запрос для Google Ads API.

        Args:
            query_type: Тип запроса ('campaigns' или 'ads')
            **kwargs: Дополнительные параметры

        Returns:
            GAQL запрос как строка
        """
        if query_type == "campaigns":
            return f"""
                SELECT 
                    campaign.id,
                    campaign.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros
                FROM campaign 
                WHERE segments.date BETWEEN '{kwargs.get('start_date')}' AND '{kwargs.get('end_date')}'
                ORDER BY campaign.id
            """
        elif query_type == "ads":
            return f"""
                SELECT 
                    ad_group_ad.ad.id,
                    ad_group_ad.ad.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros
                FROM ad_group_ad 
                WHERE campaign.id = {kwargs.get('campaign_id')}
                AND segments.date BETWEEN '{kwargs.get('start_date')}' AND '{kwargs.get('end_date')}'
                ORDER BY ad_group_ad.ad.id
            """
        else:
            raise ValueError(f"Неизвестный тип запроса: {query_type}")
