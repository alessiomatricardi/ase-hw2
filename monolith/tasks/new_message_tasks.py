from ..background import celery

# list of tasks used when sending a new message

@celery.task
def add(x, y):
    return x + y