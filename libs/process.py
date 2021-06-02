import psutil


def kill_recursive(proc_pid):
    try:
        process = psutil.Process(proc_pid)
    except Exception as e:
        print("KILL ERROR {} : {}".format(proc_pid, e))
        return 
    for proc in process.children(recursive=True):
        try:
            print("killing {}".format(proc.pid))
            proc.kill()
        except Exception as e:
            print("KILL ERROR {} : {}".format(proc.pid,e))
    try:
        print("killing {}".format(process.pid))
        process.kill()
    except Exception as e:
        print("KILL ERROR {} : {}".format(process.pid, e))

def get_child_pids(proc_pid):
    a=[]
    process=psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        a.append(proc.pid)
    return a

