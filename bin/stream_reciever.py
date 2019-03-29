
from pyArango.connection import *
from vkstreaming import Streaming, getServerUrl
import os
import yaml
import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

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
        if not db.hasCollection(coll):
            db.createCollection(name=coll)

    return db


db = init_db()
stream_coll = db["stream"]

response = getServerUrl(config['vk']['secure_key'])
vkapi = Streaming(response["endpoint"], response["key"])

logging.debug("Going to update rules.")

rules = []
streaming = {}
with open("etc/streaming_rules.yaml", 'r') as yamlconf:
    try:
        streaming = yaml.load(yamlconf)
    except yaml.YAMLError as exc:
        print(exc)
        exit()

for tag, words in streaming['rules'].items():

    rule = {'tag': tag, 'value': " ".join(words) }
    rules.append(rule)

logging.debug("Rulles to update: {}".format(rules))
upd_rules = vkapi.update_rules(rules)
logging.debug("Rules has been updated. {}".format(upd_rules))


@vkapi.stream
def stream2arango(event):
    logging.debug("Got new event: {}".format(event))
    ev = stream_coll.createDocument(event)
    ev.save()
    logging.debug("Event saved: {}".format(ev))

logging.debug("Start listening.")
vkapi.start()


