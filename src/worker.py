import os
import redis
from rq import Worker, Queue, Connection

listen = ['default']

redis_port = os.getenv('REDIS_PORT_6379_TCP_PORT', '6379')
redis_host = os.getenv('REDIS_PORT_6379_TCP_ADDR', 'localhost')
redis_url = 'redis://{}:{}'.format(redis_host, redis_port)

print 'Connecting to redis at {}'.format(redis_url)
conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
