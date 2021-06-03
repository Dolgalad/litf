"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:breif: functions for manipulating python function and class definitions
"""
import re

class f_arg:
    def __init__(self,key,dtype=None):
        self.key=key
        self.dtype=dtype
    def __str__(self):
        return "f_arg (key:{},dtype:{})".format(self.key,self.dtype)
    def data(self):
        return {"key":self.key, "dtype":self.dtype}

class f_kwarg(f_arg):
    def __init__(self,key,default):
        super().__init__(key)
        self.default=default
    def __str__(self):
        return "f_kwarg (key:{},default:{},dtype:{})".format(self.key,self.default,self.dtype)
    def data(self):
        a=super().data()
        a["default"]=self.default
        return a

def parse_arg(a):
    if "=" in a:
        b=a.split("=")
        return f_kwarg(key=b[0].strip(), default=b[1].strip())
    return f_arg(a.strip())

class ArgumentInfo:
    def __init__(self, args=[]):

        self.args_info=[]
        self.kwargs_info=[]
        for a in args:
            if isinstance(a,f_arg):
                self.args_info.append(a)
            else:
                self.kwargs_info.append(a)
    def data(self):
        a={"args":[a.data() for a in self.args_info]}
        a["kwargs"]=[a.data() for a in self.kwargs_info]
        return a
    def __len__(self):
        return self.n_positional()+self.n_keyword()
    def n_positional(self):
        return len(self.args_info)
    def n_keyword(self):
        return len(self.kwargs_info)
    def __str__(self):
        a="ArgumentInfo : n_args={}, n_kwargs={}\n".format(self.n_positional(),self.n_keyword())
        if self.__len__()==0:
            return a
        for ar in self.args_info:
            a+="\t{}\n".format(ar)
        for ar in self.kwargs_info:
            a+="\t{}\n".format(ar)
        return a
    def has_keyword(self, k):
        for kw in self.kwargs_info:
            if k==kw.key:
                return True
        for a in self.args_info:
            if k==a.key:
                return True
        return False
    def get_kwarg_info(self, k):
        for kw in self.kwargs_info:
            if kw.key==k:
                return kw
        for kw in self.args_info:
            if kw.key==k:
                return kw
        return None
    def compatible_with(self, *args, **kwargs):
        # if total number of arguments is less then number of positionals then false
        if self.n_positional()>len(args)+len(kwargs):
            print("Not enough arguments")
            return False
        # if total number of arguments is greater then number of positional and kw arguments then false
        if len(self)<(len(args)+len(kwargs)):
            print("Too many arguments")
            return False
        
        # check that all keywords correspond to an argument
        for k in kwargs:
            if not self.has_keyword(k):
                print("Keyword {} corresponds to no argument".format(k))
                return False
        # check types for compatibility
        # check positionals
        for i in range(self.n_positional()):
            if self.contains_packed_args():
                break
            if self.args_info[i].dtype is None:
                continue
            else:
                if self.args_info[i].dtype != str(type(args[i])):
                    print("Type mismatch for positional arg {} : {} != {}".format(i,\
                            self.args_info[i].dtype, str(type(args[i]))))
                    return False
        for k in kwargs:
            kw=self.get_kwarg_info(k)
            if kw is None:
                print("No keyword argument with key {}".format(k))
                return False
            if kw.dtype is None:
                continue
            else:
                if kw.dtype != str(type(kwargs[k])):
                    print("Keyword argument type mismatch for key {}: expected {} , got {}".format(k, kw.dtype, \
                            str(type(kwargs[k]))))
                    return False
        return True
        



closing={"(":")","[":"]","{":"}","'":"'","\"":"\""}
def get_content(s,opening):
    c=""
    while len(s):
        # s starts with closing character then return
        if s[0]==closing[opening]:
            return c,s
        if s[0] in closing:
            o=s[0]
            t_c,s=get_content(s[1:],o)
            c+=o+t_c+s[0]
            s=s[1:]
            continue

        c+=s[0]
        s=s[1:]
    return c,""
        

def get_next_arg(s):
    """Returns the next argument info object. s is a string with format ::
      
      var1, var2, var3, ..., kw_var1=default1, kw_var2=default2,...
      
    :param s: input arguments string
    :type s: string
    :return: next argument info object and rest of string
    :rtype: tuple(ArgList or NoneType, str)
    """
    # strip spaces
    s=s.strip()
    # next comma position
    nc_pos=s.find(",")
    # if no commas 
    if nc_pos<0:
        # if s is empty then no arguments
        if len(s)==0:
            return "",""
        else:
            # might be a positional or keyword argument
            return s,""
            return ArgInfo.from_string(s)
    c=""
    while len(s):
        if s[0] in closing:
            o=s[0]
            t_c,s=get_content(s[1:],s[0])
            c+=o+t_c+s[0]
            s=s[1:]
            continue
        if s[0]==",":
            return c,s[1:]
        c+=s[0]
        s=s[1:]
    return c,""

    
def get_f_args(f_name, code):
    """Returns an ArgList object containing the function argument information based on the 
    contents of the code variable. If multiple definitions for the same function are found then 
    a list is returned.

    :param f_name: function name
    :type f_name: str
    :param code: code
    :type code: str
    :return: argument description for the function
    :rtype: ArgList, list
    """
    # get the function definition regex
    r='^[ ]*def[ ]+{}[ ]*\((?P<args>.*)\)[ ]*:[ ]*$'.format(f_name)
    r="[ ]*def[ ]+{}\((?P<args>.*)\)".format(f_name)
    # for line in code
    a=[]
    for l in code.split("\n"):
        res=re.match(r, l)
        if res:
            test=res.groups(0)[0]
            cc=[]
            while len(test):
                tt,test=get_next_arg(test)
                cc.append(tt)
            a.append(ArgumentInfo([parse_arg(s) for s in cc]))
    if len(a)==0:
        return None
    if len(a)==1:
        return a[0]
    return a

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
def a   (   x, \
        y  ,\
        z=1)   :   
    return 6
def a(x=(1,2), y=2, z=[1,2,3]):
    pass
def a(x="azer", y='azer', z={1:1,2:2}):
    pass
def a(*args, **kwargs):
    pass
"""
    
    A=get_f_args("a",code)
    for a in A:
        print(a)
        print(a.compatible_with(12,13,15))
        print(a.compatible_with(**{"x":1,"y":2,"z":3}))
        print(a.compatible_with(x=1,y=2,z=3,t=1))


    
