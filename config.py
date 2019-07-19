from celery import Celery
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	SECRET_KEY = 'SECRET'
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app/notes.sqlite')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	CELERY_BROKER_URL = 'redis://localhost:6379/0'
	CELERY_RESULT_BACKEND = 'db+sqlite:///' + os.path.join(basedir, 'app/notes.sqlite')


def make_celery(app):
	celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])
	celery.conf.update(app.config)
	TaskBase = celery.Task

	class ContextTask(TaskBase):
		abstract = True

		def __call__(self, *args, **kwargs):
			with app.app_context():
				return TaskBase.__call__(self, *args, **kwargs)

	celery.Task = ContextTask
	return celery