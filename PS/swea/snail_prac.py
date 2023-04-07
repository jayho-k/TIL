"""
1 1 2 2 3 3 4 4
"""
from pprint import pprint

def snail1():
    dy = [-1, 0, 1, 0]
    dx = [0, 1, 0, -1]
    s = 1
    d = 0
    y, x = n // 2, n // 2
    num = 1
    grid[y][x] = num
    while True:
        for _ in range(2):
            for i in range(s):
                ny = y + dy[d]
                nx = x + dx[d]
                num += 1
                grid[ny][nx] = num
                y, x = ny, nx
                if y == 0 and x == 0:
                    return
            d = (d + 1) % 4
        s += 1

def snail2():
    dy = [1,0,-1,0]
    dx = [0,1,0,-1]
    y,x = 0,0
    d = 0
    num = 1
    grid2[y][x]=num
    while True:
        num+=1
        ny = y+dy[d]
        nx = x+dx[d]

        if 0<=ny<n and 0<=nx<n and grid2[ny][nx]==0:
            grid2[ny][nx]=num
            y,x = ny,nx

        else:
            d=(d+1)%4
            num-=1

        if (y, x) == (n//2, n//2):
            return

n = 7
grid = [[0]*n for _ in range(n)]
grid2 = [[0]*n for _ in range(n)]

snail1()
pprint(grid)

snail2()
pprint(grid2)



