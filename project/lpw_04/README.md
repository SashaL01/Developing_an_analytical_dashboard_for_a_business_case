# Л+П №4. Разработка аналитического дашборда для бизнес-кейса 
Вариант 12.

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

![Архитектура](./img/arch.jpg)


### ETL-процесс

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   github    │──▶│   Airflow   │───▶│ PostgreSQL  │──▶│  Superset   │
│   Dataset   │    │   Extract   │    │   Load      │    │ Visualize   │
│             │    │   Transform │    │   Transform │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

![Схема конвеера ETL](./img/conveer.jpg)

### Подключение Airflow к PostgreSQL

**Строка подключения**: `postgresql://airflow:airflow@postgres:5432/airflow`

**Параметры подключения**:
- **Host**: postgres
- **Port**: 5432
- **Database**: airflow
- **Username**: airflow
- **Password**: airflow

### Настройка коннектора analytics_postgres

**Настройки для коннектора analytics_postgres**

| Поле в Airflow | Значение | Откуда взято (из docker-compose.yml) |
|---|---|---|
| Connection Id | analytics_postgres | Имя, используемое в DAG |
| Connection Type | Postgres | Тип базы данных |
| Host | analytics_postgres | Имя сервиса в Docker Compose |
| Schema | analytics | Из environment: POSTGRES_DB=analytics |
| Login | analytics | Из environment: POSTGRES_USER=analytics |
| Password | analytics | Из environment: POSTGRES_PASSWORD=analytics |
| Port | 5432 | Внутренний порт контейнера |

**Пошаговая инструкция**:
1. Зайдите в Airflow UI: http://localhost:8080
2. Перейдите в Admin -> Connections
3. Нажмите синюю кнопку + ("Add a new record")
4. Заполните поля формы согласно таблице выше
5. Нажмите кнопку Test (должно появиться "Connection successfully tested")
6. Нажмите Save

## Технологический стек

### Основные компоненты

*   **Apache Airflow 2.5.0** — оркестрация ETL-процессов, управление задачами
*   **PostgreSQL 12** — хранение данных и аналитическая витрина
*   **Apache Superset 3.1.1** — интерактивная визуализация и дашборды (стабильная версия)
*   **Kaggle API** — извлечение данных с платформы Kaggle
*   **pgAdmin 4** — веб-интерфейс для администрирования PostgreSQL
*   **Redis 7** — кэширование и сессии для Superset
*   **Docker & Docker Compose** — контейнеризация и оркестрация сервисов

### Python библиотеки

*   **pandas** — обработка и анализ данных
*   **github** — скачивание датасетов
*   **psycopg2-binary** — подключение к PostgreSQL
*   **apache-airflow-providers-postgres** — интеграция Airflow с PostgreSQL

### Инфраструктура

*   **Кастомный Dockerfile** — образ Airflow с установленным gcc для компиляции пакетов
*   **Docker Volumes** — постоянное хранение данных
*   **Docker Networks** — изолированная сеть для сервисов

## Быстрый старт

### 1. Настройка Kaggle API
```bash
chmod +x setup_kaggle.sh
./setup_kaggle.sh
```

### 2. Запуск проекта
```bash
    sudo docker compose up -d
```

### 3. Проверка статуса

```bash
sudo docker compose ps
```

### 4. Доступ к сервисам
- **Airflow**: http://localhost:8080 (admin/admin)
- **pgAdmin**: http://localhost:5050 (admin@admin.com/admin)
- **Superset**: http://localhost:8088 (admin/admin)

### 5. Работа с данными
1. В Airflow запустите DAG `us_presidents_analysis`
2. В Superset подключитесь к базе `analytics_postgres`
3. Создайте дашборд с данными из `stg_us_presidents`

## Настройка Apache Superset

**Примечание**. В проекте используется Apache Superset версии 3.1.1 (стабильная версия). Версия `latest` не рекомендуется для продакшена из-за возможных нестабильностей.

### Шаг 1: Подключение к базе данных

1. Откройте Superset: http://localhost:8088
2. Перейдите к подключениям: ⚙️ Settings -> Data
3. Добавьте базу данных: Нажмите + Create Dataset
4. Заполните форму "Connect a database":

![Подключение к базе данных](./img/create_conn_superset_sql_01.jpg)

