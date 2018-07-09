import logging
import redis
from rq import Worker, Queue, Connection
import os
from timeouts import JobTimeoutException

listen = ['high']

redis_url = str(os.environ.get("REDISTOGO_URL", None))

conn = redis.from_url(redis_url)


# catch the JobTimeoutException
def timeout_handler(job, exc_type, exc_value, traceback):
    if isinstance(exc_value, JobTimeoutException):
        print("TIMEOUT HAPPEN AND I CAUGHT IT!!")
        q = Queue
        q.enqueue_job(job)

        # return True to stop chaining exc handlers
        return True

    return False


if __name__ == '__main__':
    try:
        with Connection(conn):
            worker = Worker(map(Queue, listen))
            worker.push_exc_handler(timeout_handler)

            worker.work()
    except:
        logging.exception('')
