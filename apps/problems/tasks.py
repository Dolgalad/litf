from celery import shared_task

@shared_task
def problem_submitted_task(problem):
    print("problem_submitted_task : {}".format(problem))

@shared_task
def problem_updated_task(problem):
    print("problem_updated_task : {}".format(problem))
