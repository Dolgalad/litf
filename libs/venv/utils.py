"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:brief: utilities for managing virual environements
"""
import time
import io
import signal
import sys
import os
import json
import subprocess
import venv
import psutil


def kill_hard(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()
def get_pids(proc_pid):
    a=[]
    try:
        process=psutil.Process(proc_pid)
    except:
        return []
    for proc in process.children(recursive=True):
        a.append(proc.pid)
    a.append(process.pid)
    return a
def kill_all(pids):
    print("kill_all : {}".format(pids))
    for pid in pids:
        try:
            psutil.Process(pid).kill()
        except Exception as e:
            print("in kill_all : {}".format(e))

# location of the test_script.py script
TEST_SCRIPT_PATH="test_script.py"
EXECUTION_TIMEOUT=600
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
    def __init__(self, venv_dir, resources=None):
        self.path=venv_dir
        self.create_env()
        self.copy_test_script()
        if not resources is None:
            # save code
            self.save_code(resources[0])
            # move the files
            self.move_files(resources[2])
            # install requirements
            self.install_requirements(resources[1])
    def copy_test_script(self):
        os.system("cp {} {}".format(TEST_SCRIPT_PATH, os.path.join(self.path, "test_script.py")))
    def run_test_script(self, params=""):
        #sys.stdout.write("running test script...")
        #sys.stdout.flush()
        r = self.exec_file(os.path.join(self.path,"test_script.py"),params)
        #print("done")
        return r
    def create_env(self):
        return venv.EnvBuilder(clear=True, with_pip=True).create(env_dir=self.path)
    def delete_env(self):
        #sys.stdout.write("deleting virtualenv...")
        #sys.stdout.flush()
        i= self.check_output("rm -r {}".format(self.path))
        #print("done")
        return i
    def install_requirements(self, requirements):
        #sys.stdout.write("installing requirements...")
        #sys.stdout.flush()
        self.save_requirements(requirements)
        #sys.stdout.write("done\n")
        #sys.stdout.flush()
        return self.check_output("cd {}; pip install -r requirements.txt".format(self.path))
    def save_requirements(self, requirements):
        r_path=os.path.join(self.path, "requirements.txt")
        with open(r_path,"w") as f:
            if isinstance(requirements,list):
                f.write("\n".join(requirements))
            else:
                f.write(requirements)
            f.close()
    def check_output(self,call):
        print("Checkoutput for : {}".format(call))
        c="{} ; {} ; {}".format(self.activate_cmd(),call,"deactivate")
        pids=[]
        try:
            #proc=subprocess.Popen("/bin/bash", stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            #activate_out=proc.communicate(input=c.encode(),timeout=EXECUTION_TIMEOUT)
            #print("wait")
            #proc.wait()
            proc=subprocess.Popen(c,shell=True,preexec_fn=os.setsid)
            time.sleep(.1)
            pids=get_pids(proc.pid)
            (stdout,stderr)=proc.communicate(timeout=EXECUTION_TIMEOUT)
            #a=subprocess.check_output(c,shell=True).decode("utf-8")
            if stdout is None:
                ans=VEnvOutput(stdout="")
            else:
                ans=VEnvOutput(stdout=stdout)
        except subprocess.CalledProcessError as e:
            ans= VEnvOutput(stderr=e)
        except subprocess.TimeoutExpired as e:
            ans=VEnvOutput(stderr="Timeout error\n{}".format(e))
            # KILL
            proc.kill()
            for p in pids:
                try:
                    kill_hard(p)
                except:
                    print("hard kill arror")

        except Exception as e:
            ans=VEnvOutput(stderr=e)
        return ans

    def activate_cmd(self):
        return ". "+os.path.join(self.path,"bin/activate")
    def exec_file(self, filename, args):
        file_dir=os.path.dirname(filename)
        name=filename.split("/")[-1]
        return self.check_output("cd {} ; python {} {}".format(file_dir, name, args))
    def save_code(self,code):
        #sys.stdout.write("saving code...")
        #sys.stdout.flush()
        c_path=os.path.join(self.path,"code.py")
        with open(c_path, "w") as f:
            f.write(code)
            f.close()
        #print("done")
    def save_info_file(self, data):
        #sys.stdout.write("saving info...")
        #sys.stdout.flush()
        if len(data):
            json.dump(data, open(os.path.join(self.path,"info_file.json"),"w"))
        #print("done")
    def move_files(self, files):
        #sys.stdout.write("moving files...")
        #sys.stdout.flush()
        for f in files:
            # get the basename
            base_name=os.path.basename(f)
            target_name=os.path.join(self.path,base_name)
            os.system("cp {} {}".format(f,target_name))
        #print("done")
    def move_input_data(self, files):
        #sys.stdout.write("moving input data...")
        #sys.stdout.flush()
        for f in files:
            base_name=os.path.basename(f)
            target_name=os.path.join(self.path,"input.pkl")
            os.system("cp {} {}".format(f, target_name))
        #print("done")
