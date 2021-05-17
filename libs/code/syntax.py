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

class ArgumentInfo:
    def __init__(self, args_info=[], kwargs_info=[]):
        self.args_info=args_info
        self.kwargs_info=kwargs_info
    def __len__(self):
        return self.n_positional()+self.n_keyword()
    def n_positional(self):
        return len(self.args_info)
    def n_keyword(self):
        return len(self.kwargs_info)
    @staticmethod
    def from_function_definition_str(s):
        pass
    def __str__(self):
        a="ArgumentInfo : n_args={}, n_kwargs={}\n".format(self.n_positional(),self.n_keyword())
        if self.__len__()==0:
            return a
        for ar in self.args_info:
            a+="\t{}\n".format(ar)
        for ar in self.kwargs_info:
            a+="\t{}\n".format(ar)
        return a

        


def get_code_indentexpr(code):
    return 4

def get_function_arguments(func_name, code):
    f_def="def {}(".format(func_name)
    arglist=[]
    for l in code.split("\n"):
        if f_def in l:
            # parse the current line
            # line format : def <func_name>(<pg_1>,...,<pg_p>,<kwg_1>=<kw_v_1>,...,<kwg_1>=<kw_v_q>):
            # positional arguments <pg_1>,...,<pg_p> are supposed to be floats unless specified otherwise
            #                                        in the docstring
            # keyword arguments <kwg_1>,...,<kwg_q> types need to be evaluated 
            # execute : <kwg_1>,...<kwg_q>=<kw_v_1>,...,<kw_v_q>
            # for i in [1,...,q] do
            #     type(<kw_v_i>)
            a=l[l.find(f_def)+len(f_def):]
            print("line : -{}-".format(l))
            # keep the full line
            # find first opening parenthesis
            fp_pos=l.find("(")
            # find last ) character
            fl_pos=l.rfind(")")
            if len(l[fp_pos+1:fl_pos])==0:
                arglist.append(ArgumentInfo())
                continue
            # find first = character, if none are found then function has no keyword arguments
            eq_pos=l.find("=")
            if eq_pos==-1:
                a_l=l[fp_pos+1:l.rfind(")")]
                if "," in a_l:
                    ar=[]
                    for a in a_l.split(","):
                        ar.append(f_arg(a))
                    arglist.append(ArgumentInfo(args_info=ar))
                else:
                    arglist.append(ArgumentInfo([f_arg(a_l)]))
                continue
            else:
                # find last "," before <eq_pos>
                c_pos=0
                while l.find(",",c_pos+1)<eq_pos:
                    c_pos=l.find(",",c_pos)
                if c_pos==0:
                    # no positional arguments
                    b=l[fp_pos+1:fl_pos]
                    if "," in b:
                        arglist.append(ArgumentInfo(kwargs_info=[parse_arg(k) for k in b.split(",")]))
                    else:
                        arglist.append(ArgumentInfo([parse_arg(b)]))
                    continue
                else:
                    # get positional
                    pos_l=l[fp_pos+1:c_pos]
                    positionals=[]
                    if "," in pos_l:
                        positionals=[parse_arg(k) for k in pos_l.split(",")]
                    else:
                        positionals+=[parse_arg(pos_l)]
                    kw_l=l[c_pos+1:l.rfind(")")]
                    kwargs=[]
                    if "," in kw_l:
                        kwargs+=[parse_arg(k) for k in kw_l.split(",")]
                    else:
                        kwargs+=[parse_arg(kw_l)]
                    arglist.append(ArgumentInfo(args_info=positionals, kwargs_info=kwargs))
                    continue
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
    a=get_function_arguments("a",code)
    for e in a:
        print(e)

