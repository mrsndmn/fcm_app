
from vkstreaming import Streaming, getServerUrl, VkError
from fcm_app.config import config, logging
import time
from fcm_app.tasks import save_events

ACCEPTED_EVENT_TYPES = [ 'new', 'update' ]
MAX_CONNECT_TRIES = 20
CONNECT_ERR_SLEEP = 300

def set_rule(rule):
    try:
        vkapi.add_rules(rule['tag'], rule['value'])
    except VkError as e:
        print(e.error_code) #Код ошибки
        print(e.message) #Сообщение
        if e.error_code != 2001: # tag already exists
            raise e

def connect2stream():
    logging.info("trying to connect to stream")

    for i in range(MAX_CONNECT_TRIES):
        response = getServerUrl(config['vk']['secure_key'])
        try:
            api = Streaming(response["endpoint"], response["key"])
        except VkError as e:
            logging.error("Error [{}] while connectiong to stream: {}".format(e.error_code, e.message))
            time.sleep(CONNECT_ERR_SLEEP)
        break

    return api

vkapi = connect2stream()

@vkapi.stream
def stream2arango(stream_event):

    logging.debug("Got new event. Tags: {}".format(stream_event["tags"]))
    if stream_event["action"] not in ACCEPTED_EVENT_TYPES:
        return

    save_events.delay(stream_event)