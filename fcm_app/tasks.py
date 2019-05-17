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
    print("got batch of events:", len(events))

    try:
        save2arango(events)
        #print("arango is ok\nsaving2pg:")
        save2pg(events)
    except Exception as e:
        print("Got exception while saving events: {}".format(e))
        


def save2arango(events):

    batch_db = arango_conn.begin_batch_execution(return_result=False)
    for e in events:
        batch_db.collection("stream").insert(*e['args'])

    # The commit must be called explicitly.
    batch_db.commit()


def save2pg(events):
    cur = pg_conn.cursor()
    ev_tpls = []
    for e in [ ev['args'][0] for ev in events]:
        #print(e['text'])
        author = e['author']
        if 'platform' not in author:
            author['platform'] = None
        #print(author)
        shared_post_author_id = author["shared_post_author_id"] if "shared_post_author_id" in author else None
        for k in [ "action_time","creation_time","event_type","action","attachments","geo","event_id","tags","text" ]:
            if k not in e:
                e[k] = None
        ev_tpls.append((
            author["id"], shared_post_author_id, e["action_time"], e["creation_time"], author["platform"], e["event_type"], e["action"],
            json.dumps(e["attachments"]), json.dumps(e["geo"]), json.dumps(e["event_id"]), e["tags"], e["text"]
        ))
    # print(ev_tpls)
    args_str = b",".join(cur.mogrify("(%s,%s,to_timestamp(%s),to_timestamp(%s),%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb,%s,%s)", e) for e in ev_tpls)
    inert_stmnt_prefix = """INSERT INTO {} (
        author_id, shared_post_author_id, action_time, creation_time, platform, event_type, action,
        attachments, geo, event_id, tags, event_text) VALUES
        """.format(config["pg"]["table"])
    # print("executing pg: " +  inert_stmnt_prefix + "{}".format(args_str))
    cur.execute(bytes(inert_stmnt_prefix, 'utf-8') + args_str)
    cur.close()
    pg_conn.commit()


def save2bigquery(ev):
    ...
