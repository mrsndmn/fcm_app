from celery import Celery
from celery_batches import Batches
from fcm_app.config import arango_conn, config, logging, arangodb

# ~/pyvenvs/bin/celery -A tasks worker --loglevel=info --autoscale=5,2

app = Celery('tasks', broker='amqp://172.17.0.3:5672/')

@app.task(base=Batches, flush_every=7, flush_interval=10)
def save_events(events):
    print("saving {} events".format(len(events)))
    for ev in events:
        continue

# print(arango_conn)

stream_coll = arangodb["stream"]

def save2arango(ev):
    ev = stream_coll.createDocument(ev)
    ev.save()

def save2pg(ev):
    ...

def save2bigquery(ev):
    ...