
from pyArango.connection import *
from vkstreaming import Streaming, getServerUrl
import os
import yaml
import logging
import sys
import argparse

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

parser = argparse.ArgumentParser(description="My parser")
parser.add_argument('--update-rules', dest='upd_rules', action='store_true')
parser.set_defaults(upd_rules=False)

parsed_args = parser.parse_args()
logging.debug("Parsed args: {}".format(parsed_args))


config = dict()

with open("etc/conf.yaml", 'r') as yamlconf:
    try:
        config = yaml.load(yamlconf)
    except yaml.YAMLError as exc:
        print(exc)
        exit()

print(config)

conn = Connection(arangoURL=config["arango"]["url"], username=config["arango"]["username"], password=config["arango"]["password"], verbose=True)
# print(conn)
def init_db():
    db = None
    dbname = config["arango"]["db"]
    if not conn.hasDatabase(dbname):
        db = conn.createDatabase(name=dbname)
    db = conn[dbname]

    for coll in ["stream", "posts"]:
        if not db.hasCollection(coll):
            db.createCollection(name=coll)

    return db


db = init_db()
stream_coll = db["stream"]

response = getServerUrl(config['vk']['secure_key'])
vkapi = Streaming(response["endpoint"], response["key"])

logging.debug("Going to update rules.")

if parsed_args.upd_rules:
    rules = []
    streaming = {}
    with open("etc/streaming.yaml", 'r') as yamlconf:
        try:
            streaming = yaml.load(yamlconf)
        except yaml.YAMLError as exc:
            print(exc)
            exit()

    for tag, words in streaming['rules'].items():
        for i, w in enumerate(words):
            if not w: # we should save tags order
                continue
            rules.append({'tag': "{}{}".format(tag,i), 'value': w })


    logging.debug("Rulles to update: {}".format(rules))
    upd_rules = vkapi.update_rules(rules)
    #logging.debug("Rules has been updated. {}".format(upd_rules))

@vkapi.stream
def stream2arango(event):
    logging.debug("Got new event. Tags: {}".format(event["tags"]))
    ev = stream_coll.createDocument(event)
    ev.save()

logging.debug("Start listening.")
vkapi.start()


