import os
import sys
import subprocess
import pickle as pkl
import json
from contextlib import redirect_stdout
import io
import datetime

# input data filename
INPUT_FILENAME="input.pkl"
CONSTRUCTOR_INPUT_FILENAME="c_input.pkl"
# test output filename
TEST_OUTPUT_FILENAME="test_output.json"

# errors
SUCCESS="success"
MISSING_CODE_FILE="missing_code_file"
NAME_NOT_IN_CONTEXT="name_not_in_context"
DECLARATION_ERROR="declaration_error"
INSTANTIATION_ERROR="instantiation_error"
EXECUTION_ERROR="execution_error"
OUTPUT_NOT_PKL_SERIALIZABLE="output_not_pkl_serializable"
INPUT_LOAD_ERROR="input_load_error"
CONSTRUCTOR_INPUT_LOAD_ERROR="constructor_input_load_error"
CLASS_INSTANTIATION_ERROR="class_instantiation_error"
UNKWN_CODE_TYPE="unkwnown_code_type"

# code types
CLASS_TYPE=0
FUNC_TYPE=1
UNKWN_TYPE=2

def exit_code(err):
    if err==SUCCESS:
        return 0
    elif err==MISSING_CODE_FILE:
        return 1
    elif err==NAME_NOT_IN_CONTEXT:
        return 2
    elif err==DECLARATION_ERROR:
        return 3
    elif err==INSTANTIATION_ERROR:
        return 4
    elif err==EXECUTION_ERROR:
        return 5
    elif err==OUTPUT_NOT_PKL_SERIALIZABLE:
        return 6
    elif err==INPUT_LOAD_ERROR:
        return 7
    elif err==CONSTRUCTOR_INPUT_LOAD_ERROR:
        return 8
    elif err==CLASS_INSTANTIATION_ERROR:
        return 9
    elif err==UNKWN_CODE_TYPE:
        return 10
    else:
        return -1

def err_output(e_code,e,g,l,s,code_type=None):
    gk=[k for k in g]
    lk=[k for k in l]
    if e is None:
        return {"error_code":exit_code(e_code),\
                "globals":gk,\
                "type":code_type,\
                "locals":lk,\
                "stdout":s}
    return {"error_code":exit_code(e_code),\
            "error":str(e),\
            "error_type":str(type(e)),\
            "globals":gk,\
            "type":code_type,\
            "locals":lk,\
            "stdout":s}
def get_code_type(name,g,l):
    f=""
    if name in g:
        f=str(g[name])
    if name in l:
        f=str(l[name])
    if f.startswith("<class"):
        return CLASS_TYPE
    if f.startswith("<function"):
        return FUNC_TYPE
    return UNKWN_TYPE
def save_output(output):
    pkl.dump(output,open(TEST_OUTPUT_FILENAME,"wb"))
    return 
    json.dump(output,open(TEST_OUTPUT_FILENAME,"w"))
    return
    with open(TEST_OUTPUT_FILENAME,"w") as f:
        f.write(json.dumps(output))
        f.close()

def declaration_test(code, g, l, stdout_buffer):
    try:
        exec(code, g)
        #exec(code)
    except Exception as e:
        save_output(err_output(DECLARATION_ERROR, e, g, l, stdout_buffer.getvalue()))
        exit(exit_code(DECLARATION_ERROR))
def context_test(name, g, l , stdout_buffer):
    if (not name in g) and (not name in l):
        save_output(err_output(NAME_NOT_IN_CONTEXT,None,g,l,stdout_buffer.getvalue()))
        exit(exit_code(NAME_NOT_IN_CONTEXT))
    return get_code_type(name, g, l)
def load_input_args(g,l,stdout_buffer,ct):
    in_args,in_kwargs=(),{}
    if os.path.exists(INPUT_FILENAME):
        try:
            in_args=pkl.load(open(INPUT_FILENAME,"rb"))
            if isinstance(in_args, tuple):
                in_args,in_kwargs=in_args
                return in_args, in_kwargs
            return (in_args,),{}
        except Exception as e:
            save_output(err_output(INPUT_LOAD_ERROR,e,g,l,stdout_buffer.getvalue(),ct))
            exit(exit_code(INPUT_LOAD_ERROR))
    return in_args,in_kwargs
def load_constr_args(g,l,stdout_buffer,ct):
    in_args,in_kwargs=(),{}
    if os.path.exists(CONSTRUCTOR_INPUT_FILENAME):
        try:
            in_args,in_kwargs=pkl.load(open(CONSTRUCTOR_INPUT_FILENAME,"rb"))
        except Exception as e:
            save_output(err_output(CONSTRUCTOR_INPUT_LOAD_ERROR,e,g,l,stdout_buffer.getvalue(),ct))
            exit(exit_code(CONSTRUCTOR_INPUT_LOAD_ERROR))
    return in_args,in_kwargs

