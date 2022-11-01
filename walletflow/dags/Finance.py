# python libs
import logging
import os
from datetime import datetime, timedelta, date

# airflow libs
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

# internal libs
from walletflow.dags.common_package.connector.Nubank import nubankExtractor

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

finance_dag = DAG("finance_integration", default_args=default_args)

nubank_crawler = PythonOperator(
                task_id='parse_log',
                python_callable=nubankExtractor,
                op_kwargs={'outfile_path': nubank_filename},
                dag=finance_dag)

dummy = EmptyOperator(task_id="nothing")

nubank_crawler >> dummy

logging.debug('Ended Dag configuration')
