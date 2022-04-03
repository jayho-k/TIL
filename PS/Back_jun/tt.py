'''

7 7
2 0 0 0 1 1 0
0 0 1 0 1 2 0
0 1 1 0 1 0 0
0 1 0 0 0 0 0
0 0 0 0 0 1 1
0 1 0 0 0 0 0
0 1 0 0 0 0 0

4 6
0 0 0 0 0 0
1 0 0 0 0 2
1 1 1 0 0 2
0 0 0 0 0 2
'''
from collections import deque

from django import views

def stp(grid):
    vi = []
    for y in range(n):
        for x in range(m):
            if grid[y][x] == 2:
                vi.append((y,x))

    return vi 

def bfs(vi):
    global mx

    visited = [[0]*m for _ in range(n)]

    for vy,vx in vi:
        visited[vy][vx] = 2

    q = deque(vi)

    dy = [0,0,1,-1]
    dx = [1,-1,0,0]

    while q:
        y,x = q.popleft()

        for d in range(4):
            ny = y + dy[d]
            nx = x + dx[d]
            if 0<=ny<n and 0<=nx<m and grid[ny][nx] == 0 and visited[ny][nx] == 0:
                visited[ny][nx] = 2
                q.append((ny,nx))

    cnt = 0
    for i in range(n):
        for j in range(m):
            if grid[i][j] == 0 and visited[i][j] == 0:
                cnt += 1

    mx = max(mx, cnt)
    
def dfs(d):
    if d == 3:
        bfs(vi)
        return
    
    for y in range(n):
        for x in range(m):
            if grid[y][x] == 0:
                grid[y][x] = 1
                dfs(d+1)
                grid[y][x] = 0
    
n,m = map(int,input().split())
grid = [list(map(int, input().split())) for _ in range(n)]


vi = stp(grid)
mx = 0
dfs(0)


print(mx)
