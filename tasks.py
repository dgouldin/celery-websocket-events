import time
import os

import anyjson
import celery
import redis

redis_url = os.environ.get('REDISCLOUD_URL') or 'redis://localhost:6379'
redis_client = redis.from_url(redis_url)
app = celery.Celery('tasks', backend=redis_url, broker=redis_url)

class StatusTask(celery.Task):
    abstract = True

    # Celery UUID of the root task which caused this one to be run
    root_id = None

    def run(self, *args, **kwargs):
        self.root_id = kwargs.get('root_id', self.request.id)

    def status(self, status, data=None):
        redis_client.publish(self.root_id, anyjson.dumps({
            'status': status,
            'data': data,
        }));

    def after_return(self, status, retval, task_id, *args, **kwargs):
        self.status(status, {'task_id': task_id})

    def delay_subtask(self, task_instance, *args, **kwargs):
        kwargs['root_id'] = self.root_id
        result = task_instance.subtask().delay(*args, **kwargs)
        self.status('SUBTASK', {'task_id': result.id})


class MyTask(StatusTask):
    def run(self, *args, **kwargs):
        super(MyTask, self).run(*args, **kwargs)

        time.sleep(3)
        self.delay_subtask(MySubtask())
        return True


class MySubtask(StatusTask):
    def run(self, *args, **kwargs):
        super(MySubtask, self).run(*args, **kwargs)

        time.sleep(3)
        return True
