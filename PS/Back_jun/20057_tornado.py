'''

5
0 0 0 0 0
0 0 0 0 0
0 100 0 0 0
0 0 0 0 0
0 0 0 0 0

'''
from pprint import pprint
import sys

def tornado(y,x,d):
    out_of_grid = 0
    total_sand = grid[y][x]
    total_rate_sand = 0
    grid[y][x] = 0
    d_sand_y = sand_y[d]
    d_sand_x = sand_x[d]
    for i in range(9):
        new_sand_y = y+d_sand_y[i]
        new_sand_x = x+d_sand_x[i]
        rate_sand = int(rate[i]*total_sand)
        total_rate_sand += rate_sand
        if 0<=new_sand_y<n and 0<=new_sand_x<n:
            grid[new_sand_y][new_sand_x] += rate_sand
        else:
            out_of_grid+=rate_sand

    alpha = total_sand-total_rate_sand
    ny = y+dy[d]
    nx = x+dx[d]
    if 0<=ny<n and 0<=nx<n:
        grid[ny][nx] += alpha
    else:
        out_of_grid+=alpha

    return out_of_grid

# while (s) => for2(d) => for speed
# 리뷰 해줘야할듯
def move(start):
    y,x = start
    speed = 1
    d = 0
    out = 0
    while True:
        for _ in range(2):
            for _ in range(speed):
                ny = y+(dy[d])
                nx = x+(dx[d])
                out += tornado(ny,nx,d)
                y = ny
                x = nx
                if y==0 and x==0:
                    return out
            d = (d+1)%4
        speed+=1

sand1 = [0,-1,-1,-1,-2,1,1,1,2]
sand2 = [2,1,0,-1,0,1,0,-1,0]
sand_y = {
    0:sand1,
    1:sand2,
    2:list(map(lambda x:x*-1,sand1)),
    3:list(map(lambda x:x*-1,sand2))}

sand_x = {
    0:list(map(lambda x:x*-1,sand2)),
    1:list(map(lambda x:x*-1,sand1)),
    2:sand2,
    3:sand1}

rate = [0.05,0.1,0.07,0.01,0.02,0.1,0.07,0.01,0.02]

input = sys.stdin.readline
n = int(input())
start = (n//2,n//2)
grid = [list(map(int,input().split())) for _ in range(n)]
dy = [0,1,0,-1]
dx = [-1,0,1,0]
out = move(start)
print(out)