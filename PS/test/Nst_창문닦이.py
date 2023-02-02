'''
grid=[
    [0,11,10,9],
    [8,7,6,5],
    [4,3,2,1],
    [1,2,3,4]
]
ycost=2
xcost=1

조건1
오른쪽 아래로만 움직일 수 있음

조건2
오른쪽으로 갈때 xcost가 들고
아래로 움직일때 ycost가 든다

조건3
grid에 칸을 지날때 그 칸의 cost를 얻을 수 있음

조건4
가장 많은 cost를 얻을 수 있는 값은 무엇인가?

maybe ans
7

bfs()
dp()
'''
from pprint import pprint
grid=[
    [0,11,10,9],
    [8,7,6,5],
    [4,3,2,1],
    [1,2,3,4]
]
ycost=2
xcost=1
n = len(grid)

def make_cost_table(n):
    cost_table = [[0]*(n+1) for _ in range(n+1)]
    for i in range(2,n+1):
        cost_table[1][i]=-xcost+cost_table[1][i-1]

    for y in range(2,n+1):
        for x in range(1,n+1):
            cost_table[y][x]=cost_table[y-1][x]-ycost
    return cost_table

def make_dp_table(grid):
    cost_table = make_cost_table(n)
    dp_table = [[0]*(n+1) for _ in range(n+1)]
    for y in range(1,n+1):
        for x in range(1,n+1):
            dp_table[y][x] = grid[y-1][x-1] + cost_table[y][x]

    return dp_table

dp_table = make_dp_table(grid)
dp = [[0]*(n+1) for _ in range(n+1)]
for y in range(1,n+1):
    for x in range(1,n+1):
        if y==1:
            dp[y][x] = dp_table[y][x]+dp[y][x-1]
        else:
            dp[y][x] = max(dp[y-1][x],dp[y][x-1])+dp_table[y][x]
pprint(dp)
pprint(dp_table)

