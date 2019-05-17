import json
import time

from tasktiger import TaskTiger

from fcm_app.config import arango_conn, config, logging, arango_conn, redis_conn, pg_conn

tiger = TaskTiger(connection=redis_conn, config={
    'BATCH_QUEUES': {
        'batch': config["queue"]["QBATCH_SIZE"],
        'SELECT_BATCH_TIMEOUT': config["queue"]["QDELAY"]
    }
})
# tiger.log.setLevel(logging.DEBUG)

# /home/d.tarasov/workSpace/py3-venvs/fcm_app/bin/tasktiger -h 192.168.48.2
# >>> fcm_app.tasks.tiger.delay(fcm_app.tasks.batch_task, args=(1,), kwargs={'n':1})

@tiger.task(queue='batch', batch=True)
def save_event(events):
    print("got batch of events:", events)

    try:
        save2arango(events)
        save2pg(events)
    except Exception as e:
        print("Got exception while saving events: ", e)


def save2arango(events):

    batch_db = arango_conn.begin_batch_execution(return_result=False)
    for e in range(events):
        batch_db.collection("stream").insert(e)

    # The commit must be called explicitly.
    batch_db.commit()


def save2pg(events):
    cur = pg_conn.cursor()
    ev_tpls = []
    for e in events:
        author = e['author']
        shared_post_author_id = author["shared_post_author_id"] if shared_post_author_id in author else None

        ev_tpls.append((
            author["id"], shared_post_author_id, e["action_time"], e["creation_time"], author["platform"], e["event_type"], e["action"],
            json.dumps(e["attachments"]), e["geo"], e["event_id"], e["tags"], e["event_text"]
        ))

    args_str = ','.join(cur.mogrify("(%d,%d,%d,to_timestamp(%d),to_timestamp(%d),%d,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb,%s,%s)", e) for e in ev_tpls)
    inert_stmnt_prefix = """INSERT INTO {} (
        author_id, shared_post_author_id, action_time, creation_time, platform, event_type, action,
        attachments, geo, event_id, tags, event_text) VALUES
        """.format(config["pg"]["table"])
    cur.execute(inert_stmnt_prefix + args_str)
    cur.close()
    pg_conn.commit()


def save2bigquery(ev):
    ...
