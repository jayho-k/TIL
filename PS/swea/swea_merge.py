'''
분할
'''
from collections import deque

def merge(lst):

    if len(lst)==1:
        return lst

    m = len(lst)//2

    l = merge(lst[:m])
    r = merge(lst[m:])

    return msort(deque(l),deque(r))

def msort(l,r):
    global cnt
    if l[-1] > r[-1]:
        cnt +=1

    ans = []
    while l or r:

        if l and r:

            if l[0] <= r[0]:
                ans.append(l.popleft())
            else:
                ans.append(r.popleft())

        elif l:
            ans.extend(l)
            break
        
        elif r:
            ans.extend(r)
            break
        
    return ans

T = int(input())

for tc in range(1,T+1):

    n = int(input())
    lst = list(map(int, input().split()))
    
    cnt =0

    a = merge(lst)

    print(f'#{tc} {a[len(lst)//2]} {cnt}')