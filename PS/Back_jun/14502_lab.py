'''
벽을 세워서 막아야한다. ==> 부분집합의 합을 이용한다
'''
from pprint import pprint
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
# print(cnt_lst[-1])
print(mx_cnt)
