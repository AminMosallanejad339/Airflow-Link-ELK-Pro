#!/bin/bash

ELASTICSEARCH_URL="http://localhost:9200"

INDEX="sahamyab2"
DOC_TYPE="_doc"

for file in ./*.json; do

    DOC_ID=$(basename "$file" | cut -d. -f1)
    # basename "$file" extract the name  of the file
    # cut -d. -f1 -d. means split based on . and
    # -f1 means get the first item.

    DATA=$(cat "$file")

    curl -X PUT "$ELASTICSEARCH_URL/$INDEX/$DOC_TYPE/$DOC_ID" -H 'Content-Type: application/json' -d "$DATA"
done

##################################################################################
# 🚩🚩🚩 Now you can check the Kibana to see if the records have been inserted 😎

# GET /sahamyab/_search
# {
#   "query": {
#     "match_all": {}
#   }
# }