'''





'''
from collections import deque

lst = list(range(100))
lst2 = list(range(100))

q = deque(lst)
nq = len(q)

# while q:
# for i in range(len(q)):
#     q.popleft()
#     print('q',i)

while q:
    for j in range(nq):
        q.popleft()
        print('nq',j)
        q.append()
