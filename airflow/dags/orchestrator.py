import sys
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount



sys.path.append('/opt/airflow/api-request')
from insert_records import main



# Near the top of the file
PG_USER = os.environ['POSTGRES_USER']
PG_PASSWORD = os.environ['POSTGRES_PASSWORD']
PG_DB = os.environ['POSTGRES_DB']


default_args = {
    'description': 'A DAG to orchestrate data',
    'start_date': datetime(2024, 4, 30),
    'catchup': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30),
}

dag = DAG(
    dag_id='weather-api-dbt-orchestrator',
    default_args=default_args,
    schedule=timedelta(hours=1),
)

with dag:
    task1 = PythonOperator(
        task_id='ingest_data_task',
        python_callable=main,
    )

    task2 = DockerOperator(
        task_id ='transform_data_task',
        image= 'ghcr.io/dbt-labs/dbt-postgres:1.9.0',
        command = 'build',
        working_dir='/usr/app',
        environment={
            'POSTGRES_USER': PG_USER,
            'POSTGRES_PASSWORD': PG_PASSWORD,
            'POSTGRES_DB': PG_DB,
        },
        mounts=[
            Mount(source='/home/loubens/repos/weather/dbt/my_project',
                  target='/usr/app', type='bind'),
              Mount(source='/home/loubens/repos/weather/dbt/profiles.yml',
                  target='/root/.dbt/profiles.yml', type='bind'),
        ],
        network_mode='weather_my_network',
        docker_url='unix://var/run/docker.sock',
        auto_remove='success'
    )

    task1 >> task2
