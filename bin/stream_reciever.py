
import os
import argparse
import fcm_app.vkstream
from fcm_app.config import config, streaming_cong, logging

parser = argparse.ArgumentParser(description="My parser")
parser.add_argument('--update-rules', dest='upd_rules', action='store_true')
parser.set_defaults(upd_rules=False)

parsed_args = parser.parse_args()
logging.debug("Parsed args: {}".format(parsed_args))


if parsed_args.upd_rules:
    logging.debug("Going to update rules.")
    rules = []
    streaming = streaming_cong

    glob_alt = " ".join(streaming['rules']['global_alters'])
    for tag, words in streaming['rules'].items():
        if tag == 'global_alters':
            continue
        for i, w in enumerate(words):
            if not w: # we should save tags order
                continue
            rule = {'tag': "{}{}".format(tag,i), 'value': w + " " + glob_alt }
            logging.debug("Rulle to update: {}".format(rule))
            fcm_app.vkstream.set_rule(rule)


    #logging.debug("Rules has been updated. {}".format(upd_rules))


logging.debug("Start listening to stream.")
fcm_app.vkstream.vkapi.start()


