"""
3
1 21 79
20 30 25
"""
from pprint import pprint
n = int(input())
hpList = [0]+list(map(int,input().split()))
joyList = [0]+list(map(int,input().split()))

dpTable = [[0]*101 for _ in range(n+1)]

for y in range(1,n+1):
    for x in range(1,101):
        hp,joy = hpList[y],joyList[y]
        if x<hp:
            dpTable[y][x] = dpTable[y-1][x]

        else:
            dpTable[y][x] = max(dpTable[y-1][x-hp]+joy,dpTable[y-1][x])

print(dpTable[n][99])
