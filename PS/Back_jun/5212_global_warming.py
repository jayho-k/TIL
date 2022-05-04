
from pprint import pprint


def trans(grid):
    return list(map(list,zip(*grid)))

def mxmn(grid):

    mn = 0
    for g in grid:
        g_cnt = g.count('X')
        if g_cnt == 0:
            mn+=1
        else:
            break

    mx = len(grid)
    for g in grid[::-1]:
        g_cnt = g.count('X')
        if g_cnt == 0:
            mx-=1
        else:
            break

    return mn,mx


n,m = map(int, input().split())
grid = [list(input()) for _ in range(n)]
dy = [0,0,1,-1]
dx = [1,-1,0,0]

chck = [[0]*m for _ in range(n)]
for y in range(n):
    for x in range(m):
        if grid[y][x] == 'X':
            cnt = 0
            for d in range(4):
                ny = y + dy[d]
                nx = x + dx[d]
                if 0<=ny<n and 0<=nx<m and grid[ny][nx] == 'X':
                    cnt += 1

            if cnt <2:
                chck[y][x] = 1

for y in range(n):
    for x in range(m):
        if chck[y][x] == 1:
            grid[y][x] = '.'


y_min, y_max = mxmn(grid)
grid = grid[y_min:y_max]
t_grid = trans(grid)

x_min, x_max = mxmn(t_grid)
t_grid = t_grid[x_min:x_max]
grid = trans(t_grid)


for g in grid:
    print(''.join(g))