def function_instantiation_test(name,g,l,stdout_buffer,ct):
    # instantiation test
    try:
        f=eval(name, g)
        #f=eval(name)
    except Exception as e:
        test_output=err_output(INSTANTIATION_ERROR,e,g,l,stdout_buffer.getvalue(),ct)
        save_output(test_output)
        exit(exit_code(INSTANTIATION_ERROR))
    return f

def context_add_vars(vars_dict, context):
    a=[]
    for k in vars_dict:
        t=k
        while t in context:
            t=t+"a"
        a.append(t)
        context[t]=vars_dict[k]
    return tuple(a)
 
def class_instantiation_test(constr_f, c_args, c_kwargs, g, l, stdout_buffer,ct):
    # instantiation test
    instance=None
    try:
        new_keys=context_add_vars({"constr_f":constr_f,"c_args":c_args,"c_kwargs":c_kwargs},g)
        instance=eval("{}(*{},**{})".format(*new_keys),g)
    except Exception as e:
        test_output=err_output(CLASS_INSTANTIATION_ERROR,e,g,l,stdout_buffer.getvalue(),ct)
        save_output(test_output)
        exit(exit_code(CLASS_INSTANTIATION_ERROR))
    return instance

   
def execution_test(f,args,kwargs,g,l,stdout_buffer,ct):
    y=None
    ti,tf=None,None
    try:
        # add the arguments to the context
        new_keys=context_add_vars({"f":f,"args":args,"kwargs":kwargs},g)
        ti=datetime.datetime.now()
        y=eval("{}(*{},**{})".format(*new_keys),g)
        tf=datetime.datetime.now()
    except Exception as e:
        save_output(err_output(EXECUTION_ERROR,e,g,l,stdout_buffer.getvalue(),ct))
        exit(exit_code(EXECUTION_ERROR))
    return y,ti,tf

def load_code():
    c=None
    with open("code.py","r") as f:
        c=f.read()
        f.close()
    return c
if __name__=="__main__":
    # two command line arguments
    name=sys.argv[1]
    req_type=sys.argv[2]

    # code.py must exist
    if not os.path.exists("code.py"):
        exit(exit_code(MISSING_CODE_FILE))
    code=load_code()

    # create an empty context
    context_g, context_l={},{}

    # store globals and locals keys
    glo,loc=[k for k in globals()], [k for k in locals()]

    # output
    output=None
    # begining and final dates
    ti,tf=None,None

    # code type : func, class, unknown
    code_type=UNKWN_TYPE

    if code_type=="solver":
        # load input
        #x=pkl.load(open("x.pkl","rb"))
        x=[i for i in range(1000)]
        # run the class declaration code code.py
        exec(open("code.py").read(), glo, loc)
        constr=eval(name, glo, loc)
        solver=constr()
        y=solver(x)
        print("Simulation run done")

    if req_type=="code":
        with io.StringIO() as buf, redirect_stdout(buf):
            glo,loc=[k for k in globals()], [k for k in locals()]
            # declaration code execution
            declaration_test(code, context_g, context_l, buf)

            # search for <name> in the globals dictionary
            # if <name> isn't contained in globals then exit with
            # NAME_NOT_IN_CONTEXT error
            code_type=context_test(name, context_g, context_l, buf)
            if code_type==FUNC_TYPE:
                # load input args
                args,kwargs=load_input_args(context_g,context_l,buf,code_type)
                # function instantiation test
                f=function_instantiation_test(name,context_g,context_l,buf,code_type)
                # execution test
                output,ti,tf=execution_test(f,args,kwargs,context_g,context_l,buf,code_type)
            elif code_type==CLASS_TYPE:
                # load constructor args
                c_args,c_kwargs=load_constr_args(context_g,context_l,buf,code_type)
                # load input args
                i_args,i_kwargs=load_input_args(context_g,context_l,buf,code_type)
                #print("Input args : {}, {}".format(i_args,i_kwargs))
                # constructor instantiation test
                constructor_f=function_instantiation_test(name,context_g,context_l, buf,code_type)
                # class instantiation test
                instance=class_instantiation_test(constructor_f, c_args,c_kwargs, context_g,context_l, buf,code_type)
                # we could add a execution test but we would need to know which method to test
                # when testing a solver we would need the instance to be callable or have a solve
                # method.
                if hasattr(instance,"__call__"):
                    output,ti,tf=execution_test(instance.__call__, i_args, i_kwargs, context_g,context_l, buf,code_type)
                
            else:
                print("Unknown type code")
                save_output(err_output(UNKWN_CODE_TYPE,context_g,context_l))
                exit(exit_code(UNKWN_CODE_TYPE))

            # execution was a success, save and exit
            test_output={"error_code":exit_code(SUCCESS),\
                         "globals":[k for k in context_g],\
                         "locals":[k for k in context_l],\
                         "stdout":buf.getvalue(),\
                         "type":code_type}
            if not output is None:
                test_output["output"]=output
                test_output["output_type"]=str(type(output))
            if (not ti is None) and (not tf is None):
                test_output["start_dt"]=ti
                test_output["stop_dt"]=tf
            save_output(test_output)
    # exit with success code
    exit(exit_code(SUCCESS))

