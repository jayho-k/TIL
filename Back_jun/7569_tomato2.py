'''


h 는 1부터 나머지 2부터
'''
import sys
from collections import deque

def stp(grid,m,n,h1):
    stp_lst = []
    for h in range(h1):
        for y in range(n):
            for x in range(m):
                if grid[h][y][x] == 1:
                    stp_lst.append((h,y,x))
    
    return stp_lst

def bfs(grid, lst):
    q = deque(lst)
    dh = [0,0,0,0,1,-1]
    dy = [0,0,1,-1,0,0]
    dx = [1,-1,0,0,0,0]

    while q:
        h,y,x = q.popleft()
        for d in range(6):
            nh = h + dh[d]
            ny = y + dy[d]
            nx = x + dx[d]

            if 0<=nh<h1 and 0<=ny<n and 0<=nx<m and grid[nh][ny][nx]!=-1 and grid[nh][ny][nx]==0:
                grid[nh][ny][nx] = grid[h][y][x] + 1
                q.append((nh,ny,nx))

    return grid

# m, n, h1 = map(int, input().split())
m, n, h1 = map(int, sys.stdin.readline().split())

grid = []
for i in range(h1):
    g = [list(map(int, sys.stdin.readline().split())) for _ in range(n)]
    grid.append(g)

stp_lst = stp(grid)

n_grid = bfs(grid, stp_lst)

lst = []
for g in n_grid:
    for l in g:
        lst += l

if 0 in lst:
    print(-1)
else:
    print(max(lst)-1)