from celery import shared_task

from libs.code.manager import CodeManager
from libs.file.manager import FileManager
@shared_task
def code_submitted_task(code):
    print("code_submitted_task : {}".format(code))
    CodeManager.check_code_status(code)

@shared_task
def code_updated_task(code):
    print("code_updated_task : {}".format(code))
    CodeManager.check_code_status(code)

@shared_task
def datafile_submitted_task(datafile):
    print("datafile_submitted_task : {}".format(datafile))
    FileManager.check_file_flags(datafile)

@shared_task
def datafile_updated_task(datafile):
    print("datafile_updated_task : {}".format(datafile))
    FileManager.check_file_flags(datafile)
