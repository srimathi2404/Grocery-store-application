from celery import Celery, Task
import redis
import celery_config
from dotenv import load_dotenv
import os
load_dotenv()
redis_host = os.getenv('CACHE_REDIS_HOST')
CACHE_REDIS_PORT= os.getenv('CACHE_REDIS_PORT')
CACHE_REDIS_PASSWORD= os.getenv('CACHE_REDIS_PASSWORD')

r = redis.Redis(
  host=redis_host,
  port=CACHE_REDIS_PORT,
  password=CACHE_REDIS_PASSWORD)

def celery_init_app(app):
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)


    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(celery_config)
    return celery_app

from celery import Celery
from flask import current_app as app

celery = Celery('Application Jobs')
celery.conf.enable_utc=False
celery.conf.timezone  = 'Asia/Kolkata'
class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args,**kwargs)