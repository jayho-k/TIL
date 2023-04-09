"""
여러가지 스킬들 구현하기

1. 기본) 90, -90도 회전
2. 분할) 90
3. time
4. c2o 달팽이
5. 기차
"""
from pprint import pprint
from collections import deque
# 1. 기본) 90, -90도 회전
def basic_90(mode):
    n = 7
    grid = [list(range(1,n+1)) for _ in range(n)]
    n_grid = [[0]*n for _ in range(n)]
    for y in range(n):
        for x in range(n):
            if mode==1:
                n_grid[y][x] = grid[x][n-1-y]
            elif mode==2:
                n_grid[y][n-1-x] = grid[x][y]
    pprint(grid)
    pprint(n_grid)
    print()

# 2. 분할) 90
def div_90(mode):
    n = 6
    grid = [list(range(1,n+1)) for _ in range(n)]
    n_grid = [[0]*n for _ in range(n)]
    for y in range(0,n,n//2):
        for x in range(0,n,n//2):
            for i in range(n//2):
                for j in range(n//2):
                    if mode==1:
                        n_grid[y+j][x+(n//2)-1-i] = grid[y+i][x+j]

                    # 왼쪽 -90 오른쪽 +90
                    elif mode==2:
                        if x<n//2:
                            n_grid[y + j][x+i] = grid[y + i][x+(n//2)-j-1]
                        else:
                            n_grid[y + j][x + (n // 2) - 1 - i] = grid[y + i][x + j]

# 3. time
def time_setting():
    lst = [1,2,3,4,4,4,4,5,6,7,7,8,9]
    q = deque(lst)
    time = 5
    while q and q[0]<time:
        print(q.popleft())

# 4.c2o 달팽이
def c2o_snail():
    n = 7
    grid = [[0] * n for _ in range(n)]
    num = 1
    dy = [-1,0,1,0]
    dx = [0,1,0,-1]
    y,x = n//2,n//2
    grid[y][x]=num
    d = 0
    s = 1
    for _ in range(10):
        for _ in range(2):
            for i in range(s):
                ny = y+dy[d]
                nx = x+dx[d]
                num+=1
                grid[ny][nx]=num
                if i==s-1:
                    d = (d + 1) % 4

                y,x = ny,nx
                if (y,x) == (0,0):
                    pprint(grid)
                    return
        s+=1

def train():
    # 1. 머리를 뽑는다.
    # 2. 이동 시킴
    # 3. after_move를 시킨다.
    dy = [-1,0,1,0]
    dx = [0,1,0,-1]
    grid = [
        [1, 2, 3],
        [4, 0, 4],
        [4, 0, 4]
    ]
    n = len(grid)
    team = [(0,0),(0,1),(0,2)]
    hy,hx = team[0]
    after_move = []

    # 머리 이동
    for d in range(4):
        hny = hy+dy[d]
        hnx = hx+dx[d]
        if 0<=hny<n and 0<=hnx<n and (grid[hny][hnx]==4 or grid[hny][hnx]==3):
            after_move.append((hny,hnx))

    # 나머지 이동

    for i in range(len(team)-1):
        grid[team[i][0]][team[i][1]]=4
        after_move.append(team[i])
    grid[team[-1][0]][team[-1][1]] = 4

    for j,(ay,ax) in enumerate(after_move):
        if j==0:
            grid[ay][ax]=1
        elif j==len(after_move)-1:
            grid[ay][ax] = 3
        else:
            grid[ay][ax] = 2
    pprint(grid)






