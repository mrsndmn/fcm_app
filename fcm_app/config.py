import yaml
import sys
from pyArango.connection import *
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

# ARANGO
arango_conn = Connection(arangoURL=config["arango"]["url"], username=config["arango"]["username"], password=config["arango"]["password"], verbose=True)
def init_arangodb():
    db = None
    dbname = config["arango"]["db"]
    if not arango_conn.hasDatabase(dbname):
        db = arango_conn.createDatabase(name=dbname)
    db = arango_conn[dbname]

    for coll in ["stream", "posts"]:
        if not db.hasCollection(coll):
            db.createCollection(name=coll)

    return db

arangodb = init_arangodb()

# POSTGRES



streaming_cong = dict()

with open("etc/streaming.yaml", 'r') as yamlconf:
    try:
        streaming = yaml.load(yamlconf)
    except yaml.YAMLError as exc:
        print(exc)
        exit()