from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

def print_hello(**kwargs):
    message = "Hello from Airflow!"
    print(message)
    # Push message to XCom
    kwargs['ti'].xcom_push(key='hello_message', value=message)
    return message

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'sample_dag_with_xcom',
    default_args=default_args,
    description='A DAG with PythonOperator XCom to BashOperator',
    schedule=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['example', 'xcom'],
) as dag:

    start = EmptyOperator(task_id='start')

    hello_task = PythonOperator(
        task_id='print_hello',
        python_callable=print_hello,
        provide_context=True  # for **kwargs to access ti
    )

    # BashOperator reads the message from XCom
    bash_task = BashOperator(
        task_id='bash_print_message',
        bash_command='echo "Message from PythonOperator: {{ ti.xcom_pull(task_ids=\'print_hello\', key=\'hello_message\') }}"'
    )

    end = EmptyOperator(task_id='end')

    start >> hello_task >> bash_task >> end
