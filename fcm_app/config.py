import yaml
import sys
import redis
from arango import ArangoClient, AQLQueryExecuteError
import psycopg2

import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

config = dict()

with open("etc/conf.yaml", 'r') as yamlconf:
    try:
        config = yaml.load(yamlconf)
    except yaml.YAMLError as exc:
        print(exc)
        exit()

print(config)

redis_conn = None
arango_client = None
arango_conn = None
pg_conn = None

try:
    # REDIS
    redis_conn = redis.Redis(db=config["queue"]["BATCHDB"], decode_responses=True, host=config['queue']['redis_host'])

    # ARANGO
    arango_client = ArangoClient(protocol='http', host=config["arango"]["host"], port=config["arango"]["port"])
    arango_conn = arango_client.db(config["arango"]["db"], username=config["arango"]["username"], password=config["arango"]["password"])

    # POSTGRES
    pg_conn = psycopg2.connect(config["pg"]["connstr"])
except Exception as e:
    print("oops cant lioad smthing:", e)


streaming_conf = dict()
with open("etc/streaming.yaml", 'r') as yamlconf:
    try:
        streaming_conf = yaml.load(yamlconf)
    except yaml.YAMLError as exc:
        print(exc)
        exit()