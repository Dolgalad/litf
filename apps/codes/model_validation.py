"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:brief: functions for checking the validity of this apps models
"""
from .models import CodeModel

# code management
from libs.code.manager import CodeManager

def codemodel_code_valid(post_data):
    if not "code" in post_data:
        print("codemodel_code_valid : request data missing 'code' data")
        return False
    # check for syntax errors
    if not codemode_code_syntax_valid(post_data):
        print("codemodel_code_valid : code syntax invalid")
        return False
    # check if name is in the globals dict after exec
    if not codemode_name_in_globals(post_data):
        print("codemodel_code_valid : name is not in globals after executing code")
        return False

    return True
def codemodel_name_valid(post_data):
    if len(post_data["name"])==0:
        print("codemodel_name_valid : name empty")
        return False
    return False

def codemodel_name_in_globals(post_data):
    g=CodeManager.get_globals(code=post_data["code"])
    if not post_data["name"] in g:
        return False
    return True
