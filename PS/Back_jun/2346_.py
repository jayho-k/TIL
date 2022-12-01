'''

5
3 2 1 -3 -1

'''

from collections import deque

n = int(input())
q = deque(list(map(int,input().split())))
tmp = deque(list(range(n)))
lst = []
while q:

    # print(q)
    m = q.popleft()
    ti = tmp.popleft()
    lst.append(ti+1)
    if m > 0:
        q.rotate(1-m)
        tmp.rotate(1-m)
    
    elif m < 0:
        q.rotate(-m)
        tmp.rotate(-m)

print(*lst)
