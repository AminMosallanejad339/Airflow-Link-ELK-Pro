from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator

def print_hello():
    print("✅ Airflow is working correctly!")
    return "Success"

with DAG(
    'simple_airflow_test',
    description='Simple test DAG',
    schedule=timedelta(minutes=15),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['test'],
) as dag:

    start = EmptyOperator(task_id='start')

    bash_test = BashOperator(
        task_id='bash_command_test',
        bash_command='echo "Bash operator working!" && sleep 1',
    )

    python_test = PythonOperator(
        task_id='python_function_test',
        python_callable=print_hello,
    )

    end = EmptyOperator(task_id='end')

    start >> bash_test >> python_test >> end
