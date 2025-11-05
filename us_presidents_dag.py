"""
DAG для анализа online retail
Вариант задания №12

Автор: LeeAA
Дата: 2024
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago
import math

# Конфигурация по умолчанию для DAG
default_args = {
    'owner': 'student',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

# Создание DAG
dag = DAG(
    'online_retail_analysis',
    default_args=default_args,
    description='Анализ online retail - вариант 12',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['etl', 'online_retail', 'github', 'variant_12']
)

def extract_from_github(**context):
    """
    Extract: Скачивание данных о online retail с github используя raw URL
    """
    import os
    import requests
    import pandas as pd
    from tempfile import gettempdir

    # Используем raw URL для прямого скачивания
    raw_url = "https://github.com/SashaL01/online_retail_dataset/raw/main/Online%20Retail.xlsx"
    
    # Используем системную временную директорию
    save_dir = gettempdir()
    local_path = os.path.join(save_dir, "Online_Retail.xlsx")
    
    print(f"Скачивание файла с: {raw_url}")
    print(f"Сохранение в: {local_path}")

    try:
        response = requests.get(raw_url, timeout=60, stream=True)
        response.raise_for_status()
        
        # Сохраняем файл частями для больших файлов
        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"Файл успешно сохранен: {local_path}")
        print(f"Размер файла: {os.path.getsize(local_path)} байт")
        
        # Проверяем что файл читается
        df = pd.read_excel(local_path, nrows=5)
        print(f"Структура данных: {df.shape}")
        print(f"Колонки: {df.columns.tolist()}")
        print(f"Первые 5 записей:\n{df.head()}")
        
        context["ti"].xcom_push(key="data_file_path", value=local_path)
        return local_path
        
    except Exception as e:
        print(f"Ошибка при извлечении данных: {str(e)}")
        # Удаляем частично скачанный файл при ошибке
        if os.path.exists(local_path):
            try:
                os.remove(local_path)
                print("Частично скачанный файл удален")
            except:
                pass
        raise

def load_raw_to_postgres(**context):
    """
    Load Raw: Загрузка сырых данных в PostgreSQL
    """
    import pandas as pd
    import os
    
    print("Начинаем загрузку сырых данных в PostgreSQL...")
    data_file_path = context['ti'].xcom_pull(key='data_file_path', task_ids='extract_from_github')
    
    # Проверяем что файл существует
    if not os.path.exists(data_file_path):
        raise FileNotFoundError(f"Файл не найден: {data_file_path}")
        
    df = pd.read_excel(data_file_path)
    print(f"Загружено {len(df)} записей из файла")

    postgres_hook = PostgresHook(postgres_conn_id='analytics_postgres')

    postgres_hook.run("DROP TABLE IF EXISTS raw_online_retail;")
   
    create_table_sql = """
    CREATE TABLE raw_online_retail (
        id SERIAL PRIMARY KEY,
        invoiceno TEXT,
        stockcode TEXT,
        description TEXT,
        quantity INTEGER,
        invoicedate TIMESTAMP,
        unitprice DECIMAL(10,2),
        customerid TEXT,
        country TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    postgres_hook.run(create_table_sql)
    
    df.columns = [col.lower() for col in df.columns]
    df_clean = df.fillna('')
        
    postgres_hook.insert_rows(
        table='raw_online_retail',
        rows=df_clean.values.tolist(),
        target_fields=df.columns.tolist()
    )
    print(f"Успешно загружено {len(df_clean)} записей в raw_online_retail")
    
    # Очищаем временный файл
    try:
        os.remove(data_file_path)
        print(f"Временный файл удален: {data_file_path}")
    except Exception as e:
        print(f"Не удалось удалить временный файл: {e}")

def transform_and_clean_data(**context):
    """
    Transform: Очистка данных, преобразование дат и обогащение для дашборда
    """
    import pandas as pd
    
    print("Начинаем очистку, трансформацию и обогащение данных...")
    postgres_hook = PostgresHook(postgres_conn_id='analytics_postgres')
    
    df = postgres_hook.get_pandas_df("SELECT * FROM raw_online_retail;")
    df_clean = df.copy()

    # Удаляем отрицательные значения
    df_clean = df_clean[df_clean['quantity'] > 0]
    df_clean = df_clean[df_clean['unitprice'] > 0]  

    # ОБОГАЩЕНИЕ ДАННЫХ
    df_clean['invoicedate'] = pd.to_datetime(df_clean['invoicedate'])  
    df_clean['invoice_year'] = df_clean['invoicedate'].dt.year
    df_clean['invoice_month'] = df_clean['invoicedate'].dt.month
    df_clean['invoice_day'] = df_clean['invoicedate'].dt.day
    df_clean['day_of_week'] = df_clean['invoicedate'].dt.day_name()
    df_clean['invoice_hour'] = df_clean['invoicedate'].dt.hour
    
    # Total amount
    df_clean['total_amount'] = df_clean['quantity'] * df_clean['unitprice']  

    # Price segments
    def price_segment(unit_price):
        if unit_price < 1: return 'budget'
        if unit_price < 3: return 'economy'
        if unit_price < 5: return 'standard'
        if unit_price < 10: return 'premium'
        else: return 'luxury'

    df_clean['price_segment'] = df_clean['unitprice'].apply(price_segment)

    # Season
    def get_season(month):
        if month in [12, 1, 2]: return 'winter'
        elif month in [3, 4, 5]: return 'spring'
        elif month in [6, 7, 8]: return 'summer'
        else: return 'autumn'
    
    df_clean['season'] = df_clean['invoice_month'].apply(get_season)
    
    # Time of day
    def time_of_day(hour):
        if 5 <= hour < 12: return 'morning'
        elif 12 <= hour < 17: return 'afternoon'  
        elif 17 <= hour < 21: return 'evening'
        else: return 'night'
        
    df_clean['time_of_day'] = df_clean['invoice_hour'].apply(time_of_day)

    # Holidays 
    def get_holiday_period(month, day):
        if month == 12 and day >= 15: 
            return 'new_year_holidays'
        elif month == 11: 
            return 'black_friday'
        elif month == 2 and day <= 14:  
            return 'valentines_day'
        elif month == 2 and day <= 23:
            return 'mans_day'  
        elif month == 3 and day <= 8: 
            return 'womens_day'  
        else: 
            return 'regular'

    df_clean['holiday_period'] = df_clean.apply(
        lambda x: get_holiday_period(x['invoice_month'], x['invoice_day']), axis=1
    )

    # СОХРАНЕНИЕ В БАЗУ ДАННЫХ
    postgres_hook.run("DROP TABLE IF EXISTS stg_online_retail CASCADE;")
    
    create_staging_table_sql = """
    CREATE TABLE stg_online_retail (
        id SERIAL PRIMARY KEY,
        invoiceno TEXT,
        stockcode TEXT,
        description TEXT,
        quantity INTEGER,
        invoicedate TIMESTAMP,
        unitprice DECIMAL(10,2),
        customerid TEXT,
        country TEXT,
        invoice_year INTEGER,
        invoice_month INTEGER,
        invoice_day INTEGER,
        invoice_hour INTEGER,
        day_of_week TEXT,
        total_amount DECIMAL(10,2),
        price_segment TEXT,
        season TEXT,
        time_of_day TEXT,
        holiday_period TEXT
    );
    """
    postgres_hook.run(create_staging_table_sql)
    
    # Выбираем колонки для загрузки
    columns_to_load = [
        'invoiceno', 'stockcode', 'description', 'quantity', 'invoicedate',
        'unitprice', 'customerid', 'country', 'invoice_year', 'invoice_month',
        'invoice_day', 'invoice_hour', 'day_of_week', 'total_amount', 
        'price_segment', 'season', 'time_of_day', 'holiday_period'
    ]
    
    # Загружаем данные
    postgres_hook.insert_rows(
        table='stg_online_retail',
        rows=df_clean[columns_to_load].values.tolist(),
        target_fields=columns_to_load
    )
    
    print(f"Успешно загружено {len(df_clean)} записей в stg_online_retail")

# --- Задачи DAG ---
extract_task = PythonOperator(  
    task_id='extract_from_github',
    python_callable=extract_from_github,
    dag=dag
)

load_raw_task = PythonOperator(
    task_id='load_raw_to_postgres',
    python_callable=load_raw_to_postgres,
    dag=dag
)

transform_task = PythonOperator(
    task_id='transform_and_clean_data',
    python_callable=transform_and_clean_data,
    dag=dag
)

create_datamart_task = PostgresOperator(
    task_id='create_datamart',
    postgres_conn_id='analytics_postgres',
    sql='datamart_variant_12.sql',  
    dag=dag
)

# --- Определение зависимостей ---
extract_task >> load_raw_task >> transform_task >> create_datamart_task