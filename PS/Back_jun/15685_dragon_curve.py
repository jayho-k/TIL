'''

오른쪽
x, y, d, g

3
3 3 0 1
4 2 1 3
4 2 2 1
'''

# 90도 회전
rotaion={
    0:1,
    1:2,
    2:3,
    3:0
}
def direction(d,g):

    direction_lst = [d]
    for _ in range(g):
        co_dir = direction_lst[::-1]
        for t in co_dir:
            direction_lst.append(rotaion[t])

    return direction_lst

def draw(y,x,direction_lst):

    grid[y][x] = 1
    for d in direction_lst:
        ny = y+dy[d]
        nx = x+dx[d]
        grid[ny][nx] = 1
        y = ny
        x = nx

def check(drew_grid):
    cnt = 0
    for y in range(100):
        for x in range(100):
            if drew_grid[y][x] and drew_grid[y+1][x] and drew_grid[y][x+1] and drew_grid[y+1][x+1]:
                cnt +=1
    return cnt                

from pprint import pprint

n = int(input())
curves = [tuple(map(int,input().split())) for _ in range(n)]
grid = [[0]*101 for _ in range(101)]
dy = [0,-1,0,1]
dx = [1,0,-1,0]

for x,y,d,g in curves:
    direction_lst = direction(d,g)
    draw(y,x,direction_lst)

squ_check = check(grid)
print(squ_check)
    
