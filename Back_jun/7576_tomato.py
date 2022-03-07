'''
6 4
0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 1
'''
from pprint import pprint
from collections import deque

def stp(grid):
    st_lst = []
    for y in range(n):
        for x in range(m):
            if grid[y][x] == 1:
                st_lst.append((y,x))
    
    return st_lst

def bfs(st_lst):
    
    q = deque(st_lst)
    # 동서남북
    dy = [0,0,1,-1]
    dx = [1,-1,0,0]

    # 첫 삽입
    while q:
        y, x = q.popleft()
        for d in range(4):
            ny = y + dy[d]
            nx = x + dx[d]
            if 0<=ny<n and 0<=nx<m and grid[ny][nx] != -1 and grid[ny][nx] == 0:
                q.append((ny,nx))
                grid[ny][nx] = grid[y][x] + 1
    return grid

                
            
# 시작
m, n = map(int, input().split())
grid = [list(map(int, input().split())) for _ in range(n)]

st_lst = stp(grid)
# print(st_lst)


b_grid = bfs(st_lst)

# pprint(b_grid)

ans_lst = []
for g in b_grid:
    ans_lst+= g

if 0 in ans_lst:
    print(-1)

else:
    print(max(ans_lst)-1)