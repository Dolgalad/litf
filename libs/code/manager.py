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
# Some settings
VENV_CREATION_PATH="virtual_environements"

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
    def check_code_status(code_id):
        # get the CodeModel object
        cm=CodeModel.objects.get(id=code_id)
        class_name=cm.name
        requirements=cm.get_requirements()
        code=cm.get_code()

        cm_data=cm.data()
        
        # create a virtual instrument
        venv_dir=os.path.join(VENV_CREATION_PATH,class_name)
        venv=VirtualEnv(venv_dir=venv_dir)
        # get class parameters
        class_params=get_function_arguments(class_name, code)
        # prepare input data for testing the code

        if requirements:
            # get requirements
            rs=venv.install_requirements(requirements)
        # save code in virtual environement
        sc=venv.save_code(code)
        # run the testing script
        ts=venv.exec_file(os.path.join(venv_dir,"test_script.py"), "{} code".format(class_name))
        # read the test_output.json file before deleting the virtual environement
        output_filename=os.path.join(venv_dir, "test_output.json")
        if os.path.exists(output_filename):
            print("TEST OUTPUT")
            test_output=pkl.load(open(output_filename,"rb"))
            print(test_output)

            # get output
            output=None
            ti,tf=None,None
            stdout,err=None,None
            if "output" in test_output:
                output=test_output["output"]
            if "start_dt" in test_output:
                ti=test_output["start_dt"]
            if "stop_dt" in test_output:
                tf=test_output["stop_dt"]
            if "stdout" in test_output:
                stdout=test_output["stdout"]
            if "error" in test_output:
                err=test_output["error"]
            # remove all previous execution tests
            el=ExecutionResultModel.objects.filter(implementation=cm)
            for e in el:
                e.delete()
            # save the results in the database as an ExecutionResultModel object
            erm=ExecutionResultModel.objects.create(implementation=cm,\
                                                    output_data=output,\
                                                    status=test_output["error_code"],\
                                                    start_time=ti,\
                                                    stop_time=tf,\
                                                    stdout=stdout,\
                                                    errors=err)
            erm.save()
            # set the corresponding CodeModel status flag
            cm.status=test_output["error_code"]
            cm.save()
            print("Saved ExecutionResultModel")
        else:
            print("{} not found")

        # remove venv
        venv.delete_env()
        return CodeStatus.UNCHECKED
    @staticmethod
    def check_solver_status(code):
        return CodeStatus.UNCHECKED

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
