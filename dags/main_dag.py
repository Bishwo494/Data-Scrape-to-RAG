from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow.providers.ssh.operators.ssh import SSHOperator

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 7, 1),
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='main_dag',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    description='A simple dummy DAG',
) as dag:

    start = DummyOperator(task_id='start')


    scrape = SSHOperator(
        task_id='scrape',
        ssh_conn_id='ssh_notebook',  # Must match Airflow UI Connection ID
        command='python3 /home/docker/notebooks/scrapper/scrapper.py',
        cmd_timeout=300000,
        do_xcom_push=False
    )

    silver = SSHOperator(
        task_id='silver',
        ssh_conn_id='ssh_notebook',  # Must match Airflow UI Connection ID
        command='python3 /home/docker/notebooks/etl/json_to_df_final.py',
        cmd_timeout=300000,
        do_xcom_push=False
    )

    gold = SSHOperator(
        task_id='gold',
        ssh_conn_id='ssh_notebook',  # Must match Airflow UI Connection ID
        command='python3 /home/docker/notebooks/etl/golden_layer.py',
        cmd_timeout=300000,
        do_xcom_push=False
    )

    embed = SSHOperator(
        task_id='embed',
        ssh_conn_id='ssh_notebook',  # Must match Airflow UI Connection ID
        command='python3 /home/docker/notebooks/etl/embed2.py',
        cmd_timeout=300000,
        do_xcom_push=False
    )


    end = DummyOperator(task_id='end')

    start >> scrape >> silver >> gold >> embed >> end
