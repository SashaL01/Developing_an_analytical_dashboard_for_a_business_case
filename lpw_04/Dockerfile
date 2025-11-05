FROM apache/airflow:2.5.0-python3.8
USER root
RUN apt-get update && apt-get install -y gcc python3-dev
USER airflow
RUN pip install --no-cache-dir openpyxl pandas requests