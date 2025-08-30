from typing import List, Dict, Optional
from enum import Enum
import random


class RotationStrategy(Enum):
    """Стратегии ротации креативов."""
    ROUND_ROBIN = "round_robin"
    BEST_CTR = "best_ctr"
    LOWEST_CPC = "lowest_cpc"


class CreativeRotator:
    """
    Класс для ротации креативов по заданным правилам.

    Поддерживает различные стратегии выбора следующего креатива:
    - round_robin: циклический перебор
    - best_ctr: креатив с максимальным CTR
    - lowest_cpc: креатив с минимальным CPC
    """

    def __init__(self, creatives: List[Dict]):
        """
        Инициализация ротатора.

        Args:
            creatives: Список креативов с их статистикой
                Каждый элемент должен содержать поля:
                - ad_id: уникальный ID
                - ad_name: название
                - impressions: показы
                - clicks: клики
                - spend: расходы
                - ctr: CTR (может быть вычислен автоматически)
                - cpc: CPC (может быть вычислен автоматически)
        """
        self.creatives = creatives
        self._round_robin_index = 0
        self._validate_creatives()
        self._ensure_metrics()

    def _validate_creatives(self) -> None:
        """Валидирует входные данные креативов."""
        if not self.creatives:
            raise ValueError("Список креативов не может быть пустым")

        required_fields = ['ad_id', 'ad_name', 'impressions', 'clicks', 'spend']
        for creative in self.creatives:
            for field in required_fields:
                if field not in creative:
                    raise ValueError(f"Отсутствует обязательное поле '{field}' в креативе")

    def _ensure_metrics(self) -> None:
        """Убеждается, что все метрики (CTR, CPC) рассчитаны."""
        for creative in self.creatives:
            # Рассчитываем CTR если отсутствует
            if 'ctr' not in creative:
                impressions = creative['impressions']
                clicks = creative['clicks']
                creative['ctr'] = (clicks / impressions * 100) if impressions > 0 else 0.0

            # Рассчитываем CPC если отсутствует
            if 'cpc' not in creative:
                spend = creative['spend']
                clicks = creative['clicks']
                creative['cpc'] = (spend / clicks) if clicks > 0 else float('inf')

    def choose_next(self, strategy: str = "round_robin") -> Dict:
        """
        Выбирает следующий креатив по заданной стратегии.

        Args:
            strategy: Стратегия ротации ("round_robin", "best_ctr", "lowest_cpc")

        Returns:
            Словарь с данными выбранного креатива

        Raises:
            ValueError: При неизвестной стратегии или отсутствии креативов
        """
        if not self.creatives:
            raise ValueError("Нет доступных креативов для ротации")

        strategy_enum = RotationStrategy(strategy)

        if strategy_enum == RotationStrategy.ROUND_ROBIN:
            return self._round_robin_choice()
        elif strategy_enum == RotationStrategy.BEST_CTR:
            return self._best_ctr_choice()
        elif strategy_enum == RotationStrategy.LOWEST_CPC:
            return self._lowest_cpc_choice()
        else:
            raise ValueError(f"Неизвестная стратегия ротации: {strategy}")

    def _round_robin_choice(self) -> Dict:
        """
        Циклический выбор креатива.

        Returns:
            Следующий креатив по порядку
        """
        creative = self.creatives[self._round_robin_index]
        self._round_robin_index = (self._round_robin_index + 1) % len(self.creatives)
        return creative.copy()

    def _best_ctr_choice(self) -> Dict:
        """
        Выбирает креатив с максимальным CTR.

        Returns:
            Креатив с наибольшим CTR
        """
        # Фильтруем креативы с показами > 0 для корректного CTR
        valid_creatives = [c for c in self.creatives if c['impressions'] > 0]

        if not valid_creatives:
            # Если нет креативов с показами, возвращаем случайный
            return random.choice(self.creatives).copy()

        best_creative = max(valid_creatives, key=lambda x: x['ctr'])
        return best_creative.copy()

    def _lowest_cpc_choice(self) -> Dict:
        """
        Выбирает креатив с минимальным CPC.

        Returns:
            Креатив с наименьшим CPC
        """
        # Фильтруем креативы с кликами > 0 для корректного CPC
        valid_creatives = [c for c in self.creatives if c['clicks'] > 0]

        if not valid_creatives:
            # Если нет креативов с кликами, возвращаем случайный
            return random.choice(self.creatives).copy()

        best_creative = min(valid_creatives, key=lambda x: x['cpc'])
        return best_creative.copy()

    def get_rotation_stats(self) -> Dict:
        """
        Возвращает статистику креативов для анализа ротации.

        Returns:
            Словарь со статистикой по креативам
        """
        total_impressions = sum(c['impressions'] for c in self.creatives)
        total_clicks = sum(c['clicks'] for c in self.creatives)
        total_spend = sum(c['spend'] for c in self.creatives)

        # Средние метрики
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0

        # Лучшие и худшие креативы
        valid_ctr_creatives = [c for c in self.creatives if c['impressions'] > 0]
        valid_cpc_creatives = [c for c in self.creatives if c['clicks'] > 0]

        stats = {
            "total_creatives": len(self.creatives),
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "total_spend": round(total_spend, 2),
            "average_ctr": round(avg_ctr, 2),
            "average_cpc": round(avg_cpc, 2),
            "best_performing": {},
            "worst_performing": {}
        }

        if valid_ctr_creatives:
            best_ctr = max(valid_ctr_creatives, key=lambda x: x['ctr'])
            worst_ctr = min(valid_ctr_creatives, key=lambda x: x['ctr'])

            stats["best_performing"]["ctr"] = {
                "ad_id": best_ctr['ad_id'],
                "ad_name": best_ctr['ad_name'],
                "ctr": best_ctr['ctr']
            }
            stats["worst_performing"]["ctr"] = {
                "ad_id": worst_ctr['ad_id'],
                "ad_name": worst_ctr['ad_name'],
                "ctr": worst_ctr['ctr']
            }

        if valid_cpc_creatives:
            best_cpc = min(valid_cpc_creatives, key=lambda x: x['cpc'])
            worst_cpc = max(valid_cpc_creatives, key=lambda x: x['cpc'])

            stats["best_performing"]["cpc"] = {
                "ad_id": best_cpc['ad_id'],
                "ad_name": best_cpc['ad_name'],
                "cpc": best_cpc['cpc']
            }
            stats["worst_performing"]["cpc"] = {
                "ad_id": worst_cpc['ad_id'],
                "ad_name": worst_cpc['ad_name'],
                "cpc": worst_cpc['cpc']
            }

        return stats

    def reset_round_robin(self) -> None:
        """Сбрасывает индекс round robin ротации."""
        self._round_robin_index = 0

    def add_creative(self, creative: Dict) -> None:
        """
        Добавляет новый креатив в ротацию.

        Args:
            creative: Словарь с данными креатива
        """
        required_fields = ['ad_id', 'ad_name', 'impressions', 'clicks', 'spend']
        for field in required_fields:
            if field not in creative:
                raise ValueError(f"Отсутствует обязательное поле '{field}' в креативе")

        # Вычисляем метрики если отсутствуют
        if 'ctr' not in creative:
            creative['ctr'] = (creative['clicks'] / creative['impressions'] * 100) if creative['impressions'] > 0 else 0.0

        if 'cpc' not in creative:
            creative['cpc'] = (creative['spend'] / creative['clicks']) if creative['clicks'] > 0 else float('inf')

        self.creatives.append(creative)

    def remove_creative(self, ad_id: str) -> bool:
        """
        Удаляет креатив из ротации по ID.

        Args:
            ad_id: ID креатива для удаления

        Returns:
            True если креатив был удален, False если не найден
        """
        initial_length = len(self.creatives)
        self.creatives = [c for c in self.creatives if c['ad_id'] != ad_id]

        # Корректируем индекс round robin если необходимо
        if len(self.creatives) < initial_length:
            if self._round_robin_index >= len(self.creatives):
                self._round_robin_index = 0
            return True

        return False

    def simulate_rotation(self, iterations: int, strategy: str) -> List[Dict]:
        """
        Симулирует последовательность ротации креативов.

        Args:
            iterations: Количество итераций
            strategy: Стратегия ротации

        Returns:
            Список выбранных креативов в порядке ротации
        """
        rotation_sequence = []

        # Сбрасываем состояние для воспроизводимости
        if strategy == "round_robin":
            self.reset_round_robin()

        for i in range(iterations):
            chosen = self.choose_next(strategy)
            rotation_sequence.append({
                "iteration": i + 1,
                "chosen_creative": chosen
            })

        return rotation_sequence
