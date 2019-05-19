
import os
import argparse
import fcm_app.vkstream
from fcm_app.config import config, streaming_conf, logging, pg_conn

parser = argparse.ArgumentParser(description="My parser")
parser.add_argument('--update-rules', dest='upd_rules', action='store_true')
parser.set_defaults(upd_rules=False)

parsed_args = parser.parse_args()
logging.debug("Parsed args: {}".format(parsed_args))


if parsed_args.upd_rules:
    logging.debug("Going to update rules.")
    rules = []
    streaming = streaming_conf
    fcm_app.vkstream.vkapi.del_all_rules()
    glob_alt = " ".join(streaming['rules']['global_alters'])
    cur = pg_conn.cursor()
    cur.execute("SELECT * FROM stream_rules")
    rules = cur.fetchall()
    for rule in rules:

        rule = {'tag': str(rule[0]), 'value': rule[1] + " " + glob_alt }
        logging.debug("Rulle to update: {}".format(rule))
        fcm_app.vkstream.set_rule(rule)

logging.debug("Start listening to stream.")
fcm_app.vkstream.vkapi.start()


