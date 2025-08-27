import datetime as dt
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from elasticsearch_plugin.hooks.elasticsearch_hook import ElasticsearchHook

default_args = {
    'owner': 'airflow',
    'start_date': dt.datetime(2025, 3, 3, 10, 0, 0),
    'retries': 0,
    'concurrency': 1
}

def search_tweets():
    # استفاده از hook جدید
    es_hook = ElasticsearchHook()

    # اطلاعات اتصال
    info = es_hook.info()
    print("Elasticsearch Info:", info)

    # سرچ ساده روی index 'tweets'
    result = es_hook.search(
        index='tweets',
        body={
            "query": {
                "term": {
                    "content": {"value": "داده"}
                }
            }
        }
    )
    print("Search Result:", result)

with DAG(
    'plugin_hook_dag_fixed',
    default_args=default_args,
    schedule='@once',
    catchup=False,
    tags=['elasticsearch']
) as dag:

    hook_task = PythonOperator(
        task_id='hook_es_task',
        python_callable=search_tweets
    )

    end_task = BashOperator(
        task_id='end_task',
        bash_command='echo "DAG Completed Successfully 😎"'
    )

    hook_task >> end_task
