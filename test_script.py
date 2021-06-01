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
OUTPUT_CONVERSION_ERROR="output_conversion_error"

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
    elif err==OUTPUT_CONVERSION_ERROR:
        return 11
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
            #print(open(INPUT_FILENAME,"r").read())
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

def output_conversion_test(output_type_name, out, g, l, b, c):
    #print("output_conversion_test : out_type_name:{}".format(output_type_name))
    #print("input type : {}".format(type(out)))
    #print("context_g contains {} : {}".format("output", "output" in g))
    try:
        g["output"]=out
        ti=datetime.datetime.now()
        oto=eval("{}(output)".format(output_type_name),g)
        tf=datetime.datetime.now()
        # if has dump method try to write to "output_data.dat"
        if not hasattr(oto,"dump"):
            # if object is pickleable then mabey keep it
            return output,ti,tf
        
        # dump to "output_data.dat"
        g["oto"]=oto
        exec("oto.dump(\"output_data.dat\")", g)
    except Exception as e:
        save_output(err_output(OUTPUT_CONVERSION_ERROR,e, g, l, b.getvalue(), c))
        exit(exit_code(OUTPUT_CONVERSION_ERROR))
    return output, ti, tf
    return "output_data.dat",ti,tf

def get_test_output(error_code=-1, stdout=None, c_type=2, _globals=None, _locals=None, error=None,\
        output=None, start_dt=None, stop_dt=None, conv_start_dt=None,conv_stop_dt=None):
    a,b=list(_globals.keys()),list(_locals.keys())
    return {"error_code":error_code, "stdout":stdout, "type":c_type, "globals":a,\
            "locals":b, "error":error,"output":output,"output_type":type(output),\
            "start_dt":start_dt, "stop_dt":stop_dt, "conversion_start_dt":conv_start_dt,\
            "conversion_stop_dt":conv_stop_dt}
def load_code():
    c=None
    with open("code.py","r") as f:
        c=f.read()
        f.close()
    return c
def load_info_file():
    if not os.path.exists("info_file.json"):
        return {}
    return json.load(open("info_file.json","r"))
if __name__=="__main__":
    # two command line arguments
    name=sys.argv[1]
    req_type=sys.argv[2]

    # code.py must exist
    if not os.path.exists("code.py"):
        exit(exit_code(MISSING_CODE_FILE))
    code=load_code()

    # check for existing info_file.json
    info_data=load_info_file()

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

    if req_type=="code":
        with io.StringIO() as buf, redirect_stdout(buf):
            glo,loc=[k for k in globals()], [k for k in locals()]
            # declaration code execution
            declaration_test(code, context_g, context_l, buf)

            # search for <name> in the globals dictionary
            # if <name> isn't contained in globals then exit with
            # NAME_NOT_IN_CONTEXT error
            code_type=context_test(name, context_g, context_l, buf)
            if code_type==UNKWN_TYPE:
                output_info={"error_code":exit_code(UNKWN_CODE_ERROR),"error":"litf does not abide {}'s (yet)".format(code_type),"stdout":buf.getvalue()}
            # load input args
            i_args,i_kwargs=load_input_args(context_g,context_l,buf,code_type)

            if code_type==FUNC_TYPE:
                # function instantiation test
                instance=function_instantiation_test(name,context_g,context_l,buf,code_type)
            elif code_type==CLASS_TYPE:
                # load constructor args
                c_args,c_kwargs=load_constr_args(context_g,context_l,buf,code_type)
                # constructor instantiation test
                constructor_f=function_instantiation_test(name,context_g,context_l, buf,code_type)
                # class instantiation test
                instance=class_instantiation_test(constructor_f, c_args,c_kwargs, context_g,context_l, buf,code_type)
            # if no input data return SUCCESS
            if not os.path.exists(INPUT_FILENAME):
                # try calling with no arguments
                output,ti,tf=execution_test(instance,(),{},context_g,context_l,buf,code_type)
                test_output=get_test_output(error_code=0, stdout=buf.getvalue(),c_type=code_type,\
                                       _globals=context_l, _locals=context_l,error=None,\
                                       start_dt=ti, stop_dt=tf,output=output)
                save_output(test_output)
                exit(exit_code(SUCCESS))

            # if there are input data but the object is not callable
            if not hasattr(instance, "__call__"):
                test_output=get_test_output(error_code=INSTANCE_NOT_CALLABLE_ERROR, error="code instance is not callable, perhaps you forgot to implement a __call__ method")
                save_output(test_output)
                exit(exit_code(INSTANCE_NOT_CALLABLE_ERROR))

            # execute instance ( input_args)
            output,ti,tf=execution_test(instance.__call__, i_args, i_kwargs, context_g, context_l,buf, code_type)
            if "output_type" in info_data:
                #print("converting to output type : {}".format(info_data["output_type"]))
                #print("Type before : {}".format(type(output)))
                output,ti_conv,tf_conv = output_conversion_test(info_data["output_type"], output, context_g, context_l, buf, code_type)
                #print("Type after : {}".format(type(output)))
                # if the output was dumped to an output file OUTPUT_DUMP then store its contents
            else:
                # output should be serializable
                output,ti_conv,tf_conv=output,None,None
            # if output data file exist save its data
            output_file_content=None
            if os.path.exists("output_data.dat"):
                output_file_content=open("output_data.dat","rb").read()
            
            # if there were no errors until this point we can move on to postprocessing
            postprocessing_info=[]
            if "postprocess" in info_data:
                #print(info_data["postprocess"])
                for process_name in info_data["postprocess"]:
                    try:
                        context_g["output"]=output
                        #print("postprocess input type : {}".format(type(output)))
                        ev=eval("{}(output)".format(process_name),context_g)
                        #print("postprocess output type : {}".format(type(ev)))
                        postprocessing_info.append([process_name, ev])
                    except Exception as e:
                        print("postprocessing error - {} : \n{}".format(process_name, e))

            test_output=get_test_output(error_code=0,\
                                        _globals=context_g,\
                                        _locals=context_l,\
                                        stdout=buf.getvalue(),\
                                        c_type=code_type,\
                                        error=None,
                                        start_dt=ti,\
                                        stop_dt=tf)
            if not output is None:
                # try to pickle output
                try:
                    if output_file_content is None:
                        test_output["output"]=pkl.dumps(output)
                        test_output["output_type"]=str(type(output))
                    else:
                        test_output["output"]=output_file_content
                        test_output["output_type"]=str(type(output))
                except Exception as e:
                    test_output["output"]=None
                    test_output["output_type"]=str(type(output))
                    test_output["error"]="output not serializable"
            if (not ti is None) and (not tf is None):
                test_output["start_dt"]=ti
                test_output["stop_dt"]=tf
            if (not ti_conv is None) and (not tf_conv is None):
                test_output["conversion_start_dt"]=ti_conv
                test_output["conversion_stop_dt"]=tf_conv
            if len(postprocessing_info):
                test_output["postprocessing"]=postprocessing_info
            save_output(test_output)

    # exit with success code
    exit(exit_code(SUCCESS))

