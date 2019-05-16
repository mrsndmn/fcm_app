import json
import time

import time

from tasktiger import RetryException, TaskTiger
from tasktiger.schedule import periodic
from tasktiger.retry import fixed

import fcm_app.config as config
from fcm_app.config import arango_conn, config, logging, arangodb, redis_conn

tiger = TaskTiger(connection=redis_conn, config={
    'BATCH_QUEUES': {
        'batch': config["queue"]["QBATCH_SIZE"],
    }
})
# tiger.log.setLevel(logging.DEBUG)

# /home/d.tarasov/workSpace/py3-venvs/fcm_app/bin/tasktiger -h 192.168.48.2
# >>> fcm_app.tasks.tiger.delay(fcm_app.tasks.batch_task, args=(1,), kwargs={'n':1})

@tiger.task(queue='batch', batch=True) # , schedule=periodic(seconds=5)
def batch_task(params, n=1):
    for task in tiger.current_tasks:
        print("processing task:", task.id)
    print("got batch task", params)
    time.sleep(1)


stream_coll = arangodb["stream"]
def save2arango(ev):
    ev = stream_coll.createDocument(ev)
    ev.save()


def save2pg(ev):
    ...


def save2bigquery(ev):
    ...
