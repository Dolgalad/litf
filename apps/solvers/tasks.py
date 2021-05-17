from celery import shared_task

from libs.code.manager import CodeManager
@shared_task
def solver_submitted_task(solver_id):
    print("solver_submitted_task : {}".format(solver_id))
    status=CodeManager.check_solver_status(solver_id)
    print("CodeManager.check_solver_status(solver_id)={}".format(status))
@shared_task
def solver_updated_task(solver_id):
    print("solver_updated_task : {}".format(solver_id))
    status=CodeManager.check_solver_status(solver_id)
    print("CodeManager.check_solver_status(solver_id)={}".format(status))

@shared_task
def solution_request_task(solution_request):
    print("solution_request_task : {}".format(solution_request))
    # check the solver definition
    