| Поле | Значение | Объяснение |
|---|---|---|
| Host | analytics_postgres | Имя сервиса базы данных в docker-compose.yml |
| Port | 5432 | Внутренний порт контейнера PostgreSQL |
| Database name | analytics | Из переменной POSTGRES_DB=analytics |
| Username | analytics | Из переменной POSTGRES_USER=analytics |
| Password | analytics | Из переменной POSTGRES_PASSWORD=analytics |
| Display Name | Analytics DB | Удобное имя для подключения |

![Подключение к базе данных](./img/create_conn_superset_sql_02.jpg)

### Шаг 2. Создание датасета

1. В верхнем меню нажмите + и выберите Dataset
2. В появившемся окне выберите:
   - DATABASE. Ваше подключение analytics
   - SCHEMA. public
   - SEE TABLE/VIEW. stg_online_retail
3. Нажмите ADD

### Шаг 3: Создание графиков

**График 1. Индикатор " Общая revenue." (Big Number)**
1. Перейдите в Charts и нажмите + CHART
2. Выберите датасет: datamart_online_retail
3. Выберите тип: Big Number
4. Нажмите CREATE NEW CHART
5. Настройте метрику:
   - В поле METRIC нажмите (+ Drop a column/metric here or click)
   - Выберите агрегацию COUNT(DISTINCT)
   - В поле COLUMN выберите revenue
   - Нажмите Save (метрика: COUNT(DISTINCT revenue))
6. Нажмите UPDATE CHART
7. Сохраните как "Общая revenue"

**График 2. Линейная. revenue по invoice_date**
1. Перейдите в Charts и нажмите + CHART
2. Выберите датасет: datamart_online_retail
3. Выберите тип: Pie Chart
4. Нажмите CREATE NEW CHART
5. Настройте поля:
   - DIMENSIONS: invoice_date (перетащите из левой панели)
   - METRIC: COUNT(revenue) (перетащите из левой панели)
6. Нажмите UPDATE CHART
7. Сохраните как "revenue по invoice_date"

**График 3. Столбчатая. Топ-10 стран по revenue.**
1. Перейдите в Charts и нажмите + CHART
2. Выберите датасет: datamart_online_retail
3. Выберите тип: Bar Chart
4. Нажмите CREATE NEW CHART
5. Настройте поля:
   - X-AXIS: revenue
   - METRIC: COUNT(*)
   - SORT BY: country
   - SORT ASCENDING: ✓ (галочка)
6. Нажмите UPDATE CHART


**График 4. Круговая. Доли продаж по country.**
1. Перейдите в Charts и нажмите + CHART
2. Выберите датасет: datamart_online_retail
3. Выберите тип: Bar Chart
4. Нажмите CREATE NEW CHART
5. Настройте поля:
   - METRICS: count(revenue) (создайте метрику MAX для поля years_in_office)
   - DIMENSIONS: country
   - ROW LIMIT: 10
   - SORT BY: count(revenue) (по убыванию)
6. Перейдите во вкладку CUSTOMIZE:
   - Orientation: Horizontal
7. Нажмите UPDATE CHART


**График 5. Комбинированная. revenue (столбцы) и кол-во заказов (линия) по country.**
1. Перейдите в Charts и нажмите + CHART
2. Выберите датасет: datamart_online_retail
3. Выберите тип: Table
4. Нажмите CREATE NEW CHART
5. Настройте поля:
   - QUERY MODE: Raw Records
   - COLUMNS: revenue, party, start_year, years_in_office
6. Нажмите UPDATE CHART


### Шаг 4. Сборка дашборда

1. В верхнем меню перейдите в Dashboards
2. Нажмите + DASHBOARD
3. Дайте название дашборду: "online retail"
4. Нажмите Save
5. Перетащите созданные графики с правой панели на рабочую область:
   - "Всего президентов" (Big Number) - в верхний левый угол
   - "Распределение по партиям" (Pie Chart) - рядом с индикатором
   - "Президенты по десятилетиям" (Bar Chart) - внизу слева
   - "Топ-10 по сроку правления" (Horizontal Bar Chart) - справа
   - "Сводная таблица" (Table) - внизу справа
6. Расположите и измените их размеры по своему вкусу
7. Нажмите Save для сохранения дашборда

![Сборка дашборда](./img/dashboard_01.jpg)

