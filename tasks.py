from celery import Celery
from celery_batches import Batches

# ~/pyvenvs/bin/celery -A tasks worker --loglevel=info

app = Celery('tasks', broker='amqp://172.17.0.3:5672/')

@app.task(base=Batches, flush_every=7, flush_interval=10)
def save2arango(ev):
    print("saving 2 arango {} events: {}".format(len(ev), ev))
    return

@app.task(base=Batches, flush_every=100, flush_interval=10)
def save2bigquery(ev):
    print("saving 2 bigquery: {}".format(ev))
    return

@app.task(base=Batches, flush_every=100, flush_interval=10)
def save2postgres(ev):
    print("saving 2 pg: {}".format(ev))
    return
