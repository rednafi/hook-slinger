"""Module dedicated to spawn rq workers"""

from redis import Redis
from rq import Connection, Queue
from rq.worker import Worker

import config

listen = config.QUEUE_NAMES
redis_conn = Redis.from_url(config.REDIS_URL)

if __name__ == "__main__":
    with Connection(redis_conn):
        worker = Worker(map(Queue, listen))
        worker.work(with_scheduler=True)
