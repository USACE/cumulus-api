"""
ACQUIRE MRMS V12 Raw Data and Save to S3;
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta


def trigger_download(*args, **kwargs):
    print("Time to download this url;")
    return kwargs['URL']

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

# MRMS VERSION 12
MRMS_QPE_PASS1_URL = 'https://mrms.ncep.noaa.gov/data/2D/MultiSensor_QPE_01H_Pass1/MRMS_MultiSensor_QPE_01H_Pass1_00.00_{{ execution_date.strftime("%Y%m%d%H0000") }}.grib2.gz'
MRMS_QPE_PASS2_URL = 'https://mrms.ncep.noaa.gov/data/2D/MultiSensor_QPE_01H_Pass2/MRMS_MultiSensor_QPE_01H_Pass2_00.00_{{ (execution_date - macros.timedelta(hours=1)).strftime("%Y%m%d%H0000") }}.grib2.gz'

dag_mrms_v12 = DAG("download_mrms_v12", default_args=default_args, schedule_interval='55 * * * *')
mrms_v12_qpe_pass1 = PythonOperator(task_id="download_mrms_v12_qpe_pass1", python_callable=trigger_download, op_kwargs={'URL': MRMS_QPE_PASS1_URL}, dag=dag_mrms_v12)
mrms_v12_qpe_pass2 = PythonOperator(task_id="download_mrms_v12_qpe_pass2", python_callable=trigger_download, op_kwargs={'URL': MRMS_QPE_PASS2_URL}, dag=dag_mrms_v12)
