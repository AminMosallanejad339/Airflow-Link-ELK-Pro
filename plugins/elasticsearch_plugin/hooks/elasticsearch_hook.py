from airflow.hooks.base import BaseHook
from elasticsearch import Elasticsearch
from airflow.utils.log.logging_mixin import LoggingMixin

class ElasticsearchHook(BaseHook, LoggingMixin):
    def __init__(self, elasticsearch_conn_id='elasticsearch_default'):
        # گرفتن connection از Airflow
        conn = self.get_connection(elasticsearch_conn_id)

        scheme = conn.extra_dejson.get('scheme', 'http')
        verify_certs = conn.extra_dejson.get('verify_certs', True)

        # ساخت host list
        hosts = [f"{scheme}://{conn.host}:{conn.port}"]

        # config برای احراز هویت
        conn_config = {}
        if conn.login and conn.password:
            conn_config['http_auth'] = (conn.login, conn.password)

        # اضافه کردن verify_certs
        conn_config['verify_certs'] = verify_certs

        # ایجاد client Elasticsearch
        self.es = Elasticsearch(hosts, **conn_config)
        self.index = conn.schema

    def get_conn(self):
        return self.es

    def get_index(self):
        return self.index

    def set_index(self, index):
        self.index = index

    def search(self, index, body):
        self.set_index(index)
        return self.es.search(index=self.index, body=body)

    def create_index(self, index, body=None):
        self.set_index(index)
        return self.es.indices.create(index=self.index, body=body or {})

    def add_doc(self, index, doc):
        self.set_index(index)
        return self.es.index(index=self.index, body=doc)

    def info(self):
        return self.es.info()

    def ping(self):
        return self.es.ping()
