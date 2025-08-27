# A connection from Airflow to Elasticsearch

## Install Airflow by Docker

```bash
mkdir -p ./dags ./logs ./plugins ./config

echo -e "AIRFLOW_UID=$(id -u)" > .env

AIRFLOW_UID=50000

docker compose up airflow-init

docker compose up
```

Reference: https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html 



## Create `tweets` index and insert some data  into it

- check ‍‍‍‍`localhost:9200`
- go to **Kibana** dashboard : localhost:5601
- ‌from main menu, open `Dev Tools` and run 

```bash
PUT tweets/_doc/1
{
  "id" : 123 ,
  "content": "چندمین دوره مهندسی داده دکتر محمد فزونی" ,
  "date" : "2025/08/24"
}

PUT tweets/_doc/2
{
  "id" : 143 ,
  "content": "داده های شبکه اجتماعی را جمع کن" ,
  "date" : "2025/08/24"
}

PUT tweets/_doc/3
{
  "id" : 1234 ,
  "content": "حجم داده هایی که نوع بشر در سال های اخیر در حال ایجاد و تولید است در حال سر به فلک کشیدن است",
  "date" : "2025/08/24"
}

PUT tweets/_doc/4
{
  "id" : 12345 ,
  "content": "مهندسی عالیست عزیزان من",
  "date" : "2025/08/23"
}
```



## Search your index in `Elasticsearch`

```bash
GET tweets/_doc/1

#################################
GET _search
{
  "query": {
    "match_all": {}
  }
}

#################################
GET /sahamyab/_search
{
  "query": {
    "match_all": {}
  }
}
```



## Create a connection from `airflow` to `Elasticsearch`

- Set :  `AIRFLOW__CORE__RELOAD_ON_PLUGIN_CHANGE: 'true'` in `docker-compose` file .

- Create `elasticsearch_default` connection
  - name : 	`elasticsearch_default` 
  - Conn Type : `elasticsearch`
  - Host : `elastic`search #🚩Pay much attention to this
  - Schema : `tweets`
  - port : `9200`
