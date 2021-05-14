import os
import sys
import subprocess
import pickle as pkl

def log_error(e):
    with open("error_log","a") as f:
        f.write("{}\n".format(e))
        f.close()
if __name__=="__main__":

    class_name=sys.argv[1]
    class_type=sys.argv[2]

    # code.py must exist
    if not os.path.exists("code.py"):
        print("unable to find code.py")
        exit(2)
    # store globals and locals
    glo,loc={},{}

    if class_type=="solver":
        # load input
        #x=pkl.load(open("x.pkl","rb"))
        x=[i for i in range(1000)]
        # run the class declaration code code.py
        exec(open("code.py").read(), glo, loc)
        constr=eval(class_name, glo, loc)
        solver=constr()
        y=solver(x)
        print("Simulation run done")
    if class_type=="code":
        try:
            exec(open("code.py").read(), glo, loc)
        except Exception as e:
            log_error(e)
            exit(1)
        
        try:
            constr=eval(class_name, glo, loc)
        except Exception as e:
            log_error(e)
            exit(2)

        try:
            constr()
        except:
            log_error(e)
            exit(3)
    exit(0)

