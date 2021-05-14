"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:brief: utility functions common to the whole project
"""

def debug_print(s):
    print("DEBUG : {}".format(s))

from apps.problems.models import ProblemModel
from apps.codes.models import CodeModel, DataFileModel
from apps.solvers.models import SolverModel

def get_checked_ids(post_data, prefix):
    return [int(k.replace(prefix,"")) for k in post_data if k.startswith(prefix)]
def get_checked_problems(post_data):
    return get_checked_ids(post_data,"problem_id_")
def get_checked_codes(post_data):
    return get_checked_ids(post_data,"code_id_")
def get_checked_datafiles(post_data):
    return get_checked_ids(post_data,"datafile_id_")
def get_checked_solvers(post_data):
    return get_checked_ids(post_data, "solver_id_")
def get_checked_postprocesses(post_data):
    return get_checked_ids(post_data, "postprocess_id_")

def delete_postprocesses(ids, user):
    pp=[CodeModel.objects.get(id=i) for i in ids]
    for p in pp:
        if user==p.author or user.is_superuser:
            p.delete()
        else:
            debug_print("User {} does not have the right to delete CodeModel ({})".format(user, p.id))
def delete_problems(ids, user):
    problems=[ProblemModel.objects.get(id=i) for i in ids]
    for problem in problems:
        # if user is superuser then delete
        # if user is author then delete
        # otherwise print error message and return
        if user==problem.author or user.is_superuser:
            problem.delete()
        else:
            debug_print("in delete_problems : user does not have the right to delete ProblemModel({})".format(problem.id))
def delete_codes(ids, user):
    codes=[CodeModel.objects.get(id=i) for i in ids]
    for code in codes:
        if code.author==user or user.is_superuser:
            code.delete()
        else:
            debug_print("User {} does not have the right to delete CodeModel ({})".format(user,code.id))

def delete_datafiles(ids, user):
    files=[DataFileModel.objects.get(id=i) for i in ids]
    for f in files:
        if f.author==user or user.is_superuser:
            f.delete()
        else:
            debug_print("User {} does not have the right to delete DataFileModel ({})".format(user, f.id))

def delete_solvers(ids, user):
    solvers=[SolverModel.objects.get(id=i) for i in ids]
    for solver in solvers:
        if user==solver.author or user.is_superuser:
            solver.delete()
        else:
            debug_print("User {} does not have the right to delete SolverModel ({})".format(user, solver.id))
