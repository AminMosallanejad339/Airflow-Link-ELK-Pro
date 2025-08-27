from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from plugins.elasticsearch_hook import ElasticsearchHook  # hook سفارشی
import random

def generate_kibana_data():
    """Generate sample data for Kibana visualization and send to Elasticsearch"""
    try:
        es_hook = ElasticsearchHook()
        index_name = "kibana_sample_data"

        # بررسی وجود ایندکس
        if not es_hook.get_conn().indices.exists(index=index_name):
            es_hook.create_index(index=index_name, body={
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 1
                }
            })
            print(f"Index '{index_name}' created")

        sample_data = {
            "timestamp": datetime.now().isoformat(),
            "metric_value": random.randint(1, 100),
            "service": random.choice(["web", "api", "database", "cache"]),
            "status": random.choice(["success", "warning", "error"]),
            "response_time": random.uniform(0.1, 5.0)
        }

        res = es_hook.add_doc(index=index_name, doc=sample_data)
        print(f"✅ Data sent to Elasticsearch: {sample_data}")
        print(f"Response: {res}")
        return True
    except Exception as e:
        print(f"❌ Error sending data to Elasticsearch: {str(e)}")
        return False

with DAG(
    'kibana_data_pipeline_hook',
    description='Generate sample data for Kibana using custom hook',
    schedule=timedelta(minutes=5),
    start_date=datetime(2025, 8, 27),
    catchup=False,
    tags=['kibana', 'data'],
) as dag:

    start = EmptyOperator(task_id='start')

    generate_data = PythonOperator(
        task_id='generate_sample_data',
        python_callable=generate_kibana_data,
    )

    end = EmptyOperator(task_id='end')

    start >> generate_data >> end
