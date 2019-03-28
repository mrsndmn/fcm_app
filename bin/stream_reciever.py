
from pyArango.connection import *
from vkstreaming import Streaming
import os
import yaml

config = dict()

with open("etc/conf.yaml", 'r') as yamlconf:
    try:
        config = yaml.load(yamlconf)
    except yaml.YAMLError as exc:
        print(exc)
        exit()

print(config)

conn = Connection(arangoURL=config["arango"]["url"])

def init_db():
    db = None
    dbname = config["arango"]["db"]
    try:
        db = conn[dbname]
    except KeyError:
        db = conn.createDatabase(name=dbname)

    for coll in ["stream", "posts"]:
        try:
            db[coll]
        except KeyError:
            db.createCollection(name=coll)

    return db


db = init_db()


vkapi = Streaming(config["vk"]["stream"]["api_host"], )
