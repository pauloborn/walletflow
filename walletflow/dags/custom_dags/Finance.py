# python libs
import logging
import os
from datetime import datetime, timedelta, date

# airflow libs
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

# internal libs
from sqlalchemy_utils.types.enriched_datetime.pendulum_date import pendulum

from walletflow.dags.custom_dags.finance.crawler.NubankCrawler import NubankCrawler
from walletflow.dags.custom_dags.finance.normalize.NubankNormalize import NubankNormalize


def dummy_fn():
    return ''


logging.debug('Starting Dag configuration')

date_tag = date.today().strftime('%Y%m%d')
base_folder = f'{os.environ["AIRFLOW_HOME"]}/data/{date_tag}'
nubank_filename = f'{base_folder}/nubank.txt'

default_args = {
    "owner": "paulo.born",
    "depends_on_past": False,
    "start_date": datetime.now() - timedelta(minutes=20),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "catchup": False,
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

finance_dag = DAG(
    dag_id="finance_integration",
    description='DAG finance crawler',
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=['example'],
    default_args=default_args
)

nucrawler = NubankCrawler()
nubank_crawler = PythonOperator(
    task_id='nubank_crawler',
    python_callable=nucrawler.run(),
    dag=finance_dag
)

nunormalize = NubankNormalize()
nubank_normalize = PythonOperator(
    task_id='nubank_normalize',
    python_callable=nunormalize.run(),
    dag=finance_dag
)

dummy = EmptyOperator(task_id="nothing")

nubank_crawler >> dummy

logging.debug('Ended Dag configuration')
