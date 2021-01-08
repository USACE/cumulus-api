FROM apache/airflow:master-python3.8

USER root
COPY init.sh /init.sh
RUN chown airflow:airflow /init.sh

USER airflow
COPY airflow.cfg /opt/airflow/airflow.cfg
COPY ./dags/* /opt/airflow/dags/
