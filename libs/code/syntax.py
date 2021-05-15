"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:breif: functions for manipulating python function and class definitions
"""

class f_arg:
    def __init__(self,key):
        self.key=key
    def __str__(self):
        return "f_arg (key:{})".format(self.key)
class f_kwarg(f_arg):
    def __init__(self,key,default):
        super().__init__(key)
        self.default=default
    def __str__(self):
        return "f_kwarg (key:{},default:{})".format(self.key,self.default)
def parse_arg(a):
    if "=" in a:
        b=a.split("=")
        return f_kwarg(key=b[0], default=b[1])
    return f_arg(a)


def get_code_indentexpr(code):
    return 4

def get_function_arguments(func_name, code):
    f_def="def {}(".format(func_name)
    arglist=[]
    for l in code.split("\n"):
        if f_def in l:
            # parse the current line
            a=l[l.find(f_def)+len(f_def):]
            args=[]
            while len(a):
                pos=a.find(",")
                if pos==-1:
                    b=a[:a.find(")")]
                    if len(b):
                        args.append(parse_arg(b))
                    break
                else:
                    b=a[:pos]
                    a=a[pos+1:]
                    args.append(parse_arg(b))
            arglist.append(args)
    return arglist

if __name__=="__main__":
    print("Testing function_argument parsing")
    code="""
def a():
    return 1
def a(x):
    return 2
def a(x,y,z):
    return 3
def a(x=1,y=1,z=1):
    return 4
def a(x,y=1,z=1):
    return 5
"""
    print(get_function_arguments("a",code))
