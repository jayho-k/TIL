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

# 토네이도
def tornado(y,x,d):

    out_of_grid = 0
    total_sand = grid[y][x]
    grid[y][x] = 0
    
    total_rate_sand = 0
    d_sand_y = sand_y[d]
    d_sand_x = sand_x[d]


    # 총 9개의 비율을 가진 것을 순서대로 계산
    # rate = [0.05,0.1,0.07,0.01,0.02,0.1,0.07,0.01,0.02]
    # d_sand_y, d_sand_x => 비율의 방향
    for i in range(9):
        new_sand_y = y+d_sand_y[i]
        new_sand_x = x+d_sand_x[i]
        rate_sand = int(rate[i]*total_sand)

        total_rate_sand += rate_sand
        if 0<=new_sand_y<n and 0<=new_sand_x<n:
            grid[new_sand_y][new_sand_x] += rate_sand
        
        # 밖에 나갔을 경우
        else:
            out_of_grid+=rate_sand

    # 알파값 계산
    alpha = total_sand-total_rate_sand
    ny = y+dy[d]
    nx = x+dx[d]
    if 0<=ny<n and 0<=nx<n:
        grid[ny][nx] += alpha

    # 밖에 나갔을 경우
    else:
        out_of_grid+=alpha

    return out_of_grid

# 1) 달팽이 구현
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

# 2) 흙뿌리기 규칙
sand1 = [0,-1,-1,-1,-2,1,1,1,2]
sand2 = [2,1,0,-1,0,1,0,-1,0]

sand_y = {
    0:sand1,
    1:sand2,
    2:list(map(lambda x:x*-1,sand1)),
    3:list(map(lambda x:x*-1,sand2))}

sand_x = {
    0:list(map(lambda x:x*-1,sand2)),
    1:sand1,
    2:sand2,
    3:list(map(lambda x:x*-1,sand1)),
    # 1:list(map(lambda x:x*-1,sand1)),
    # 3:sand1
    }

for i in range(4):
    lst = []
    for j in range(9):
        lst.append((sand_y[i],sand_x[i]))

rate = [0.05,0.1,0.07,0.01,0.02,0.1,0.07,0.01,0.02]

# input
input = sys.stdin.readline
n = int(input())
start = (n//2,n//2)
grid = [list(map(int,input().split())) for _ in range(n)]
dy = [0,1,0,-1]
dx = [-1,0,1,0]
out = move(start)
print(out)