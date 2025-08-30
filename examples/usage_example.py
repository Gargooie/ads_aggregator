import logging
import sys
import os
from datetime import date, timedelta

# Добавляем путь к родительской директории для импорта модуля
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ads_aggregator.clients.meta_ads_client import MetaAdsClient
from ads_aggregator.clients.google_ads_client import GoogleAdsClient
from ads_aggregator.aggregator import AdsAggregator
from ads_aggregator.rotator import CreativeRotator


def main():
    """Демонстрация работы системы агрегации рекламных данных."""

    # Настраиваем логирование
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    print(" Демонстрация системы агрегации рекламных данных\n")

    # 1. Инициализация клиентов рекламных платформ
    print(" Инициализация клиентов...")

    # Meta Ads клиент (мок credentials)
    meta_credentials = {
        'access_token': 'mock_meta_access_token_12345',
        'app_id': 'mock_app_id',
        'app_secret': 'mock_app_secret',
        'account_id': 'act_1234567890'
    }
    meta_client = MetaAdsClient(meta_credentials)

    # Google Ads клиент (мок credentials)
    google_credentials = {
        'developer_token': 'mock_developer_token_abcdef',
        'client_id': 'mock_client_id',
        'client_secret': 'mock_client_secret',
        'refresh_token': 'mock_refresh_token',
        'customer_id': '1234567890'
    }
    google_client = GoogleAdsClient(google_credentials)

    print(f" Meta Ads клиент: {meta_client.platform_name}")
    print(f" Google Ads клиент: {google_client.platform_name}\n")

    # 2. Создание агрегатора
    aggregator = AdsAggregator([meta_client, google_client])

    # 3. Получение данных за последние 7 дней
    end_date = date.today()
    start_date = end_date - timedelta(days=7)

    print(f" Получение данных за период: {start_date} - {end_date}")

    try:
        # Агрегируем данные с обеих платформ
        aggregated_data = aggregator.aggregate_data(start_date, end_date, parallel=True)

        print(f" Успешно получены данные с {len(aggregated_data)} кампаний\n")

        # 4. Показываем сводную статистику
        stats = aggregator.get_summary_stats(aggregated_data)

        print(" Сводная статистика:")
        print(f"  Всего платформ: {stats['total_platforms']}")
        print(f"  Всего кампаний: {stats['total_campaigns']}")
        print(f"  Всего объявлений: {stats['total_ads']}")
        print(f"  Общие показы: {stats['totals']['impressions']:,}")
        print(f"  Общие клики: {stats['totals']['clicks']:,}")
        print(f"  Общие расходы: ${stats['totals']['spend']:,.2f}\n")

        print(" Статистика по платформам:")
        for platform, platform_stats in stats['platform_breakdown'].items():
            print(f"  {platform.upper()}:")
            print(f"    Кампаний: {platform_stats['campaigns']}")
            print(f"    Объявлений: {platform_stats['ads']}")
            print(f"    Показы: {platform_stats['impressions']:,}")
            print(f"    Клики: {platform_stats['clicks']:,}")
            print(f"    Расходы: ${platform_stats['spend']:,.2f}")

        print("\n" + "="*50 + "\n")

        # 5. Демонстрация ротации креативов
        print(" Демонстрация ротации креативов")

        # Собираем все креативы из первой кампании с объявлениями
        campaign_with_ads = None
        for campaign in aggregated_data:
            if campaign['ads']:
                campaign_with_ads = campaign
                break

        if campaign_with_ads:
            print(f" Используем креативы из кампании: {campaign_with_ads['name']}")

            # Создаем ротатор
            rotator = CreativeRotator(campaign_with_ads['ads'])

            print(f" Инициализирован ротатор с {len(campaign_with_ads['ads'])} креативами\n")

            # Демонстрируем разные стратегии
            strategies = ["round_robin", "best_ctr", "lowest_cpc"]

            for strategy in strategies:
                print(f" Стратегия: {strategy}")

                # Показываем 3 итерации ротации
                for i in range(3):
                    chosen = rotator.choose_next(strategy)
                    print(f"  Итерация {i+1}: {chosen['ad_name']} "
                          f"(CTR: {chosen['ctr']:.2f}%, CPC: ${chosen['cpc']:.2f})")

                print()

                # Сбрасываем round_robin для демонстрации
                if strategy == "round_robin":
                    rotator.reset_round_robin()

            # Показываем статистику ротатора
            rotation_stats = rotator.get_rotation_stats()
            print(" Статистика креативов:")
            print(f"  Всего креативов: {rotation_stats['total_creatives']}")
            print(f"  Средний CTR: {rotation_stats['average_ctr']:.2f}%")
            print(f"  Средний CPC: ${rotation_stats['average_cpc']:.2f}")

            if 'best_performing' in rotation_stats and 'ctr' in rotation_stats['best_performing']:
                best_ctr = rotation_stats['best_performing']['ctr']
                print(f"  Лучший CTR: {best_ctr['ad_name']} ({best_ctr['ctr']:.2f}%)")

            if 'best_performing' in rotation_stats and 'cpc' in rotation_stats['best_performing']:
                best_cpc = rotation_stats['best_performing']['cpc']
                print(f"  Лучший CPC: {best_cpc['ad_name']} (${best_cpc['cpc']:.2f})")

        print("\n" + "="*50 + "\n")

        # 6. Экспорт данных в JSON
        print(" Экспорт данных в JSON...")

        json_data = aggregator.to_json(aggregated_data, pretty=True)

        # Показываем первые 500 символов JSON для примера
        print("Пример JSON структуры:")
        print(json_data[:500] + "..." if len(json_data) > 500 else json_data)

        print(f"\n Полный JSON содержит {len(json_data)} символов")

        # 7. Демонстрация фильтрации данных
        print("\n Фильтрация данных:")

        # Фильтр по платформе
        meta_data = aggregator.filter_by_platform(aggregated_data, "meta")
        google_data = aggregator.filter_by_platform(aggregated_data, "google")

        print(f"  Meta кампаний: {len(meta_data)}")
        print(f"  Google кампаний: {len(google_data)}")

        # Фильтр по минимальным расходам
        high_spend_campaigns = aggregator.filter_by_spend_threshold(aggregated_data, 50.0)
        print(f"  Кампании с расходами ≥ $50: {len(high_spend_campaigns)}")

        print("\n Демонстрация завершена успешно!")

    except Exception as e:
        logger.error(f"Ошибка во время демонстрации: {e}")
        print(f" Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
