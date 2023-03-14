'''

1
4
0100
1110
1011
1010

'''
from collections import deque
def bfs(y,x,n):
    q = deque([(y,x)])
    val = [[1e9]*n for _ in range(n)]
    val[y][x]=0
    while q:
        y,x = q.popleft()
        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]
            if 0<=ny<n and 0<=nx<n and val[ny][nx]>val[y][x]+grid[ny][nx]:
                val[ny][nx]=val[y][x]+grid[ny][nx]
                q.append((ny,nx))

    return val[n-1][n-1]

dy = [-1,0,1,0]
dx = [0,1,0,-1]
for tc in range(1,int(input())+1):

    n = int(input())
    grid = [list(map(int,list(input()))) for _ in range(n)]
    v = bfs(0,0,n)
    print(f"{tc} {v}")
    