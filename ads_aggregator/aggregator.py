import json
from typing import List, Dict, Optional
from datetime import date
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from .clients.base_client import BaseAdsClient
from .exceptions import AdsAPIError


class AdsAggregator:
    """
    Агрегатор для объединения рекламных данных из различных платформ.

    Принимает список клиентов рекламных платформ и возвращает 
    унифицированный JSON с данными по кампаниям и креативам.
    """

    def __init__(self, clients: List[BaseAdsClient]):
        """
        Инициализация агрегатора.

        Args:
            clients: Список экземпляров клиентов рекламных платформ
        """
        self.clients = clients
        self.logger = logging.getLogger(__name__)

    def aggregate_data(self, start_date: date, end_date: date, 
                      parallel: bool = True) -> List[Dict]:
        """
        Агрегирует данные со всех подключенных платформ.

        Args:
            start_date: Дата начала периода
            end_date: Дата окончания периода
            parallel: Использовать ли параллельные запросы

        Returns:
            Список объединенных данных в формате JSON

        Raises:
            AdsAPIError: При критических ошибках API
        """
        all_data = []

        if parallel and len(self.clients) > 1:
            # Параллельная обработка для ускорения запросов
            with ThreadPoolExecutor(max_workers=min(len(self.clients), 4)) as executor:
                future_to_client = {
                    executor.submit(self._fetch_client_data, client, start_date, end_date): client
                    for client in self.clients
                }

                for future in as_completed(future_to_client):
                    client = future_to_client[future]
                    try:
                        platform_data = future.result()
                        all_data.extend(platform_data)
                        self.logger.info(f"Успешно получены данные из {client.platform_name}")
                    except Exception as e:
                        self.logger.error(f"Ошибка получения данных из {client.platform_name}: {e}")
                        # Продолжаем с другими платформами
                        continue
        else:
            # Последовательная обработка
            for client in self.clients:
                try:
                    platform_data = self._fetch_client_data(client, start_date, end_date)
                    all_data.extend(platform_data)
                    self.logger.info(f"Успешно получены данные из {client.platform_name}")
                except Exception as e:
                    self.logger.error(f"Ошибка получения данных из {client.platform_name}: {e}")
                    continue

        return all_data

    def _fetch_client_data(self, client: BaseAdsClient, 
                          start_date: date, end_date: date) -> List[Dict]:
        """
        Получает и форматирует данные от одного клиента.

        Args:
            client: Экземпляр клиента платформы
            start_date: Дата начала
            end_date: Дата окончания

        Returns:
            Форматированные данные кампаний с объявлениями
        """
        platform_data = []

        # Получаем кампании
        campaigns = client.fetch_campaigns(start_date, end_date)

        for campaign in campaigns:
            # Получаем объявления для каждой кампании
            try:
                ads = client.fetch_ads(campaign['campaign_id'], start_date, end_date)

                # Формируем унифицированную структуру данных
                formatted_campaign = {
                    "platform": client.platform_name,
                    "campaign_id": campaign['campaign_id'],
                    "name": campaign['name'],
                    "impressions": campaign['impressions'],
                    "clicks": campaign['clicks'],
                    "spend": campaign['spend'],
                    "ads": ads
                }

                platform_data.append(formatted_campaign)

            except Exception as e:
                self.logger.error(
                    f"Ошибка получения объявлений для кампании {campaign['campaign_id']}: {e}"
                )
                # Добавляем кампанию без объявлений
                formatted_campaign = {
                    "platform": client.platform_name,
                    "campaign_id": campaign['campaign_id'],
                    "name": campaign['name'],
                    "impressions": campaign['impressions'],
                    "clicks": campaign['clicks'],
                    "spend": campaign['spend'],
                    "ads": []
                }
                platform_data.append(formatted_campaign)

        return platform_data

    def to_json(self, data: List[Dict], pretty: bool = True) -> str:
        """
        Преобразует агрегированные данные в JSON.

        Args:
            data: Агрегированные данные
            pretty: Форматировать ли JSON для читаемости

        Returns:
            JSON строка
        """
        if pretty:
            return json.dumps(data, indent=2, ensure_ascii=False)
        return json.dumps(data, ensure_ascii=False)

    def get_summary_stats(self, data: List[Dict]) -> Dict:
        """
        Возвращает сводную статистику по всем платформам.

        Args:
            data: Агрегированные данные

        Returns:
            Словарь со сводной статистикой
        """
        stats = {
            "total_platforms": len(set(campaign['platform'] for campaign in data)),
            "total_campaigns": len(data),
            "total_ads": sum(len(campaign['ads']) for campaign in data),
            "platform_breakdown": {},
            "totals": {
                "impressions": 0,
                "clicks": 0,
                "spend": 0.0
            }
        }

        # Подсчет по платформам
        for campaign in data:
            platform = campaign['platform']
            if platform not in stats['platform_breakdown']:
                stats['platform_breakdown'][platform] = {
                    "campaigns": 0,
                    "ads": 0,
                    "impressions": 0,
                    "clicks": 0,
                    "spend": 0.0
                }

            stats['platform_breakdown'][platform]['campaigns'] += 1
            stats['platform_breakdown'][platform]['ads'] += len(campaign['ads'])
            stats['platform_breakdown'][platform]['impressions'] += campaign['impressions']
            stats['platform_breakdown'][platform]['clicks'] += campaign['clicks']
            stats['platform_breakdown'][platform]['spend'] += campaign['spend']

            # Общие итоги
            stats['totals']['impressions'] += campaign['impressions']
            stats['totals']['clicks'] += campaign['clicks']
            stats['totals']['spend'] += campaign['spend']

        # Округляем spend
        stats['totals']['spend'] = round(stats['totals']['spend'], 2)
        for platform in stats['platform_breakdown']:
            stats['platform_breakdown'][platform]['spend'] = round(
                stats['platform_breakdown'][platform]['spend'], 2
            )

        return stats

    def filter_by_platform(self, data: List[Dict], platform: str) -> List[Dict]:
        """
        Фильтрует данные по конкретной платформе.

        Args:
            data: Агрегированные данные
            platform: Название платформы для фильтрации

        Returns:
            Отфильтрованные данные
        """
        return [campaign for campaign in data if campaign['platform'] == platform]

    def filter_by_spend_threshold(self, data: List[Dict], min_spend: float) -> List[Dict]:
        """
        Фильтрует кампании по минимальному расходу.

        Args:
            data: Агрегированные данные
            min_spend: Минимальная сумма расходов

        Returns:
            Отфильтрованные данные
        """
        return [campaign for campaign in data if campaign['spend'] >= min_spend]
