from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
import requests
from requests.auth import HTTPBasicAuth

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

def test_elasticsearch_connection():
    """Test connection to Elasticsearch"""
    try:
        es_password = "Anubis1274"

        response = requests.get(
            'http://es01:9200/',
            auth=HTTPBasicAuth('elastic', es_password),
            verify=False,
            timeout=30
        )

        if response.status_code == 200:
            cluster_info = response.json()
            print(f"✅ Successfully connected to Elasticsearch!")
            print(f"Cluster Name: {cluster_info.get('cluster_name')}")
            return True
        else:
            print(f"❌ Connection failed. Status: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error connecting to Elasticsearch: {str(e)}")
        return False

def create_test_index():
    """Create a test index in Elasticsearch"""
    try:
        es_password = "Anubis1274"

        response = requests.put(
            'http://es01:9200/airflow_test_index',
            auth=HTTPBasicAuth('elastic', es_password),
            headers={'Content-Type': 'application/json'},
            verify=False,
            timeout=30
        )

        if response.status_code in [200, 201]:
            print("✅ Successfully created test index")
            return True
        else:
            print(f"❌ Failed to create index. Status: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error creating index: {str(e)}")
        return False

def index_sample_document():
    """Index a sample document"""
    try:
        es_password = "Anubis1274"

        document = {
            "timestamp": datetime.now().isoformat(),
            "message": "Hello from Airflow DAG!",
            "source": "airflow_test",
            "status": "success"
        }

        response = requests.post(
            'http://es01:9200/airflow_test_index/_doc',
            auth=HTTPBasicAuth('elastic', es_password),
            headers={'Content-Type': 'application/json'},
            json=document,
            verify=False,
            timeout=30
        )

        if response.status_code in [200, 201]:
            print("✅ Successfully indexed document")
            return True
        else:
            print(f"❌ Failed to index document. Status: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error indexing document: {str(e)}")
        return False

with DAG(
    'test_elasticsearch_integration',
    default_args=default_args,
    description='Test DAG for Elasticsearch integration',
    schedule=timedelta(minutes=30),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['test', 'elasticsearch'],
) as dag:

    start = EmptyOperator(task_id='start')

    test_connection = PythonOperator(
        task_id='test_elasticsearch_connection',
        python_callable=test_elasticsearch_connection,
    )

    create_index = PythonOperator(
        task_id='create_test_index',
        python_callable=create_test_index,
    )

    index_document = PythonOperator(
        task_id='index_sample_document',
        python_callable=index_sample_document,
    )

    check_services = BashOperator(
        task_id='check_services_status',
        bash_command='echo "Test started at $(date)" && sleep 2',
    )

    end = EmptyOperator(task_id='end')

    start >> check_services >> test_connection >> create_index >> index_document >> end
