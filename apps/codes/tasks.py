from celery import shared_task
from celery.schedules import crontab
from litf.celery import app

from libs.code.manager import CodeManager
from libs.file.manager import FileManager
from libs.code import status

from apps.codes.models import CodeModel, ExecutionResultModel
from apps.solvers.models import SolverExecutionResultModel
from libs.process import kill_recursive, get_child_pids

import socket

@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, run_next_pending_execution.s(), name="hello_period")
@app.task
def test(arg):
    print(arg)

@app.task
def run_next_pending_execution():
    # check for missing integrity checks
    for er in ExecutionResultModel.objects.all():
        if not er.flags=="integrity":
            if er.status==status.CodeExecutionStatus.PENDING:
                hic=er.implementation.has_integrity_check()
                if hic:
                    # check if the result is linked to a solver run
                    solver_runs=SolverExecutionResultModel.objects.filter(result=er)
                    if len(solver_runs):
                        S=solver_runs[0]
                        fl_names=["solver","input_type","output_type","postprocess"]
                        solver_implementation_checked=S.solver.implementation.has_integrity_check()
                        if S.solver.problem.input_type:
                            problem_input_type_checked=S.solver.problem.input_type.has_integrity_check()
                        else:
                            problem_input_type_checked=True
                        if S.solver.problem.output_type:
                            problem_output_type_checked=S.solver.problem.output_type.has_integrity_check()
                        else:
                            problem_output_type_checked=True
                        pp_names=[pp.name for pp in S.solver.problem.postprocess.all()]
                        pp_state=[pp.has_integrity_check() for pp in S.solver.problem.postprocess.all()]
                        problem_postprocess_all_checked=all(pp_state)
                        fl=[solver_implementation_checked,\
                                          problem_input_type_checked,\
                                          problem_output_type_checked,\
                                          problem_postprocess_all_checked]
                        ready_to_run=all(fl)
                        if ready_to_run:
                            CodeManager.execute_problem_solver_run(S)
                            return
                        else:
                            print("Problem integrity unchecked")
                            print("\tproblem  : {}({})".format(S.solver.problem.name, S.solver.problem.id))
                            print("\tfl_names : {}".format(fl_names))
                            print("\tfl_state : {}".format(fl))
                            print("\tpp names : {}".format(pp_names))
                            print("\tpp state : {}".format(pp_state))
                        continue
                    else:
                        CodeManager.codemodel_execute_result(er.implementation,er)
                        return 
                else:
                    print("WARNING : waiting for integrity check on CodeModel {}({})".format(er.implementation.name, er.implementation.id))


                #CodeManager.codemodel_execute_result(er.implementation,er)
                # check if integrity check has been done for this model
                continue
    print("TASK RUN_NEXT_PENDING_EXECUTION : Nothing to do")


@shared_task
def code_submitted_task(code_id):
    print("code_submitted_task : {}".format(code_id))
    CodeManager.check_code_status(code_id)
    # check if the code status of all code objects that depend on the current code

@shared_task
def code_updated_task(code_id, **kwargs):
    # check status of dependencies
    #    if has_invalid_dependency : set status to DEPENDENCY_ERROR

    # get list of code objects that depend on this item
    # interrupt all executions that involve an item in the dependance graph
    # clear set state to PENDING for all items in the dependency graph
    # starting from the root, execute integrity check of the graph
    from litf.celery import app
    i=app.control.inspect()
    active_tasks=i.active()

    # get codemodel
    cm=CodeModel.objects.get(id=code_id)

    # kill all code_update_task tasks that involve a CodeModel object that depends on the current object
    CELERY_TASK_LIST="celery@{}".format(socket.gethostname())
    print("CELERY_TASK_LIST : {}".format(CELERY_TASK_LIST))
    print("active tasks keys : {}".format([k for k in active_tasks]))
    task_list=[]
    if CELERY_TASK_LIST in active_tasks:
        task_list=active_tasks[CELERY_TASK_LIST]
    for task in active_tasks["celery@mademu"]:
        # check if this task conflicts with the current task i.e. task involves code that depends on
        # current code
        if task["id"]!=code_updated_task.request.id and task["name"]=="apps.codes.tasks.code_updated_task":
            ncm=CodeModel.objects.get(id=task["args"][0])
            if ncm.depends(cm):
                pids=get_child_pids(task["worker_pid"])
                # hard kill task and all children
                app.control.revoke(task["id"], terminate=True)
                kill_recursive(task["worker_pid"])
                for p in pids:
                    kill_recursive(p)

    # set all executions to pending for this model and all its dependants
    CodeManager.codemodel_set_execution_pending(code_id)
    for d in cm.get_dependants():
        CodeManager.codemodel_set_execution_pending(d.id)
    # check integrity of current code then do the same for all its dependencies
    # check codes status
    CodeManager.check_code_status(code_id)
    # check codes status for all depending codes
    for d in cm.get_dependants():
        CodeManager.check_code_status(d.id)

    # execute results that were set to pending
    #CodeManager.execute_pending_results(code_id)
    # check code status for all code depending on current code
    #CodeManager.check_code_dependants(code_id)

@shared_task
def datafile_submitted_task(datafile):
    print("datafile_submitted_task : {}".format(datafile))
    FileManager.check_file_flags(datafile)

@shared_task
def datafile_updated_task(datafile):
    print("datafile_updated_task : {}".format(datafile))
    FileManager.check_file_flags(datafile)
