"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:briel: module for managing code testing
"""
import os
import re
import json
import pickle as pkl

from libs.utils import debug_print

# code status
from .status import CodeStatus
# virtual environements
from libs.venv.utils import VirtualEnv
# function parameter parser
from libs.code.syntax import *
# import CodeModel
from apps.codes.models import CodeModel,ExecutionResultModel, CodeArgumentModel
# import SolverModel
from apps.solvers.models import SolverModel, PostprocessingResultModel, SolverExecutionResultModel

# code model resources
from .codemodel_resources import CodeModelResources

# code execution status
from libs.code import status

# Some settings
VENV_CREATION_PATH="virtual_environements"
OUTPUT_FILENAME="test_output.json"

class CodeManager:
    @staticmethod
    def merge_codemodel_resources(a,b):
        x_code=a[0]
        x_req=a[1]
        x_f=a[2]
        # append files
        for f in b[2]:
            if not f in x_f:
                x_f.append(f)
        # append resources
        for r in b[1]:
            if not r in x_req:
                x_req.append(r)
        # append b's code to a's
        x_code="\n".join([x_code,b[0]])
        return (x_code,x_req,x_f)

    @staticmethod
    def get_codemodel_resources(cm=None):
        if cm is None:
            return ("",[],[])
        if isinstance(cm,list):
            a=CodeManager.get_codemodel_resources()
            for i in cm:
                a=CodeManager.merge_codemodel_resources(a,CodeManager.get_codemodel_resources(i))
            return a
        return (cm.get_code(), cm.get_requirements(), cm.get_filenames())

    @staticmethod
    def run_test_and_get_output(venv, params=""):
        ts=venv.run_test_script(params)
        print("run_test_and_get_output : {}".format(ts))
        # check if output file exists
        if not os.path.exists(os.path.join(venv.path,"test_output.json")):
            errs="output file not found"
            if ts.has_errors():
                errs+=str(ts.stderr)
            
            return {"error_code":-2, "error":errs,"stdout":"", "output":None, "output_type":None, "start_dt":None, "stop_dt": None}
        return CodeManager.load_output(venv.path)
    @staticmethod
    def get_solver_venv_dir(problem_id, solver_id):
        dirname="{}_{}_venv".format(problem_id, solver_id)
        return os.path.join(VENV_CREATION_PATH, dirname)
    @staticmethod
    def get_problem_solver_resources(solver):
        # check for input and output types
        #input_type_res=CodeManager.get_codemodel_resources(solver.problem.input_type)
        input_type_res = CodeModelResources.from_codemodel(solver.problem.input_type)

        #output_type_res=CodeManager.get_codemodel_resources(solver.problem.output_type)
        output_type_res=CodeModelResources.from_codemodel(solver.problem.output_type)

        # check for postprocessing types
        #process_res=CodeManager.get_codemodel_resources([p for p in solver.problem.postprocess.all()])
        process_res=CodeModelResources.from_codemodel([p for p in solver.problem.postprocess.all()])

        # get solver implementation resources
        #solver_res=CodeManager.get_codemodel_resources(solver.implementation)
        solver_res=CodeModelResources.from_codemodel(solver.implementation)
        # merge the resources
        resources=CodeModelResources()
        resources.merge_with(input_type_res)
        resources.merge_with(output_type_res)
        resources.merge_with(process_res)
        resources.merge_with(solver_res)
        return resources

    @staticmethod
    def get_problem_solver_input_data(solver):
        input_data=[f.datafile.path for f in solver.problem.input_data.all() if f.flags=="input"]
        print("input data : {}".format(input_data))
        # if no input data available
        if input_data==[]:
            # create a temporary file
            pkl.dump([float(k) for k in range(10)],open("testtesttest.pkl","wb"))
            input_data.append("testtesttest.pkl")

        return input_data
    @staticmethod
    def solver_run(solver_id, result=None):
        msg="Solver_run : solver_id={}".format(solver_id)
        if not result is None:
            msg+=", result={}".format(result.id)
        print(msg)

        solver=SolverModel.objects.get(id=solver_id)

        # delete all postprocessing results for this solvers results
        ppr=PostprocessingResultModel.objects.filter(problem=solver.problem, solver=solver).all().delete()

        # check if the solver is already awaiting results
        # create a pending result, set its state to RUNNING
        # get the resources and info for the problem
        info_data=solver.problem.info()
        resources=CodeManager.get_problem_solver_resources(solver)


        if result is None:
            # check if an incomplete SolverExecutionResultModel exists for this solver
            if solver.has_pending_execution_result():
                print("Solver has a pending execution result")
                return
            # create a pending SolverExecutionResultModel
            solver.create_pending_execution_result()

        
        # initialize info_data
        info_data=solver.problem.info()
        # get input data resources
        input_data=CodeManager.get_problem_solver_input_data(solver)

        # merge the resources
        resources=CodeManager.get_problem_solver_resources(solver)

        # setup virtual environement
        venv_dir=CodeManager.get_solver_venv_dir(problem_id=solver.problem.id, solver_id=solver.id)
        venv=VirtualEnv(venv_dir, resources=resources)

        # add input data
        venv.move_input_data(input_data)
        # add info file
        venv.save_info_file(info_data)

        # execute the test script and get output
        output=CodeManager.run_test_and_get_output(venv, "{} code".format(solver.implementation.name))
        print("\texit_code={}".format(output["error_code"]))
        if not "output" in output:
            output["output"]=None
        # if the output is a string and a file exists with the same name in the virtual environement

        # save the output
        erm=CodeManager.save_output_solver_erm(solver, solver.implementation, output, flags="solution", result=result)
        erm.save()

        # postprocessing
        if "postprocessing" in output:
            print("\tpostprocessing : {}".format(output["postprocessing"]))
            for [process_name, process_out] in output["postprocessing"]:
                process_obj=None
                for ppp in solver.problem.postprocess.all():
                    if ppp.name == process_name:
                        process_obj=ppp
                if process_obj is None:
                    continue
                if isinstance(process_out, str):
                    pp=os.path.join(venv.path, process_out)
                    os.system("ls {}".format(venv.path))
                    if os.path.exists(pp):
                        # save the output file somewhere
                        from django.core.files import File
                        f=File(open(pp,"rb"))
                        #f.save("new_name")
                        postpr=PostprocessingResultModel.objects.create(problem=solver.problem, \
                                                                 implementation=process_obj,\
                                                                 output_file=f,\
                                                                 solver=solver,\
                                                                 execution_result=erm.result)
                        postpr.save()
                else:
                    postpr=PostprocessingResultModel.objects.create(problem=solver.problem,\
                                                                 implementation=process_obj,\
                                                                 solver=solver,\
                                                                 output_data=process_out,\
                                                                 execution_result=erm.result)
                    postpr.save()



        # remove venv
        venv.delete_env()
        return output["error_code"]


    @staticmethod
    def load_output(venv_dir):
        p=os.path.join(venv_dir,"test_output.json")
        odata=os.path.join(venv_dir, "output_data.dat")
        output_data=None
        if os.path.exists(odata):
            # get the contents as binary
            output_data=open(odata,"rb").read()
        if not os.path.exists(p):
            return {"error_code":-2,"error":"Test output file not found"}
        d=pkl.load(open(p,"rb"))
        d["output_content"]=output_data
        required_fields=["output_type","output","error", "start_dt", "stop_dt", "stdout"]
        for rf in required_fields:
            if not rf in d:
                d[rf]=None
        return d
    @staticmethod
    def save_output_erm(cm, output, input_data=None, flags=None, erm=None):
        # save the model
        if erm is None:
            erm=cm.get_pending_execution_result()
        erm.input_data=input_data
        #erm.output_data=output["output_content"]
        erm.output_data=output["output"]
        erm.output_type=output["output_type"]
        erm.status=output["error_code"]
        erm.start_time=output["start_dt"]
        erm.stop_time=output["stop_dt"]
        erm.stdout=output["stdout"]
        erm.errors=output["error"]
        erm.flags=flags
        erm.save()

        return erm
    @staticmethod
    def save_output_solver_erm(solver, cm, output, input_data=None, flags=None, result=None):
        # save the model
        if result is None:
            erm=solver.get_pending_execution_result()
        else:
            erm=result
        if erm.result is None:
            res=ExecutionResultModel.objects.create(implementation=solver.implementation,\
                                                    input_data=input_data,\
                                                    output_data=output["output"],\
                                                    output_type=output["output_type"],\
                                                    status=output["error_code"],\
                                                    start_time=output["start_dt"],\
                                                    stop_time=output["stop_dt"],\
                                                    stdout=output["stdout"],\
                                                    errors=output["error"],\
                                                    flags=flags)
            res.save()
            erm.result=res
        else:
            erm.result.input_data=input_data
            erm.result.output_data=output["output"]
            erm.result.output_type=output["output_type"]
            erm.result.status=output["error_code"]
            erm.result.start_time=output["start_dt"]
            erm.result.stop_time=output["stop_dt"]
            erm.result.stdout=output["stdout"]
            erm.result.errors=output["error"]
            erm.result.flags=flags
            erm.result.save()
        erm.status=erm.result.status
        erm.save()

        return erm
    @staticmethod
    def check_code_dependants(code_id):
        cm=CodeModel.objects.get(id=code_id)
        # get list of all codes that need to be checked because they depend on the current code
        dependants=cm.get_dependants()
        for d in dependants:
            CodeManager.check_code_status(d.id)
    @staticmethod
    def get_codemodel_input_data(cm):
        print("get codemodel input data")
        # check the codemodels parameters
        if cm.arguments is None:
            print("\tcodemodel has no arguments 1")
            return []
        cm_params = json.loads(cm.arguments.data)
        if cm_params is None:
            print("\tcodemodel has no arguments 2")
            return []
        # get input data compatible with the number of positional arguments
        n=len(cm_params["args"])
        if n==0:
            print("\tcodemodel has no arguments 3")
            return []
        # store some floats in a pkl file
        in_dat=tuple(list(range(n)))
        pkl.dump((in_dat,{}), open("temp_input_data.pkl","wb"))
        print("\tinput_data : {}".format(in_dat))
        return ["temp_input_data.pkl"]

    @staticmethod
    def check_codemodel_arguments(cm):
        # get the CodeArgumentModel object for this codemodel object
        # get the Argument description for this CodeModel object
        from libs.code.syntax import get_f_args
        arg_description=get_f_args(cm.name, cm.code)
        if arg_description is None:
            cm.arguments=None
            cm.save()
            return
        arg_description_data=json.dumps(arg_description.data())
        # save the argument description
        if cm.arguments is None:
            ca=CodeArgumentModel.objects.create(data=arg_description_data)
            ca.save()
            cm.arguments=ca
            cm.save()
        else:
            old_arg_desc=cm.arguments.data
            if old_arg_desc!=arg_description_data:
                cm.arguments.data=arg_description_data
                cm.arguments.save()
                cm.save()
    @staticmethod
    def execute_pending_results(code_id):
        cm=CodeModel.objects.get(id=code_id)
        # get pending results
        pending_res=ExecutionResultModel.objects.filter(implementation=code_id)
        pending_res=pending_res.filter(status=status.CodeExecutionStatus.PENDING)
        for res in pending_res:
            CodeManager.codemodel_execute_result(cm, res)

    @staticmethod
    def codemodel_execute_result(cm, res):
        # get resources for the codemodel
        # get input data for result object
        resources=CodeManager.get_codemodel_resources(cm)
        # set the result status to RUNNING 
        res.status=status.ExecutionStatus.RUNNING
        res.save()

        # check the codemodel arguments
        CodeManager.check_codemodel_arguments(cm)

        # get codemodel's input data
        input_data=CodeManager.get_codemodel_input_data(cm)

        # create a virtual instrument
        venv_dir=os.path.join(VENV_CREATION_PATH,cm.name)
        venv=VirtualEnv(venv_dir=venv_dir, resources=resources)
        venv.move_input_data(input_data)
        # get class parameters
        #class_params=get_function_arguments(cm.name, cm.code)

        # run the testing script
        output=CodeManager.run_test_and_get_output(venv, "{} code".format(cm.name))
        print(output)


        # save the output
        erm=CodeManager.save_output_erm(cm, output, flags=res.flags, erm=res)


        # set the codemodels status
        cm.status=erm.status
        cm.save()
        #erm.save()

        # remove venv
        venv.delete_env()

    @staticmethod
    def check_code_status(code_id, check_type="code", input_data=[]):
        # get the CodeModel object
        cm=CodeModel.objects.get(id=code_id)

        # check the codemodel arguments
        CodeManager.check_codemodel_arguments(cm)
        
        # set all previous results to pending and remove all integrity checks
        exec_list=ExecutionResultModel.objects.filter(implementation=code_id).all()
        for e in exec_list:
            if e.flags is None:
                e.set_pending()
            elif "integrity"== e.flags:
                e.delete()
            else:
                e.set_pending()
        # create the pending ExecutionResultModel
        cm.create_pending_execution_result()


        # get resources
        resources=CodeManager.get_codemodel_resources(cm)
        # check if input data exists
        
        # get codemodel's input data
        input_data=CodeManager.get_codemodel_input_data(cm)

        # create a virtual instrument
        venv_dir=os.path.join(VENV_CREATION_PATH,cm.name)
        venv=VirtualEnv(venv_dir=venv_dir, resources=resources)
        venv.move_input_data(input_data)
        # get class parameters
        #class_params=get_function_arguments(cm.name, cm.code)

        # run the testing script
        output=CodeManager.run_test_and_get_output(venv, "{} code".format(cm.name))


        # save the output
        erm=CodeManager.save_output_erm(cm, output, flags="integrity")


        # set the codemodels status
        cm.status=erm.status
        cm.save()
        #erm.save()

        # remove venv
        venv.delete_env()
        return CodeStatus.UNCHECKED

    @staticmethod
    def check_solver_status(solver_id):
        # get list of SolverExecutionResultModels 
        res_l=SolverExecutionResultModel.objects.filter(solver=solver_id)
        if len(res_l)==0:
            CodeManager.solver_run(solver_id)
            return 0
        for res in res_l:
            CodeManager.solver_run(solver_id, result=res)
        return 0
    @staticmethod
    def get_globals(code=None):
        """Returns the keys of the globals dictionary after executing the code
        :return: keys of globals dictionary
        :rtype: list of str
        """
        debug_print("get_globals : code_len:{}".format(len(code)))
        if code:
            g={}
            exec(code, g)
            return list(g)
        return []
    @staticmethod
    def codemodel_set_execution_pending(cm_id):
        cm=CodeModel.objects.get(id=cm_id)
        execution_results=ExecutionResultModel.objects.filter(implementation=cm)
        for er in execution_results:
            er.set_pending()
