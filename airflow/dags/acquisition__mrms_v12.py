"""
ACQUIRE MRMS V12 Raw Data and Save to S3;
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def t_download_mrms_v12(ds, **kwargs):
    print("Hello My Name is Operator running at {{ ds }}")
    print(ds)
    return kwargs['cheese']

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2021, 1, 1),
    "catchup_by_default": False,
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG("download_mrms_v12", default_args=default_args, schedule_interval=timedelta(1))

t1 = PythonOperator(
    task_id="download_mrms_v12",
    python_callable=t_download_mrms_v12,
    op_kwargs={'cheese': "machine"},
    dag=dag
)
