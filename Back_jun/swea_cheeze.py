'''
3
3 5 
7 2 6 5 3
5 10
5 9 3 9 9 2 5 8 7 1
5 10
20 4 5 7 3 15 2 1 2 2
'''
from collections import deque

T = int(input())
for tc in range(1, T+1):
    n, m = map(int, input().split())
    l = map(int, input().split())
    lst = list(map(list, enumerate(l, start=1)))
    # print(lst)

    rst = deque(lst[n:])
    q = deque(lst[:n])
    
    for n_rst in rst:
        while 1:
            q[0][1]=q[0][1]//2
            # print(q)
            if q[0][1] == 0:
                q.popleft()
                q.appendleft(n_rst)
                # print('end',q)
                break
            else:
                q.rotate(-1)
    
    while q:
        q[0][1]=q[0][1]//2
        # print(q)
        if q[0][1] == 0:
            ans = q.popleft()
        else:
            q.rotate(-1)
    
    print(f'#{tc} {ans[0]}')