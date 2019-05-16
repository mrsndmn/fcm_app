
from tasktiger import TaskTiger
import redis

redis_conn = redis.Redis(db=0, decode_responses=True, host="192.168.48.2")
tiger = TaskTiger(connection=redis_conn, config={
    'BATCH_QUEUES': {
        'batch': 10,
    }
})

@tiger.task(queue='batch', batch=True)
def batch_task(params):
    for task in tiger.current_tasks:
        print("processing task:", task.id)
    print("got batch task", params)

