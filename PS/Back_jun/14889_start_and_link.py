'''
6
0 1 2 3 4 5
1 0 2 3 4 5
1 2 0 3 4 5
1 2 3 0 4 5
1 2 3 4 0 5
1 2 3 4 5 0

'''

tmp = []
def dfs(d,i):
    global ans
    if d == n//2:
        tmp2 = []
        for k in range(len(lst)):
            if lst[k] not in tmp:
                tmp2.append(lst[k])
        lst1 = list(permutations(tmp,2))
        lst2 = list(permutations(tmp2,2))
        total1 = 0
        total2 = 0

        for l1y,l1x in lst1:
            total1 += grid[l1y][l1x]

        for l2y,l2x in lst2:
            total2 += grid[l2y][l2x]

        ans = min(ans, abs(total1-total2))

    for i in range(i,len(lst)):
        if lst[i] not in tmp:
            tmp.append(lst[i])
            dfs(d+1,i)
            tmp.pop()

import sys
from pprint import pprint
from itertools import permutations

input = sys.stdin.readline
n = int(input())
grid = [list(map(int,input().split())) for _ in range(n)]
lst = list(range(n))
ans = 1e9
dfs(0,0)
print(ans)
