from celery import Celery
from celery.contrib.batches import Batches

# ~/pyvenvs/bin/celery -A tasks worker --loglevel=info --autoscale=5,2

app = Celery('tasks', broker='amqp://172.17.0.3:5672/')

@app.task(base=Batches, flush_every=100, flush_interval=10)
def save2arango(ev):
    print("saving 2 arango: {}".format(ev))
    return

@app.task(base=Batches, flush_every=100, flush_interval=10)
def save2bigquery(ev):
    print("saving 2 bigquery: {}".format(ev))
    return

@app.task(base=Batches, flush_every=100, flush_interval=10)
def save2postgres(ev):
    print("saving 2 pg: {}".format(ev))
    return