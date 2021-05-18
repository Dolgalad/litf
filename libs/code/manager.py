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
from apps.codes.models import CodeModel,ExecutionResultModel
# import SolverModel
from apps.solvers.models import SolverModel
# Some settings
VENV_CREATION_PATH="virtual_environements"
OUTPUT_FILENAME="test_output.json"
# regex 
FUNC_DEF_RX="^[ ]*def[ ]+{}[ ]*\([ ]*\)[ ]*:[ ]*$"
CLASS_DEF_RX="^[ ]*class[ ]+{}[ ]*:$"
CLASS_INIT_RX="^[ ]*def[ ]+__init__[ ]*\([ ]*self[ ]*,[ ]*x\)[ ]*:$"
def get_params(c_name, c_code):
    class_def_re=CLASS_DEF_RX.format(c_name)
    func_def_re=FUNC_DEF_RX.format(c_name)
    print("CLASS DEFINITION REGEX : {}".format(class_def_re))
    print("FUNC  DEFINITION REGEX : {}".format(func_def_re))
    for line in c_code.split("\n"):
        print("line re.match :\n\t{}\n\t{}".format(line,re.match(class_def_re, line)))
        print("func match", "\n\t{}".format(line,re.match(func_def_re, line)))
    return {}
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
        # check if output file exists
        if not os.path.exists(os.path.join(venv.path,"test_output.json")):
            return {"error_code":-2, "error":"output file not found"}
        return CodeManager.load_output(venv.path)
    @staticmethod
    def get_solver_venv_dir(problem_id, solver_id):
        dirname="{}_{}_venv".format(problem_id, solver_id)
        return os.path.join(VENV_CREATION_PATH, dirname)
    @staticmethod
    def solver_run(solver_id):
        solver=SolverModel.objects.get(id=solver_id)
        # if solver status is not SUCCESS (0) then return 
        print("Solver status : {}".format(solver.implementation.status))
        #if not solver.implementation.status==0:
        #    return
        
        # initialize info_data
        info_data={}
        # get input data resources
        input_data=[]
        for in_data in solver.problem.input_data.all():
            input_data.append(in_data.datafile.path)
        
        # check for input and output types
        input_type_res=CodeManager.get_codemodel_resources(solver.problem.input_type)
        if solver.problem.input_type:
            info_data["input_type"]=solver.problem.input_type.name

        output_type_res=CodeManager.get_codemodel_resources(solver.problem.output_type)
        if solver.problem.output_type:
            info_data["output_type"]=solver.problem.output_type.name
        # check for postprocessing types
        process_res=CodeManager.get_codemodel_resources([p for p in solver.problem.postprocess.all()])
        # add the preprocess steps to the info file
        info_data["postprocess"]=[p.name for p in solver.problem.postprocess.all()]
        # get solver implementation resources
        solver_res=CodeManager.get_codemodel_resources(solver.implementation)
        # merge the resources
        resources=CodeManager.merge_codemodel_resources(input_type_res,output_type_res)
        resources=CodeManager.merge_codemodel_resources(resources, process_res)
        resources=CodeManager.merge_codemodel_resources(resources, solver_res)

        # setup virtual environement
        venv_dir=CodeManager.get_solver_venv_dir(problem_id=solver.problem.id, solver_id=solver.id)
        venv=VirtualEnv(venv_dir, resources=resources)

        # add input data
        venv.move_input_data(input_data)
        # add info file
        venv.save_info_file(info_data)

        # execute the test script and get output
        print("before solver execution : ")
        os.system("ls {}".format(venv.path))
        output=CodeManager.run_test_and_get_output(venv, "{} code".format(solver.implementation.name))
        print("SOLVER RUN OUTPUT")
        print("OUTPUT STATUS : {}".format(output["error_code"]))
        print("OUTPUT STDOUT : \n{}".format(output["stdout"]))
        print("OUTPUT ERRORS : {}".format(output["error"]))

        # save the problem solution
        # save the output
        erm=CodeManager.save_output_erm(solver.implementation, output, flags="solution")



        # remove venv
        venv.delete_env()
        return output["error_code"]


    @staticmethod
    def load_output(venv_dir):
        p=os.path.join(venv_dir,"test_output.json")
        odata=os.path.join(venv_dir, "output_data.dat")
        output_data=None
        if os.path.exists(odata):
            print("output_data.dat exists !!!!!!!!!!!!!!!!!!!!!!")
            # get the contents as binary
            output_data=open(odata,"rb").read()
            print("TPAZEHG : {}".format(type(output_data)))
        if not os.path.exists(p):
            return {"error_code":-2,"error":"Test output file not found"}
        d=pkl.load(open(p,"rb"))
        d["output_content"]=output_data
        return d
    @staticmethod
    def save_output_erm(cm, output, input_data=None, flags=None):
        stdout,err=None,None
        ti,tf=None,None
        y=None
        if "output" in output:
            y=output["output"]
        if "error" in output:
            err=output["error"]
        if "start_dt" in output:
            ti=output["start_dt"]
        if "stop_dt" in output:
            tf=output["stop_dt"]
        if "stdout" in output:
            stdout=output["stdout"]
        # save the model
        erm=ExecutionResultModel.objects.create(implementation=cm,\
                                                input_data=input_data,\
                                                output_data=output["output_content"],\
                                                status=output["error_code"],\
                                                start_time=ti,\
                                                stop_time=tf,\
                                                stdout=stdout,\
                                                errors=err,\
                                                flags=flags)
        erm.save()
        #print("Saved erm : {}".format(erm.data()))
        return erm
                                 

    @staticmethod
    def check_code_status(code_id, check_type="code", input_data=[]):
        # get the CodeModel object
        cm=CodeModel.objects.get(id=code_id)

        # remove all previous code status execution results for this codemodel
        for e in ExecutionResultModel.objects.filter(implementation=code_id,\
                                                     flags="integrity"):
            e.delete()

        # get resources
        resources=CodeManager.get_codemodel_resources(cm)

        # create a virtual instrument
        venv_dir=os.path.join(VENV_CREATION_PATH,cm.name)
        venv=VirtualEnv(venv_dir=venv_dir, resources=resources)
        # get class parameters
        class_params=get_function_arguments(cm.name, cm.code)

        # run the testing script
        output=CodeManager.run_test_and_get_output(venv, "{} code".format(cm.name))

        print("CODE RUN")
        print(output)

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
        return CodeManager.solver_run(solver_id)

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
