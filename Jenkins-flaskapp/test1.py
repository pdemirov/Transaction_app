import time
from elasticsearch import Elasticsearch, ConnectionError as ESConnectionError

es = None
for attempt in range(10):
    try:
        es = Elasticsearch(["http://elasticsearch:9200"])
        if es.ping():
            print("Connected to Elasticsearch")
            break
    except ESConnectionError as e:
        print(f"Attempt {attempt + 1} failed: {e}")
        time.sleep(5)
else:
    raise ESConnectionError("Could not connect to Elasticsearch after several attempts")

if es:
    print(es.info())