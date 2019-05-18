from fcm_app.config import arango_conn, pg_conn, config, logging
import fcm_app.tasks

import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

import json
import time

step = 500

errors = 0
for cur in range(72125,2000000, step):
    print(cur)
    try:
        acursor = arango_conn.aql.execute('FOR doc IN stream limit @offset,@limit RETURN doc', bind_vars={'limit': step, 'offset': cur})
        fcm_app.tasks.save2pg([ { 'args': [ e ] } for e in acursor ])
        # time.sleep(0.1)
    except Exception as e:
        print("got exception!", e)
        # raise e
        errors += 1

print(errors)

