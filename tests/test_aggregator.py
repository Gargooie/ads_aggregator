import unittest
from unittest.mock import Mock, patch
from datetime import date
from ads_aggregator.aggregator import AdsAggregator
from ads_aggregator.clients.base_client import BaseAdsClient
from ads_aggregator.exceptions import AdsAPIError


class MockAdsClient(BaseAdsClient):
    """Мок-класс для тестирования агрегатора."""

    def __init__(self, platform_name="test", should_fail=False):
        self._platform_name = platform_name
        self.should_fail = should_fail
        super().__init__({"test": "credentials"})

    def _get_platform_name(self):
        return self._platform_name

    def fetch_campaigns(self, start_date, end_date):
        if self.should_fail:
            raise AdsAPIError("Мок ошибка API")

        return [
            {
                "campaign_id": f"{self._platform_name}_camp_1",
                "name": f"{self._platform_name} Campaign 1", 
                "impressions": 1000,
                "clicks": 50,
                "spend": 25.0
            }
        ]

    def fetch_ads(self, campaign_id, start_date, end_date):
        if self.should_fail:
            raise AdsAPIError("Мок ошибка API")

        return [
            {
                "ad_id": f"{campaign_id}_ad_1",
                "ad_name": "Test Ad 1",
                "impressions": 500,
                "clicks": 25,
                "spend": 12.5,
                "ctr": 5.0,
                "cpc": 0.5
            },
            {
                "ad_id": f"{campaign_id}_ad_2", 
                "ad_name": "Test Ad 2",
                "impressions": 500,
                "clicks": 25,
                "spend": 12.5,
                "ctr": 5.0,
                "cpc": 0.5
            }
        ]


class TestAdsAggregator(unittest.TestCase):
    """Тесты для класса AdsAggregator."""

    def setUp(self):
        """Подготовка тестовых данных."""
        self.mock_client1 = MockAdsClient("platform1")
        self.mock_client2 = MockAdsClient("platform2") 
        self.aggregator = AdsAggregator([self.mock_client1, self.mock_client2])

        self.start_date = date(2023, 1, 1)
        self.end_date = date(2023, 1, 31)

    def test_aggregator_initialization(self):
        """Тест инициализации агрегатора."""
        self.assertEqual(len(self.aggregator.clients), 2)
        self.assertEqual(self.aggregator.clients[0].platform_name, "platform1")
        self.assertEqual(self.aggregator.clients[1].platform_name, "platform2")

    def test_successful_aggregation(self):
        """Тест успешной агрегации данных."""
        data = self.aggregator.aggregate_data(self.start_date, self.end_date, parallel=False)

        # Должно быть 2 кампании (по одной с каждой платформы)
        self.assertEqual(len(data), 2)

        # Проверяем структуру данных
        for campaign in data:
            self.assertIn("platform", campaign)
            self.assertIn("campaign_id", campaign)
            self.assertIn("name", campaign)
            self.assertIn("impressions", campaign)
            self.assertIn("clicks", campaign)
            self.assertIn("spend", campaign)
            self.assertIn("ads", campaign)

            # У каждой кампании должно быть 2 объявления
            self.assertEqual(len(campaign["ads"]), 2)

    def test_aggregation_with_failing_client(self):
        """Тест агрегации при ошибке одного из клиентов."""
        failing_client = MockAdsClient("failing", should_fail=True)
        working_client = MockAdsClient("working") 

        aggregator = AdsAggregator([failing_client, working_client])
        data = aggregator.aggregate_data(self.start_date, self.end_date, parallel=False)

        # Должны получить данные только от работающего клиента
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["platform"], "working")

    def test_summary_stats(self):
        """Тест получения сводной статистики."""
        data = self.aggregator.aggregate_data(self.start_date, self.end_date, parallel=False)
        stats = self.aggregator.get_summary_stats(data)

        # Проверяем базовые показатели
        self.assertEqual(stats["total_platforms"], 2)
        self.assertEqual(stats["total_campaigns"], 2)
        self.assertEqual(stats["total_ads"], 4)  # 2 кампании * 2 объявления

        # Проверяем общие итоги
        self.assertEqual(stats["totals"]["impressions"], 2000)  # 1000 * 2
        self.assertEqual(stats["totals"]["clicks"], 100)       # 50 * 2
        self.assertEqual(stats["totals"]["spend"], 50.0)       # 25.0 * 2

        # Проверяем разбивку по платформам
        self.assertIn("platform1", stats["platform_breakdown"])
        self.assertIn("platform2", stats["platform_breakdown"])

    def test_json_export(self):
        """Тест экспорта в JSON."""
        data = self.aggregator.aggregate_data(self.start_date, self.end_date, parallel=False)

        # Тест обычного JSON
        json_str = self.aggregator.to_json(data, pretty=False)
        self.assertIsInstance(json_str, str)
        self.assertIn("platform", json_str)

        # Тест форматированного JSON
        pretty_json = self.aggregator.to_json(data, pretty=True)
        self.assertIsInstance(pretty_json, str)
        self.assertIn("\n", pretty_json)  # Форматированный JSON содержит переносы строк

    def test_platform_filtering(self):
        """Тест фильтрации по платформе."""
        data = self.aggregator.aggregate_data(self.start_date, self.end_date, parallel=False)

        # Фильтруем по platform1
        platform1_data = self.aggregator.filter_by_platform(data, "platform1")
        self.assertEqual(len(platform1_data), 1)
        self.assertEqual(platform1_data[0]["platform"], "platform1")

        # Фильтруем по несуществующей платформе
        empty_data = self.aggregator.filter_by_platform(data, "nonexistent")
        self.assertEqual(len(empty_data), 0)

    def test_spend_threshold_filtering(self):
        """Тест фильтрации по порогу расходов."""
        data = self.aggregator.aggregate_data(self.start_date, self.end_date, parallel=False)

        # Фильтруем кампании с расходами >= 20.0
        high_spend_data = self.aggregator.filter_by_spend_threshold(data, 20.0)
        self.assertEqual(len(high_spend_data), 2)  # Обе кампании имеют spend = 25.0

        # Фильтруем кампании с расходами >= 30.0
        very_high_spend_data = self.aggregator.filter_by_spend_threshold(data, 30.0)
        self.assertEqual(len(very_high_spend_data), 0)  # Ни одна кампания не имеет spend >= 30.0


if __name__ == '__main__':
    unittest.main()
