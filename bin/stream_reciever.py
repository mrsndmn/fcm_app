
from pyArango.connection import *
from vkstreaming import Streaming, getServerUrl

import os
import sys
import time

import yaml
import logging
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

vkapi = connect2stream()

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

    glob_alt = " ".join(streaming['rules']['global_alters'])
    for tag, words in streaming['rules'].items():
        if tag == 'global_alters':
            continue
        for i, w in enumerate(words):
            if not w: # we should save tags order
                continue
            rules.append({'tag': "{}{}".format(tag,i), 'value': w + " " + glob_alt })


    logging.debug("Rulles to update: {}".format(rules))
    upd_rules = vkapi.update_rules(rules)
    #logging.debug("Rules has been updated. {}".format(upd_rules))


ACCEPTED_EVENT_TYPES = [ 'new', 'update' ]
MAX_CONNECT_TRIES = 20
CONNECT_ERR_SLEEP = 300

def connect2stream():
    logging.info("trying to connect to stream")

    for i in range(MAX_CONNECT_TRIES):
        response = getServerUrl(config['vk']['secure_key'])
        try:
            api = Streaming(response["endpoint"], response["key"])
        except vkapi.VkError as e:
            logging.error("Error [{}] while connectiong to stream: {}".format(e.error_code, e.message))
            time.sleep(CONNECT_ERR_SLEEP)
        break

    return api


@vkapi.stream
def stream2arango(stream_event):
    if stream_event['code'] == 300:
        logging.info("Streaming api is going to shutdown")
        vkapi.stop()
        connect2stream()
        return

    logging.debug("Got new event. Tags: {}".format(stream_event["tags"]))
    if stream_event["action"] not in ACCEPTED_EVENT_TYPES:
        return


    ev = stream_coll.createDocument(stream_event)
    ev.save()

logging.debug("Start listening.")
vkapi.start()


