import datetime as dt
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from elasticsearch_plugin.hooks.elasticsearch_hook import ElasticsearchHook

default_args = {
    'owner': 'airflow',
    'start_date': dt.datetime(2025, 3, 3, 10, 0, 0),
    'concurrency': 1,
    'retries': 0
}

def do_some_stuff():
    es_hook = ElasticsearchHook()
    print(es_hook.info())
    result = es_hook.search(
        index='tweets',
        body={
            "query": {
                "term": {
                    "content": {
                        "value": "داده"
                    }
                }
            }
        }
    )
    print(result)

with DAG(
    'plugin_hook_dag',
    default_args=default_args,
    schedule='@once',
    catchup=False
) as dag:
    hook_es = PythonOperator(
        task_id='hook_es',
        python_callable=do_some_stuff
    )

    opr_end = BashOperator(
        task_id='opr_end',
        bash_command='echo "Done Darling 😎"'
    )

    hook_es >> opr_end