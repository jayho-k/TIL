'''

5 5
1 1 1
1 1 2
1 2 2
1 2 3
3 1
'''
from pprint import pprint
from collections import deque
import sys
input = sys.stdin.readline
n,m = map(int,input().split())
trains = [deque([0]*20) for _ in range(n)]
order = [list(map(int,input().split())) for _ in range(m)]

for o in order:
    if o[0] == 1:
        if trains[o[1]-1][o[2]-1] == 0:
            trains[o[1]-1][o[2]-1] = 1

    elif o[0]==2:
        if trains[o[1]-1][o[2]-1] == 1:
            trains[o[1]-1][o[2]-1] = 0

    elif o[0]==3:
        trains[o[1]-1].appendleft(0)
        trains[o[1]-1].pop()
    else:
        trains[o[1]-1].append(0)
        trains[o[1]-1].popleft()

store = set()
cnt = 0
for i in range(len(trains)):
    t = ''.join(map(str,trains[i]))
    if t not in store:
        store.add(t)
        cnt += 1
    

print(cnt)
