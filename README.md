# Ads Aggregator - Система агрегации рекламных данных


### Требования

- Python 3.10+
- pip

# Установка зависимостей
pip install -r requirements.txt

# Установка 
pip install ads-aggregator

# или в режиме разрабоки 
pip install -e .


### Настройка credentials

#### Meta Ads API

meta_credentials = {
    'access_token': 'your_meta_access_token',
    'app_id': 'your_app_id', 
    'app_secret': 'your_app_secret',
    'account_id': 'act_your_account_id'
}


#### Google Ads API


google_credentials = {
    'developer_token': 'your_developer_token',
    'client_id': 'your_oauth2_client_id',
    'client_secret': 'your_oauth2_client_secret', 
    'refresh_token': 'your_refresh_token',
    'customer_id': 'your_customer_id'
}



##  Тестирование

# Запуск всех тестов
python -m pytest tests/

# Запуск с покрытием кода
python -m pytest tests/ --cov=ads_aggregator


### Запуск примера

python examples/usage_example.py


##API Документация

### BaseAdsClient

Абстрактный базовый класс для всех клиентов рекламных платформ.

**Методы:**
- `fetch_campaigns(start_date, end_date)` - получение кампаний
- `fetch_ads(campaign_id, start_date, end_date)` - получение объявлений

### AdsAggregator

Основной класс для агрегации данных.

**Методы:**
- `aggregate_data(start_date, end_date, parallel=True)` - агрегация данных
- `get_summary_stats(data)` - сводная статистика
- `to_json(data, pretty=True)` - экспорт в JSON
- `filter_by_platform(data, platform)` - фильтрация по платформе
- `filter_by_spend_threshold(data, min_spend)` - фильтрация по расходам

### CreativeRotator

Класс для ротации креативов.

**Методы:**
- `choose_next(strategy)` - выбор следующего креатива
- `get_rotation_stats()` - статистика по креативам
- `add_creative(creative)` - добавление креатива
- `remove_creative(ad_id)` - удаление креатива
- `simulate_rotation(iterations, strategy)` - симуляция ротации
