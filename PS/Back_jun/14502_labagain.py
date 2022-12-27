'''


7 7
2 0 0 0 1 1 0
0 0 1 0 1 2 0
0 1 1 0 1 0 0
0 1 0 0 0 0 0
0 0 0 0 0 1 1
0 1 0 0 0 0 0
0 1 0 0 0 0 0

'''
from collections import deque
from pprint import pprint
from itertools import permutations,combinations
import sys
input = sys.stdin.readline


# wall에서 3개 뽑기
add_walls2 = set()
# tmp = []
visited_dfs = []
def dfs(grid,no_walls,d,idx):
    
    if d == 3:
        add_walls2.add(tuple(visited_dfs))
        return

    for i in range(idx, len(no_walls)):
        wy,wx = no_walls[i]
        if (wy,wx) not in visited_dfs:
            visited_dfs.append((wy,wx))
            # tmp.append((wy,wx))
            dfs(grid,no_walls,d+1,i+1)
            # tmp.pop()
            visited_dfs.pop()

def bfs(sy,sx):

    q = deque([(sy,sx)])
    setted_visited[sy][sx] = 2
    while q:
        y,x = q.popleft()
        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]
            
            if 0<=ny<n and 0<=nx<m and setted_visited[ny][nx] == 0:
                setted_visited[ny][nx] = 2
                q.append((ny,nx))

    return setted_visited


def wall(grid):
    no_w_lst = []
    w_lst = []
    virus = []
    for wy in range(n):
        for wx in range(m):
            if grid[wy][wx] == 0:
                no_w_lst.append((wy,wx))
            if grid[wy][wx] == 1:
                w_lst.append((wy,wx))
            if grid[wy][wx] == 2:
                virus.append((wy,wx))

    return no_w_lst,w_lst, virus

def wall_setting(visited,w_lst):
    for wy,wx in w_lst:
        visited[wy][wx] = 1
    # for viy,vix in virus:
    #     visited[viy][vix] = 2
    return visited

def check(visited):
    cnt = 0
    for y in range(n):
        for x in range(m):
            if visited[y][x] == 0:
                cnt += 1
    return cnt
            
n,m = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]
dy = [-1,0,1,0]
dx = [0,1,0,-1]
no_w_lst,w_lst,virus = wall(grid)


dfs(grid,no_w_lst,0,0)
add_walls = list(map(list,combinations(no_w_lst,3)))

mx = 0
for add_wall in add_walls2:
    visited = [[0]*m for _ in range(n)]
    setted_visited = wall_setting(visited,w_lst)
    for add_y,add_x in add_wall:
        setted_visited[add_y][add_x] = 1
    for vi_y,vi_x in virus:
        bfs(vi_y,vi_x)
    cnt = check(setted_visited)
    if mx < cnt:
        # pprint(setted_visited)
        mx = cnt
        # mx = max(mx,cnt)
print(mx)


# copy
# [b[:] for g in grid]
# 이렇게 조금 더 빠르다고 한다.