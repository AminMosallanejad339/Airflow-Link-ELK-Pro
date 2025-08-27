from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from elasticsearch_hook import ElasticsearchHook  # ← مستقیم import از فایل hook
import warnings

# غیرفعال کردن هشدارهای مربوط به SSL
warnings.filterwarnings("ignore")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}

def test_es_connection(**kwargs):
    """Test Elasticsearch connection using custom hook"""
    hook = ElasticsearchHook()
    if hook.ping():
        print("✅ Connected to Elasticsearch")
        kwargs['ti'].xcom_push(key='es_status', value=True)
        return True
    else:
        print("❌ Elasticsearch connection failed")
        kwargs['ti'].xcom_push(key='es_status', value=False)
        return False

def decide_next_task(**kwargs):
    """Decide whether to create index or skip"""
    es_status = kwargs['ti'].xcom_pull(task_ids='test_elasticsearch_connection', key='es_status')
    if es_status:
        return 'create_test_index'
    else:
        return 'skip_indexing'

def create_test_index():
    """Create test index using ElasticsearchHook"""
    hook = ElasticsearchHook()
    if hook.create_index('airflow_test_index'):
        print("✅ Test index created")
        return True
    else:
        print("❌ Failed to create index")
        return False

def index_sample_document():
    """Index sample document using ElasticsearchHook"""
    hook = ElasticsearchHook()
    doc = {
        "timestamp": datetime.now().isoformat(),
        "message": "Hello from Airflow DAG!",
        "source": "airflow_test",
        "status": "success"
    }
    if hook.index_document('airflow_test_index', doc):
        print("✅ Document indexed successfully")
        return True
    else:
        print("❌ Failed to index document")
        return False

with DAG(
    'elasticsearch_integration_hook',
    default_args=default_args,
    description='DAG with custom ElasticsearchHook',
    schedule=timedelta(minutes=30),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['elasticsearch', 'hook', 'test'],
) as dag:

    start = EmptyOperator(task_id='start')

    test_connection = PythonOperator(
        task_id='test_elasticsearch_connection',
        python_callable=test_es_connection,
        provide_context=True
    )

    branch_task = BranchPythonOperator(
        task_id='branch_after_connection',
        python_callable=decide_next_task,
        provide_context=True
    )

    create_index_task = PythonOperator(
        task_id='create_test_index',
        python_callable=create_test_index
    )

    index_document_task = PythonOperator(
        task_id='index_sample_document',
        python_callable=index_sample_document
    )

    skip_indexing = EmptyOperator(task_id='skip_indexing')

    end = EmptyOperator(task_id='end', trigger_rule='none_failed_or_skipped')

    # تعریف ترتیب اجرا
    start >> test_connection >> branch_task
    branch_task >> create_index_task >> index_document_task >> end
    branch_task >> skip_indexing >> end
