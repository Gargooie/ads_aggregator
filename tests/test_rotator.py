import unittest
from ads_aggregator.rotator import CreativeRotator, RotationStrategy


class TestCreativeRotator(unittest.TestCase):
    """Тесты для класса CreativeRotator."""

    def setUp(self):
        """Подготовка тестовых данных."""
        self.test_creatives = [
            {
                "ad_id": "ad_1",
                "ad_name": "Creative A",
                "impressions": 1000,
                "clicks": 50,
                "spend": 25.0,
                "ctr": 5.0,
                "cpc": 0.5
            },
            {
                "ad_id": "ad_2", 
                "ad_name": "Creative B",
                "impressions": 2000,
                "clicks": 40,
                "spend": 20.0,
                "ctr": 2.0,
                "cpc": 0.5
            },
            {
                "ad_id": "ad_3",
                "ad_name": "Creative C", 
                "impressions": 500,
                "clicks": 25,
                "spend": 12.5,
                "ctr": 5.0,
                "cpc": 0.5
            }
        ]

    def test_rotator_initialization(self):
        """Тест инициализации ротатора."""
        rotator = CreativeRotator(self.test_creatives)
        self.assertEqual(len(rotator.creatives), 3)
        self.assertEqual(rotator._round_robin_index, 0)

    def test_empty_creatives_validation(self):
        """Тест валидации пустого списка креативов."""
        with self.assertRaises(ValueError):
            CreativeRotator([])

    def test_missing_required_fields(self):
        """Тест валидации отсутствующих обязательных полей."""
        invalid_creative = [{"ad_id": "test", "ad_name": "Test"}]  # Отсутствуют другие поля

        with self.assertRaises(ValueError):
            CreativeRotator(invalid_creative)

    def test_automatic_metrics_calculation(self):
        """Тест автоматического расчета CTR и CPC."""
        creatives_without_metrics = [
            {
                "ad_id": "ad_1",
                "ad_name": "Creative A",
                "impressions": 1000,
                "clicks": 50,
                "spend": 25.0
                # Отсутствуют ctr и cpc
            }
        ]

        rotator = CreativeRotator(creatives_without_metrics)
        creative = rotator.creatives[0]

        # CTR должен быть рассчитан как (50/1000)*100 = 5.0
        self.assertEqual(creative['ctr'], 5.0)

        # CPC должен быть рассчитан как 25.0/50 = 0.5
        self.assertEqual(creative['cpc'], 0.5)

    def test_round_robin_strategy(self):
        """Тест стратегии round_robin."""
        rotator = CreativeRotator(self.test_creatives)

        # Первый выбор должен быть ad_1
        first_choice = rotator.choose_next("round_robin")
        self.assertEqual(first_choice['ad_id'], "ad_1")

        # Второй выбор должен быть ad_2
        second_choice = rotator.choose_next("round_robin")
        self.assertEqual(second_choice['ad_id'], "ad_2")

        # Третий выбор должен быть ad_3
        third_choice = rotator.choose_next("round_robin")
        self.assertEqual(third_choice['ad_id'], "ad_3")

        # Четвертый выбор должен снова быть ad_1 (цикл)
        fourth_choice = rotator.choose_next("round_robin")
        self.assertEqual(fourth_choice['ad_id'], "ad_1")

    def test_best_ctr_strategy(self):
        """Тест стратегии best_ctr."""
        rotator = CreativeRotator(self.test_creatives)

        # У Creative A и Creative C CTR = 5.0 (максимальный)
        # Должен вернуться один из них (первый найденный)
        best_ctr_choice = rotator.choose_next("best_ctr")
        self.assertIn(best_ctr_choice['ad_id'], ["ad_1", "ad_3"])
        self.assertEqual(best_ctr_choice['ctr'], 5.0)

    def test_lowest_cpc_strategy(self):
        """Тест стратегии lowest_cpc."""
        rotator = CreativeRotator(self.test_creatives)

        # У всех креативов CPC = 0.5, должен вернуться первый найденный
        lowest_cpc_choice = rotator.choose_next("lowest_cpc")
        self.assertEqual(lowest_cpc_choice['cpc'], 0.5)

    def test_ctr_calculation(self):
        """Тест правильности расчета CTR."""
        # CTR = (clicks / impressions) * 100
        impressions = 1000
        clicks = 75
        expected_ctr = (clicks / impressions) * 100  # 7.5%

        test_creative = [{
            "ad_id": "test",
            "ad_name": "Test Creative",
            "impressions": impressions,
            "clicks": clicks,
            "spend": 50.0
        }]

        rotator = CreativeRotator(test_creative)
        self.assertEqual(rotator.creatives[0]['ctr'], expected_ctr)

    def test_cpc_calculation(self):
        """Тест правильности расчета CPC."""
        # CPC = spend / clicks
        spend = 100.0
        clicks = 25
        expected_cpc = spend / clicks  # 4.0

        test_creative = [{
            "ad_id": "test",
            "ad_name": "Test Creative",
            "impressions": 1000,
            "clicks": clicks,
            "spend": spend
        }]

        rotator = CreativeRotator(test_creative)
        self.assertEqual(rotator.creatives[0]['cpc'], expected_cpc)

    def test_zero_impressions_ctr(self):
        """Тест расчета CTR при нулевых показах."""
        test_creative = [{
            "ad_id": "test",
            "ad_name": "Test Creative",
            "impressions": 0,
            "clicks": 0,
            "spend": 0.0
        }]

        rotator = CreativeRotator(test_creative)
        self.assertEqual(rotator.creatives[0]['ctr'], 0.0)

    def test_zero_clicks_cpc(self):
        """Тест расчета CPC при нулевых кликах."""
        test_creative = [{
            "ad_id": "test",
            "ad_name": "Test Creative",
            "impressions": 1000,
            "clicks": 0,
            "spend": 10.0
        }]

        rotator = CreativeRotator(test_creative)
        # При нулевых кликах CPC должен быть inf
        self.assertEqual(rotator.creatives[0]['cpc'], float('inf'))

    def test_rotation_stats(self):
        """Тест получения статистики ротации."""
        rotator = CreativeRotator(self.test_creatives)
        stats = rotator.get_rotation_stats()

        # Проверяем основные поля статистики
        self.assertEqual(stats['total_creatives'], 3)
        self.assertEqual(stats['total_impressions'], 3500)  # 1000+2000+500
        self.assertEqual(stats['total_clicks'], 115)        # 50+40+25
        self.assertEqual(stats['total_spend'], 57.5)        # 25+20+12.5

        # Проверяем наличие информации о лучших креативах
        self.assertIn('best_performing', stats)
        self.assertIn('worst_performing', stats)

    def test_add_creative(self):
        """Тест добавления креатива."""
        rotator = CreativeRotator(self.test_creatives)
        initial_count = len(rotator.creatives)

        new_creative = {
            "ad_id": "ad_4",
            "ad_name": "Creative D",
            "impressions": 800,
            "clicks": 32,
            "spend": 16.0
        }

        rotator.add_creative(new_creative)

        self.assertEqual(len(rotator.creatives), initial_count + 1)
        self.assertEqual(rotator.creatives[-1]['ad_id'], "ad_4")
        self.assertEqual(rotator.creatives[-1]['ctr'], 4.0)  # (32/800)*100

    def test_remove_creative(self):
        """Тест удаления креатива."""
        rotator = CreativeRotator(self.test_creatives)
        initial_count = len(rotator.creatives)

        # Удаляем существующий креатив
        result = rotator.remove_creative("ad_2")

        self.assertTrue(result)
        self.assertEqual(len(rotator.creatives), initial_count - 1)

        # Проверяем что креатив действительно удален
        ad_ids = [c['ad_id'] for c in rotator.creatives]
        self.assertNotIn("ad_2", ad_ids)

        # Пытаемся удалить несуществующий креатив
        result = rotator.remove_creative("nonexistent")
        self.assertFalse(result)

    def test_simulation(self):
        """Тест симуляции ротации."""
        rotator = CreativeRotator(self.test_creatives)

        # Тестируем симуляцию на 5 итераций
        simulation = rotator.simulate_rotation(5, "round_robin")

        self.assertEqual(len(simulation), 5)

        # Проверяем структуру каждой итерации
        for i, iteration in enumerate(simulation):
            self.assertEqual(iteration['iteration'], i + 1)
            self.assertIn('chosen_creative', iteration)
            self.assertIn('ad_id', iteration['chosen_creative'])

    def test_invalid_strategy(self):
        """Тест обработки неверной стратегии."""
        rotator = CreativeRotator(self.test_creatives)

        with self.assertRaises(ValueError):
            rotator.choose_next("invalid_strategy")

    def test_reset_round_robin(self):
        """Тест сброса индекса round_robin."""
        rotator = CreativeRotator(self.test_creatives)

        # Делаем несколько выборов
        rotator.choose_next("round_robin")
        rotator.choose_next("round_robin")

        # Индекс должен быть 2
        self.assertEqual(rotator._round_robin_index, 2)

        # Сбрасываем
        rotator.reset_round_robin()
        self.assertEqual(rotator._round_robin_index, 0)

        # Следующий выбор должен быть первый креатив
        choice = rotator.choose_next("round_robin")
        self.assertEqual(choice['ad_id'], "ad_1")


if __name__ == '__main__':
    unittest.main()
