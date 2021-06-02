from celery import shared_task

from libs.code.manager import CodeManager
from libs.file.manager import FileManager

from apps.codes.models import CodeModel
from libs.process import kill_recursive, get_child_pids

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
    print(code_updated_task.request.id)
    for task in active_tasks["celery@mademu"]:
        print("TASK : {} {} {}".format(task["id"], task["name"], task["args"]))
        print([k for k in task])
        # check if this task conflicts with the current task i.e. task involves code that depends on
        # current code
        if task["id"]!=code_updated_task.request.id and task["name"]=="apps.codes.tasks.code_updated_task":
            ncm=CodeModel.objects.get(id=task["args"][0])
            if ncm.depends(cm):
                print("Terminate task : {}".format(task["id"]))
                print("task pids : {}".format(get_child_pids(task["worker_pid"])))
                pids=get_child_pids(task["worker_pid"])
                # hard kill task and all children
                app.control.revoke(task["id"], terminate=True)
                kill_recursive(task["worker_pid"])
                for p in pids:
                    kill_recursive(p)

    print("code_updated_task : {}".format(code_id))
    CodeManager.codemodel_set_execution_pending(code_id)
    # check codes status
    CodeManager.check_code_status(code_id)
    # execute results that were set to pending
    CodeManager.execute_pending_results(code_id)
    # check code status for all code depending on current code
    CodeManager.check_code_dependants(code_id)

@shared_task
def datafile_submitted_task(datafile):
    print("datafile_submitted_task : {}".format(datafile))
    FileManager.check_file_flags(datafile)

@shared_task
def datafile_updated_task(datafile):
    print("datafile_updated_task : {}".format(datafile))
    FileManager.check_file_flags(datafile)
