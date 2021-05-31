from celery import shared_task

from .models import ProblemModel
from apps.solvers.models import SolverModel, SolverExecutionResultModel, PostprocessingResultModel

from libs.code.manager import CodeManager
@shared_task
def problem_submitted_task(problem):
    print("problem_submitted_task : {}".format(problem))

@shared_task
def problem_updated_task(problem):
    print("problem_updated_task : {}".format(problem))
    print("problem input_type changed ? ")
    print("problem output_type changed ? ")
    print("problem postprocessing changed ? ")
    # run the solvers again
    # get list of solvers
    print("porblem : {}".format(problem))
    solvers=SolverModel.objects.filter(problem=problem)
    for solver in solvers:
        CodeManager.check_solver_status(solver.id)

def problem_results(problem_id):
    solvers=SolverModel.objects.filter(problem=problem_id)
    for solver in solvers:
        # get solver execution results
        for sol in SolverExecutionResultModel.objects.filter(solver=solver):
            yield sol
@shared_task
def postprocess_updated_task(postprocess_id):
    print("postprocess update task : {}".format(postprocess_id))
    CodeManager.codemodel_set_execution_pending(postprocess_id)
    # check the status of the codemodel object
    CodeManager.check_code_status(postprocess_id)
    # check dependants
    CodeManager.check_code_dependants(postprocess_id)

    # run the postprocess for all results that need it
    # get list of problems that use this postprocessing step
    for problem in ProblemModel.objects.all():
        for postprocess in problem.postprocess.all():
            if postprocess.id==postprocess_id:
                print("problemm : {}, process : {}".format(problem, postprocess))
                # rerun all solver for this problem
                print("RERUN solvers")
                for solver in SolverModel.objects.filter(problem=problem).all():
                    CodeManager.check_solver_status(solver.id)
                continue

                for result in problem_results(problem.id):
                    # if postprocessing result exists for this execution result
                    pp_res=PostprocessingResultModel.objects.filter(problem=problem, execution_result=result.result)
                    if len(pp_res):
                        # delete the postprocessing results
                        print("Comuting new postprocessing result for res : {}".format(pp_res))
                        print(pp_res[0].output_data)
                    else:
                        print("Creating missing postprocessing result for res : {}".format(result))
    
