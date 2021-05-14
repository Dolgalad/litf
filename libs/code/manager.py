"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:briel: module for managing code testing
"""
import os
import re

from libs.utils import debug_print

# code status
from .status import CodeStatus
# virtual environements
from libs.venv.utils import VirtualEnv

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
    def check_code_status(code):
        class_name=code["name"]
        # create a virtual instrument
        venv_dir=os.path.join(VENV_CREATION_PATH,code["name"])
        venv=VirtualEnv(venv_dir=venv_dir)
        # get class parameters
        class_params=get_params(class_name, code["code"])
        # get requirements
        print("REQUIREMENTS : ")
        print(code["requirements"])
        rs=venv.install_requirements(code["requirements"])
        print("venv.install_requirements : {}".format(rs))
        # save code in virtual environement
        sc=venv.save_code(code["code"])
        print("venv.save_code : {}".format(sc))
        # run the testing script
        ts=venv.exec_file(os.path.join(venv_dir,"test_script.py"), "{} code".format(code["name"]))
        print("venv.exec_file : {}".format(ts))

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
