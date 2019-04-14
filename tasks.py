from celery import Celery

app = Celery('tasks', broker='amqp://172.17.0.3:5672/')

@app.task
def add(x, y):
    print("{} + {} = {}".format(x, y, x + y))
    return x + y

