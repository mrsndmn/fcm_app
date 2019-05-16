from fcm_app.config import redis_conn
import fcm_app.tasks

fcm_app.tasks.tiger.run_worker()

