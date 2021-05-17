"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:brief: utilities for managing virual environements
"""
import os
import subprocess
import venv

# location of the test_script.py script
TEST_SCRIPT_PATH="test_script.py"
class VEnvOutput:
    def __init__(self, stdout=None, stderr=None):
        self.stdout=stdout
        self.stderr=stderr
    def no_errors(self):
        return self.stderr is None
    def has_errors(self):
        return not self.stderr is None
    def __str__(self):
        return "VEnvOutput (with_errs:{})\n{}".format(self.has_errors(),self.stdout)

class VirtualEnv:
    """Class for managing a python virtual environement
    """
    def __init__(self, venv_dir):
        self.path=venv_dir
        self.create_env()
        self.copy_test_script()
    def copy_test_script(self):
        os.system("cp {} {}".format(TEST_SCRIPT_PATH, os.path.join(self.path, "test_script.py")))
    def create_env(self):
        return venv.EnvBuilder(clear=True, with_pip=True).create(env_dir=self.path)
    def delete_env(self):
        return self.check_output("rm -r {}".format(self.path))
    def install_requirements(self, requirements):
        self.save_requirements(requirements)
        return self.check_output("cd {}; pip install -r requirements.txt".format(self.path))
    def save_requirements(self, requirements):
        r_path=os.path.join(self.path, "requirements.txt")
        print("save_requirements path : {}".format(r_path))
        with open(r_path,"w") as f:
            if isinstance(requirements,list):
                f.write("\n".join(requirements))
            else:
                f.write(requirements)
            f.close()
    def check_output(self,call):
        c="{} ; {} ; {}".format(self.activate_cmd(),call,"deactivate")
        try:
            a=subprocess.check_output(c,shell=True).decode("utf-8")
            return VEnvOutput(stdout=a)
        except subprocess.CalledProcessError as e:
            return VEnvOutput(stderr=e)
    def activate_cmd(self):
        return ". "+os.path.join(self.path,"bin/activate")
    def exec_file(self, filename, args):
        file_dir=os.path.dirname(filename)
        name=filename.split("/")[-1]
        return self.check_output("cd {} ; python {} {}".format(file_dir, name, args))
    def save_code(self,code):
        c_path=os.path.join(self.path,"code.py")
        with open(c_path, "w") as f:
            f.write(code)
            f.close()
    def move_files(self, files):
        for f in files:
            # get the basename
            base_name=os.path.basename(f)
            target_name=os.path.join(self.path,base_name)
            os.system("cp {} {}".format(f,target_name))
