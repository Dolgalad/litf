from celery import shared_task

from libs.code.manager import CodeManager
from libs.file.manager import FileManager
@shared_task
def code_submitted_task(code_id):
    print("code_submitted_task : {}".format(code_id))
    CodeManager.check_code_status(code_id)

@shared_task
def code_updated_task(code_id):
    print("code_updated_task : {}".format(code_id))
    CodeManager.check_code_status(code_id)

@shared_task
def datafile_submitted_task(datafile):
    print("datafile_submitted_task : {}".format(datafile))
    FileManager.check_file_flags(datafile)

@shared_task
def datafile_updated_task(datafile):
    print("datafile_updated_task : {}".format(datafile))
    FileManager.check_file_flags(datafile)
