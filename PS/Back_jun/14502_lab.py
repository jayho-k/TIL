'''
벽을 세워서 막아야한다. ==> 부분집합의 합을 이용한다
'''
from collections import deque
from copy import deepcopy
import sys

def stp(grid):
    stp_lst = []
    for y in range(n):
        for x in range(m):
            if grid[y][x] == 2:
                stp_lst.append((y,x))
    return stp_lst


def bfs(grid,stp_lst):
    global c_grid
    q = deque(stp_lst)
    c_grid = deepcopy(grid)

    dy = [0,0,1,-1]
    dx = [1,-1,0,0]

    while q:
        y,x = q.popleft()

        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]
            
            if 0<=ny<n and 0<=nx<m and c_grid[ny][nx]==0:
                c_grid[ny][nx] = 2
                q.append((ny,nx))


def w(d):
    global mx_cnt
    if d==3:
        bfs(grid,stp_lst)
        cnt = 0
        for g in c_grid:
            cnt += g.count(0)

        if mx_cnt < cnt:
            mx_cnt = cnt
        return

    for y in range(n):
        for x in range(m):
            if grid[y][x] == 0:
                grid[y][x] = 1
                w(d+1)
                grid[y][x] = 0
                

n,m = map(int, sys.stdin.readline().split())
grid = [list(map(int, sys.stdin.readline().split())) for _ in range(n)]
stp_lst = stp(grid)

mx_cnt = 0
cnt_lst = [0]
w(0)
print(mx_cnt)


# 카피사용안하고 풀기
from collections import deque

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