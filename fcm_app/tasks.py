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
def save_event(events, nopg=False, noarango=False):
    print("got batch of events:", len(events))

    try:
        if not noarango:
            save2arango(events)
        #print("arango is ok\nsaving2pg:")
        if not nopg:
            save2pg(events)
    except Exception as e:
        print("Got exception while saving events: {}".format(e))
        raise(e)



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
            elif isinstance(e[k], str):
                e[k] = e[k].replace('\x00', '')

        attachments = e['attachments']
        attachment_text = ''
        for a in attachments:
            print(a)
            if attachment_text: attachment_text += ' '
            if   a['type'] == 'link':         attachment_text += a['link']['title'] + a['link']['description']
            elif a['type'] == 'video':        attachment_text += a['video']['title'] + a['video']['description']
            elif a['type'] == 'audo':         attachment_text += a['audo']['title'] + a['audo']['artist']
            elif a['type'] == 'album':        attachment_text += a['album']['title'] + a['album']['text']
            elif a['type'] == 'note':         attachment_text += a['note']['title'] + a['note']['text']
            elif a['type'] == 'doc':          attachment_text += a['doc']['title']
            elif a['type'] == 'photo':        attachment_text += a['photo']['text']
            elif a['type'] == 'page':         attachment_text += a['page']['title']
            elif a['type'] == 'poll':         attachment_text += a['poll']['question']
            elif a['type'] == 'podcast':      attachment_text += a['podcast']['title']
            elif a['type'] == 'podcast':      attachment_text += a['podcast']['title']
            elif a['type'] == 'market_album': attachment_text += a['market_album']['title']
            else: print('unknown type:', a)

        ev_tpls.append((
            author["id"], shared_post_author_id, e["action_time"], e["creation_time"], author["platform"], e["event_type"], e["action"],
            json.dumps(e["geo"]).rstrip('\0'), json.dumps(e["event_id"]).rstrip('\0'), e["tags"], e["text"],attachment_text
        ))
    # print(ev_tpls)
    try:
        args_str = b",".join(cur.mogrify("(%s,%s,to_timestamp(%s),to_timestamp(%s),%s,%s,%s,%s::jsonb,%s::jsonb,%s,%s,%s)", e) for e in ev_tpls)
        inert_stmnt_prefix = """INSERT INTO {} (
            author_id, shared_post_author_id, action_time, creation_time, platform, event_type, action,
            geo, event_id, tags, event_text,attachment_text) VALUES
            """.format(config["pg"]["table"])
        print("executing pg: " +  inert_stmnt_prefix + "{}".format(args_str))
        cur.execute(bytes(inert_stmnt_prefix, 'utf-8') + args_str)
        cur.close()
        print("ok saved to pg")
        pg_conn.commit()
    except Exception as e:
        # print("pgerr: ", e, ev_tpls)
        pg_conn.rollback()
        raise e


def save2bigquery(ev):
    ...
