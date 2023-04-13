from collections import deque
def setting(plans):
    
    tmp = []
    for p_name, p_st, p_time in plans:
        t = p_st.split(':')
        tmp.append((int(t[0])*60+int(t[1]),int(p_time), p_name))
    tmp.sort()
    return tmp

def solution(plans):
    
    
    q = deque(setting(plans))
    stack = []
    ans = []
    
    while q:
        
        if len(q)==1:
            _,_,name = q.popleft()
            ans.append(name)
            break
            
        cr_st, cr_time, cr_name = q.popleft()
        nx_st, nx_time, nx_name = q[0]
        
        if cr_st+cr_time < nx_st:
            new_time = cr_st+cr_time
            ans.append(cr_name)
            
            while stack:
                st_st, st_time, st_name = stack.pop()
                if new_time+st_time <= nx_st:
                    ans.append(st_name)
                    new_time += st_time
                    
                else:
                    stack.append((new_time,st_time-(nx_st-new_time),st_name))
                    break

        elif cr_st+cr_time == nx_st:
            ans.append(cr_name)

        else:
            diff = nx_st-cr_st
            stack.append((nx_st,cr_time-diff,cr_name))
    
    while stack:
        _,_,name = stack.pop()
        ans.append(name)
    
    return ans
    
if __name__ == '__main__':
    plans =[["aaa", "12:00", "20"], ["bbb", "12:10", "30"], ["ccc", "12:40", "10"]]
    print(solution(plans))