'''
바이러스 위치 정함
m개 뽑음
bfs돌림
    => 2만남
    => 

반복

 '''

from itertools import combinations
from collections import deque
from pprint import pprint

def vi(grid):
    lst = []
    cnt = 0
    for y in range(n):
        for x in range(n):
            if grid[y][x] == 2:
                lst.append((y,x))

            if grid[y][x] == 0:
                cnt += 1

    return lst, cnt

def bfs(stp):

    # 비있는게 다 채워지기만 하면 된다
    global zero

    mx = 0
    q = deque(stp)
    visited = [[0]*n for _ in range(n)]
    for sy,sx in stp:
        visited[sy][sx] = 1
        
    dy = [0,0,1,-1]
    dx = [1,-1,0,0]

    while q:
        y,x = q.popleft()

        for d in range(4):
            ny = y + dy[d]
            nx = x + dx[d]

            if 0<=ny<n and 0<=nx<n and visited[ny][nx] == 0:
                if grid[ny][nx] == 0:
                    visited[ny][nx] = visited[y][x] + 1
                    q.append((ny,nx))
                    mx = max(mx, visited[ny][nx])
                    zero -= 1

                if grid[ny][nx] == 2:
                    visited[ny][nx] = visited[y][x] + 1
                    q.append((ny,nx))
                    mx = max(mx, visited[ny][nx])

                if zero == 0:
                    return mx

    for i in range(n):
        for j in range(n):
            if grid[i][j] == 0 and visited[i][j] == 0:
                return 1e9

n,m = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]
vi_lo, z = vi(grid)
ch_vi = list(map(list,combinations(vi_lo,m)))

mn = 1e9

if z == 0:
    mn = 1
else:
    for ch in ch_vi:
        zero = z
        mx = bfs(ch)
        mn = min(mn, mx)
    
if mn == 1e9:
    print(-1)
else:
    print(mn-1)
