'''

'''

from collections import deque
n = int(input())
q = deque(list(range(1,n+1)))


while q:
    tmp1 = q.popleft()
    if not q:
        break
    tmp2 = q.popleft()
    q.append(tmp2)
    
print(tmp1)
