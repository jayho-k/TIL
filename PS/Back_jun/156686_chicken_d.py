'''
치킨 배달~~~

stp의 개수가 정해져 있음
완탐 ㄱ
1. 시작 지점 세팅을 어떻게 정해주어야 하는가?
    일단 치킨이 있는 곳을 다 lst에 넣어준다
2. visited를 어떻게 설정을 해주는가?
3. 그것만 되면 visieted의 거리의 합을 구하면 된다.
'''
from sys import stdin
from collections import deque

def stp(grid):
    lst = []
    for y in range(n):
        for x in range(n):
            if grid[y][x] == 2:
                lst.append((y,x))

    return lst

def sel(d,m):
    if d == m:
        st_p= []
        for m_i in range(stn):
            if lst[m_i] ==1:
                st_p.append(stp_lst[m_i])
        #stp
        return

    for i in range(stn):
        if lst[i] == 0:
            lst[i] = 1
            sel(d+1,m)
            lst[i] = 0

def bfs(grid,st_p):

    pass

n, m = map(int, stdin.readline().split())
grid = [list(map(int, stdin.readline().split())) for _ in range(n)]

stp_lst = stp(grid)

stn = len(stp_lst)
lst = [0]*stn
sel(0,m)
