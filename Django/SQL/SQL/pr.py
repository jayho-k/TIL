# from collections import deque

# lst = [1,4,3,2,5,1]
# q = deque(lst)
# print(len(q[:]))
from itertools import permutations

lst = '1 2 3 4 5'
lst2 = ['+','-','*','/']
o_lst = list(permutations(lst2, 4))

lst = lst.split()
for o in o_lst:
    rlst = []
    for i in range(len(lst)):
        rlst.append(lst[i])
        if i == len(lst)-1:
            break
        rlst.append(o[i])

    for j in range(0,5,2):
        pass