







if __name__=="__main__":
    openings={"(":")", "{":"}", "[":"]"}
    
    def next_delimiter(s):
        n_p,n_d=None, None
        for k in openings:
            k_pos=s.find(k)
            if k_pos==-1:
                continue
            if n_p is None:
                n_p=k_pos
                n_d=k
            else:
                if k_pos < n_p:
                    n_p=k_pos
                    n_d=k
        return n_p,n_d
    def get_next(s,delimiter=","):
        # search for next delimiter character
        next_dpos=s.find(delimiter)
        if next_dpos==-1:
            return s,""
        # get next delimiter
        d_pos,d=next_delimiter(s)
        # if delimiter comes before the comma
        if d_pos is None:
            print("no opening")
            print(next_dpos)
            return s[:next_dpos],s[next_dpos+1:]

        if next_dpos<d_pos : 
            print("no opening")
            return s[:next_dpos],s[next_dpos+1:]
        else:
            print("openingin")
            a=s.find(openings[d])
            return s[:a+1], s[a+2:]
            pass

               

    s="x, y, z, a=1, b=(2,1), c=[1,3], d=(1,1,1)):"
    while len(s):
        w,s=get_next(s)
        print(w)
