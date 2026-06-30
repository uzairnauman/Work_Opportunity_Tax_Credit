from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Import your existing scripts
from Scripts.hire import hire_employee
from Scripts.fire_employee import fire_employee
from Scripts.simulate_day import simulate_day

# Define default args for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 12, 17),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    'simulate_day',
    default_args=default_args,
    schedule_interval='@daily',  # or None for manual trigger
    catchup=False,
) as dag:

    task_simulate_day = PythonOperator(
        task_id='run_simulate_day',
        python_callable=simulate_day
    )

    task_simulate_day  # set task order (only one task here)