Отлично, вы на правильном пути! Судя по вашему скриншоту, вы почти создали фильтр. Superset подсвечивает красным единственное, чего не хватает — **имени фильтра**.

Вот скорректированная и полная инструкция на основе вашего изображения:

### Шаг 5. Добавление интерактивного фильтра по партии на дашборд

В окне **"Add and edit filters"**, выполните следующие шаги:

1.  **Заполните обязательное поле `FILTER NAME`**. Это название, которое пользователи увидят на дашборде.
    *   Введите понятное имя, например: **"Партия"** или **"Фильтр по партиям"**.

2.  **Проверьте остальные настройки:**
    *   **`FILTER TYPE`**: **Value** — это правильный тип для создания фильтра с выпадающим списком уникальных значений из колонки.
    *   **`DATASET`**: **stg_us_presidents** — вы правильно выбрали свой набор данных.
    *   **`COLUMN`**: **party** — вы правильно указали колонку, по которой будет происходить фильтрация.

3.  **(Опционально) Настройте поведение фильтра:**
    *   **`Sort filter values`**. Поставьте галочку, чтобы список партий в фильтре был отсортирован по алфавиту. Это удобно для пользователя.
    *   **`Can select multiple values`**. Эта галочка (уже стоит по умолчанию) позволяет пользователям выбирать несколько партий одновременно для сравнения.

4.  **Сохраните фильтр.**
    *   После того как вы введете имя, кнопка сохранения (обычно "Save" или "Add" внизу окна) станет активной. Нажмите ее.

Фильтр появится на вашем дашборде, и вы сможете использовать его для интерактивного анализа данных на всех графиках, построенных на основе датасета `stg_us_presidents`. Не забудьте нажать **"SAVE"** на самом дашборде, чтобы сохранить все изменения.

![Сборка дашборда](./img/dashboard_01.jpg)

### 6. Очистка окружения
```bash
chmod +x cleanup.sh
sudo ./cleanup.sh
```

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


     

### Представление us_presidents_datamart
VIEW на основе таблицы stg_online_retail для аналитики.

## Устранение неполадок

### Проблемы с правами доступа
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Проблемы с Kaggle API
```bash
./setup_kaggle.sh
```

### Проблемы с компиляцией
```bash
sudo docker compose build
sudo docker compose up -d
```

## Git-репозиторий

Проект содержит:
- **DAG**: `dags/us_presidents_dag.py`
- **SQL**: `dags/datamart_variant_30.sql`
- **Docker**: `docker-compose.yml`, `Dockerfile`
- **Скрипты**: `setup_kaggle.sh`, `cleanup.sh`
- **Документация**: `README.md`

**Исключения**: `kaggle.json` (не включать в Git!)

## Форма отчета

Итогом работы является публичный Git-репозиторий с файлом `Readme.md`, оформленным по профессиональному стандарту. Структура `Readme.md` должна включать следующие разделы:

### Цель работы
Краткое описание цели в контексте вашего бизнес-кейса.

### Исследуемые метрики бизнес-процесса
Перечень и описание ключевых метрик, которые вы анализировали.

### Архитектура решения
Краткое описание архитектуры data-конвейера (Airflow -> Postgres -> Superset).

### Технологический стек
Перечень использованных технологий.

### ER-диаграмма базы данных
Схема таблиц в PostgreSQL, задействованных в проекте (можно в виде скриншота).

### Ссылки на исходный код
*   Python-файл вашего DAG (`.py`).
*   SQL-файл для создания витрины данных (`.sql`).
*   JSON-файл с экспортированным дашбордом из Apache Superset или публичная ссылка на дашборд.

### Описание проделанной работы (с наглядными результатами)
*   Скриншот графа успешно выполненного DAG из интерфейса Airflow.
*   Текст вашего SQL-запроса для создания витрины данных (в блоке кода).
*   Скриншот итогового дашборда, на котором видны все 5 обязательных типов чартов и фильтры.

### Выводы по анализу
Краткие выводы и бизнес-инсайты, которые можно сделать на основе созданного дашборда.


# Задание и оценка работы

Варианты заданий для выполнения лабораторной работы доступны по ссылке:
**[Скачать варианты заданий](http://95.131.149.21/moodle/mod/assign/view.php?id=2108)**







