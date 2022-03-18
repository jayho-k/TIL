'''





'''
from collections import deque

lst = [1,2,3,4,5,6]

q = deque(lst)
nq = len(q)
# for i in range(len(q)):
#     q.popleft()
#     print('q',i)


for j in range(nq):
    q.popleft()
    print('nq',j)