'''
5 4
0 0 1 0
0 0 0 0
1 0 0 0
0 0 0 0
0 0 0 1

'''
from collections import deque
import sys
input = sys.stdin.readline

def bfs(y,x):

    q = deque([(y,x)])
    visited = [[0]*m for _ in range(n)]
    visited[y][x] = 1
    if grid[y][x] == 1:
        return 0

    t = 1e9

    dy = [-1,-1,0,1,1,1,0,-1]
    dx = [0,1,1,1,0,-1,-1,-1]

    while q:
        y,x = q.popleft()

        for d in range(8):
            ny = y+dy[d]
            nx = x+dx[d]
            
            if 0<=ny<n and 0<=nx<m and visited[ny][nx] == 0:

                visited[ny][nx] = visited[y][x] + 1
                q.append((ny,nx))

                if grid[ny][nx] == 1:
                    if t > visited[ny][nx]:
                        t = visited[ny][nx]

    return t

n,m = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]

mx = 0
for y in range(n):
    for x in range(m):
        t = bfs(y,x)
        mx = max(mx,t)

print(mx-1)