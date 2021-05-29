from main import celery


@celery.task(name='task.greet_user')
def greet():
    print("Task Called >>>>>")
    return "Task Called"
