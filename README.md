# Developing_an_analytical_dashboard_for_a_business_case

# Л+П №4. Разработка аналитического дашборда для бизнес-кейса 
Вариант 12.

## Цель работы
извлечь данные из github , загрузить в postgress в raw слой, проанализировать ,очисть и сделать насыщение данных , далее, заругрузить в stg слой и создать витринну данных , создать чарты и дашборд в superset

## Описание проекта

Полный цикл аналитики данных для анализа процессов online retail:
- Извлечение данных с github
- Загрузка в PostgreSQL
- Создание аналитической витрины
- Визуализация в Apache Superset

## Метрики и показатели

*    **invoiceNo** — номер инвойса
*    **StockCode** — код товара
*    **Description** — описание товара
*    **Quantity** — кол-во заказанного товара
*    **InvoiceDate** — дата инвойса
*    **UnitPrice** — цена за единицу товара
*    **CustomerID** — id клиента
*    **Country** — страна заказа

## Логика расчета показателей

**Исходные данные**

*   **archive ics uci**. `Online Retail` — данные об онлайн продажах
*   **Поля**. invoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID,Country


**Ожидаемый результат.** Интерактивный дашборд с визуализацией ключевых метрик онлайн продаж.

## Подробная архитектура решения

### Общая схема системы

![Архитектура] <img width="637" height="601" alt="image" src="https://github.com/user-attachments/assets/7c549636-a3c4-4601-bc3e-ef0fbb34a7b8" />


### ETL-процесс

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   github    │──▶│   Airflow   │───▶│ PostgreSQL  │──▶│  Superset   │
│   Dataset   │    │   Extract   │    │   Load      │    │ Visualize   │
│             │    │   Transform │    │   Transform │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

![Схема конвеера ETL]<img width="918" height="212" alt="image" src="https://github.com/user-attachments/assets/3845d386-271a-47a4-9307-9cd35b452cd8" />

## Технологический стек

### Основные компоненты

*   **Apache Airflow 2.5.0** — оркестрация ETL-процессов, управление задачами
*   **PostgreSQL 12** — хранение данных и аналитическая витрина
*   **Apache Superset 3.1.1** — интерактивная визуализация и дашборды (стабильная версия)
*   **github API** — извлечение данных с платформы github
*   **pgAdmin 4** — веб-интерфейс для администрирования PostgreSQL
*   **Redis 7** — кэширование и сессии для Superset
*   **Docker & Docker Compose** — контейнеризация и оркестрация сервисов

### Python библиотеки

*   **pandas** — обработка и анализ данных
*   **github** — скачивание датасетов
*   **psycopg2-binary** — подключение к PostgreSQL
*   **apache-airflow-providers-postgres** — интеграция Airflow с PostgreSQL

## Структура проекта

```
lpw_04/
├── dags/
│   ├── us_presidents_dag.py     # DAG для варианта 30
│   └── datamart_variant_12.sql  # SQL для витрины данных
├── docker-compose.yml           # Конфигурация инфраструктуры
├── Dockerfile                   # Кастомный образ Airflow
├── requirements.txt             # Python зависимости
├── kaggle.json                  # Kaggle API ключ
├── setup_kaggle.sh              # Настройка Kaggle API
├── cleanup.sh                   # Очистка окружения
└── README.md                    # Документация
```

## Структура данных

### Таблица stg_us_presidents
Основная таблица с обогащенными данными о президентах США:

| Поле | Тип | 
|---|---|---|
| invoiceno | TEXT | 
| stockcode | TEXT |
| description | TEXT |
| quantity | INTEGER | 
| invoicedate | TIMESTAMP | 
| unitprice | DECIMAL(10,2)  
|  customerid  |  INTEGER    |  
| country     |TEXT      |  
|invoice_year      | TIMESTAMP     
| invoice_month     | TIMESTAMP      
|invoice_day      |  TIMESTAMP     
|invoice_hour      |    TIMESTAMP  
|day_of_week      |    TIMESTAMP  
| total_amount     |  DECIMAL(10,2),     
| price_segment | TEXT
|   season | TEXT
|   time_of_day | TEXT
|  holiday_period | TEXT


     


### ссылка на dashboard
http://localhost:8088/superset/dashboard/p/N7Jd1OG1veM/

### ER-диаграмма базы данных
Схема таблиц в PostgreSQL
<img width="797" height="626" alt="image" src="https://github.com/user-attachments/assets/44208028-6ad7-4d4e-a3a3-ab4ce854fbbd" />



### Выводы по анализу
На основе созданного дашборда видно, что объем выручки составляет 10.6 миллионов, основноая покупающаяя страна Великобритании, который генерирует 85% общего дохода. Это создает риски для компании - любые изменения  могут существенно повлиять на все финансовые показатели.
Европейские рынки, остаются слаборазвитыми: Нидерланды, Ирландия и Германия вместе составляют менее 7% от общей выручки.







