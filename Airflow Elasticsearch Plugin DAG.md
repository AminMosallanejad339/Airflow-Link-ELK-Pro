# Airflow Elasticsearch Plugin DAG - Complete Setup Guide

## 📋 Overview

This guide provides step-by-step instructions to set up an Airflow DAG that connects to Elasticsearch using a custom plugin and hook.

## 🏗️ Architecture

```
Airflow DAG → Custom Elasticsearch Hook → Elasticsearch Cluster (3 nodes)
```

## 📁 Project Structure

 ![2025-08-25-173336](2025-08-25-173336.png)

## 🚀 Step-by-Step Setup

### 1. Create Plugin Directory Structure

```bash
mkdir -p plugins/elasticsearch_plugin/hooks
mkdir -p plugins/elasticsearch_plugin/operators
```

### 2. Create Plugin Initialization Files

**File: `plugins/elasticsearch_plugin/__init__.py`**
```python
from airflow.plugins_manager import AirflowPlugin
from elasticsearch_plugin.hooks.elasticsearch_hook import ElasticsearchHook

class ElasticsearchPlugin(AirflowPlugin):
    name = "elasticsearch_plugin"
    hooks = [ElasticsearchHook]
```

**File: `plugins/elasticsearch_plugin/hooks/__init__.py`**
```python
from .elasticsearch_hook import ElasticsearchHook

__all__ = ['ElasticsearchHook']
```

### 3. Create Elasticsearch Hook

**File: `plugins/elasticsearch_plugin/hooks/elasticsearch_hook.py`**
```python
from airflow.hooks.base import BaseHook
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3

class ElasticsearchHook(BaseHook):
    """
    Hook to connect to Elasticsearch
    """
    def __init__(self, elasticsearch_conn_id='elasticsearch_default'):
        super().__init__()
        self.elasticsearch_conn_id = elasticsearch_conn_id
        self.client = None
        
    def get_conn(self):
        """
        Returns an Elasticsearch client
        """
        if self.client is not None:
            return self.client
            
        conn = self.get_connection(self.elasticsearch_conn_id)
        
        # Extract connection details
        host = conn.host or 'localhost'
        port = conn.port or 9200
        login = conn.login
        password = conn.password
        extra = conn.extra_dejson
        
        # Build connection parameters
        es_params = {
            'hosts': [{'host': host, 'port': port}],
            'use_ssl': extra.get('use_ssl', False),
            'verify_certs': extra.get('verify_certs', False),
            'timeout': extra.get('timeout', 30),
        }
        
        # Add authentication if provided
        if login and password:
            es_params['http_auth'] = (login, password)
            
        # AWS IAM authentication (if using AWS Elasticsearch)
        if extra.get('aws_region'):
            aws_region = extra['aws_region']
            aws_access_key = extra.get('aws_access_key_id')
            aws_secret_key = extra.get('aws_secret_access_key')
            
            if aws_access_key and aws_secret_key:
                aws_auth = AWS4Auth(aws_access_key, aws_secret_key, aws_region, 'es')
            else:
                # Use IAM role credentials
                session = boto3.Session()
                credentials = session.get_credentials()
                aws_auth = AWS4Auth(
                    credentials.access_key,
                    credentials.secret_key,
                    aws_region,
                    'es',
                    session_token=credentials.token
                )
                
            es_params['http_auth'] = aws_auth
            es_params['connection_class'] = RequestsHttpConnection
            
        self.client = Elasticsearch(**es_params)
        return self.client
        
    def info(self):
        """
        Get cluster info
        """
        es = self.get_conn()
        return es.info()
        
    def search(self, index, body, **kwargs):
        """
        Execute a search query
        """
        es = self.get_conn()
        return es.search(index=index, body=body, **kwargs)
        
    def index(self, index, body, id=None, **kwargs):
        """
        Index a document
        """
        es = self.get_conn()
        return es.index(index=index, body=body, id=id, **kwargs)
        
    def get(self, index, id, **kwargs):
        """
        Get a document by ID
        """
        es = self.get_conn()
        return es.get(index=index, id=id, **kwargs)
```

