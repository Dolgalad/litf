from celery import shared_task

from libs.code.manager import CodeManager
from libs.file.manager import FileManager
@shared_task
def code_submitted_task(code_id):
    print("code_submitted_task : {}".format(code_id))
    CodeManager.check_code_status(code_id)
    # check if the code status of all code objects that depend on the current code

@shared_task
def code_updated_task(code_id):
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