### 4. Create Your DAG File

**File: `dags/elasticsearch_plugin_dag.py`**
```python
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
```

### 5. Set Up Airflow Connection

**Method 1: Using Airflow UI**
1. Open Airflow UI at http://localhost:8080
2. Go to **Admin → Connections**
3. Click **+**
4. Fill in:
   - Connection Id: `elasticsearch_default`
   - Connection Type: `HTTP`
   - Host: `es01` (or your Elasticsearch host)
   - Port: `9200`
   - Login: `elastic`
   - Password: `your_elastic_password` (from .env file)
   - Extra: `{"use_ssl": true, "verify_certs": false}`

**Method 2: Using CLI**
```bash
docker exec -it airflow-elk-pro-airflow-scheduler-1 airflow connections add \
    'elasticsearch_default' \
    --conn-type 'http' \
    --conn-host 'es01' \
    --conn-port 9200 \
    --conn-login 'elastic' \
    --conn-password 'your_elastic_password' \
    --conn-extra '{"use_ssl": true, "verify_certs": false}'
```

### 6. Install Required Python Packages

Add to your `docker-compose.yml` in the `x-airflow-common` section:

```yaml
environment:
  &airflow-common-env
  _PIP_ADDITIONAL_REQUIREMENTS: >
    elasticsearch==7.13.0
    boto3==1.26.0
    requests-aws4auth==1.1.0
```

### 7. Restart Airflow Services

```bash
docker-compose down
docker-compose up -d
```

### 8. Verify Plugin Loading

```bash
docker exec airflow-elk-pro-airflow-scheduler-1 airflow plugins list
```

You should see your `elasticsearch_plugin` in the list.

### 9. Test Elasticsearch Connection

```bash
# Test Elasticsearch is reachable
docker exec airflow-elk-pro-airflow-scheduler-1 curl -u elastic:your_elastic_password https://es01:9200 -k

# Create test index with some data
docker exec airflow-elk-pro-airflow-scheduler-1 curl -X POST -u elastic:your_elastic_password \
  "https://es01:9200/tweets/_doc" \
  -H 'Content-Type: application/json' \
  -d '{
    "content": "این یک داده تست است",
    "timestamp": "2024-01-01T00:00:00",
    "user": "test_user"
  }' -k
```

### 10. Trigger the DAG

**Method 1: Using UI**
1. Go to Airflow UI → DAGs
2. Find `plugin_hook_dag`
3. Click trigger button (play icon)

**Method 2: Using CLI**
```bash
docker exec airflow-elk-pro-airflow-scheduler-1 airflow dags trigger plugin_hook_dag
```

## 🔧 Troubleshooting

### Common Issues:

1. **Plugin not loading:**
   ```bash
   # Check plugin directory permissions
   chmod -R 755 plugins/
   
   # Check logs
   docker logs airflow-elk-pro-airflow-scheduler-1 | grep -i plugin
   ```

2. **Connection issues:**
   ```bash
   # Test network connectivity
   docker exec airflow-elk-pro-airflow-scheduler-1 ping es01
   
   # Test Elasticsearch connection
   docker exec airflow-elk-pro-airflow-scheduler-1 curl -v https://es01:9200 -k
   ```

3. **SSL certificate issues:**
   - Set `"verify_certs": false` in connection extra
   - Or add CA certificate to containers

4. **Authentication issues:**
   ```bash
   # Verify credentials
   docker exec airflow-elk-pro-es01-1 curl -u elastic:your_elastic_password https://localhost:9200 -k
   ```

## 📊 Monitoring

Check DAG execution:
```bash
# List DAG runs
docker exec airflow-elk-pro-airflow-scheduler-1 airflow dags list-runs plugin_hook_dag

# View task logs
docker exec airflow-elk-pro-airflow-scheduler-1 airflow tasks list plugin_hook_dag
```

