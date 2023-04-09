"""
5 24 20 82
4 5 2
2 1 1
1 4 2
2 5 1
1 1 1
1 3 1
5 3 1
3 1 2
3 5 2
4 4 2
4 3 2
2 2 2
3 2 2
1 2 2
1 5 1
5 1 1
4 1 2
2 3 2
2 4 1
5 4 1
5 2 2
4 2 2
3 4 1
5 5 1
3 2
3 5
2 2
4 2
3 3
5 4
3 4
5 5
2 4
2 3
1 1
2 5
5 1
1 2
5 3
4 4
2 1
4 5
1 4
4 3

5 3 1 1
2 4 1
1 4 2
4 2 1
2 4

5 3 1 26
2 4 1
1 4 2
4 2 1
2 4
"""
from pprint import pprint
from collections import deque

def make_dydx(y,x,num):
    if num == 1:
        ny = y + dy_lr[d]
        nx = x + dx_lr[d]
    else:
        ny = y + dy_ud[d]
        nx = x + dx_ud[d]
    return ny,nx


def esc_move(gy,gx,esc_per):
    res = []
    runs = []

    # esc나누기
    for i in range(len(esc_per)):
        ey, ex, num,d = esc_per[i]
        if abs(gy-ey)+abs(gx-ex)<=3:
            runs.append((ey,ex,num,d))
        else:
            res.append((ey,ex,num,d))

    #
    for ry,rx,r_num,d in runs:
        ny,nx = make_dydx(ry,rx,r_num)
        if 0<=ny<n and 0<=nx<n:
            if (ny,nx)!=(gy,gx):
                res.append((ny,nx,r_num,d))
            else:
                res.append((ry,rx,r_num,d))

        else:
            d=(d+1)%2
            ny, nx = make_dydx(ry, rx, r_num)
            if (ny, nx) != (gy, gx):
                res.append((ny, nx, r_num, d))
            else:
                res.append((ry, rx, r_num, d))

    return res

def check(d,y,x,esc_per,num):
    res = set()
    res_esc_per = []

    # 자신 포함 3칸 check
    for i in range(3):
        ny = y+dy[d]*i
        nx = x+dx[d]*i
        if 0<=ny<n and 0<=nx<n and (ny,nx) not in trees:
            res.add((ny,nx))

    # 잡히면 제외 아니면 res
    caught = 0
    for ey,ex,e_num,d in esc_per:
        if (ey,ex) in res:
            caught+=1
            continue
        res_esc_per.append((ey,ex,e_num,d))

    return res_esc_per, num*caught


def make_cen2zero(y,x):
    s = 1
    d = 0
    cen2zero = [(y,x,d)]
    while True:
        for _ in range(2):
            for i in range(s):
                # 1칸이동
                ny = y+dy[d]
                nx = x+dx[d]

                # 방향을 바꾸고 상태로 만들때
                if i == s-1:
                    d = (d + 1) % 4
                    cen2zero.append((ny, nx, d))
                    y,x = ny,nx
                    break


                cen2zero.append((ny, nx, d))
                y,x = ny,nx
                if (y, x) == (0, 0):
                    cen2zero.pop()
                    return cen2zero
        s+=1

def make_zero2cen(y,x):

    visited = [[0] * n for _ in range(n)]
    d = 2
    visited[y][x] = 1
    zero2cen = [(y,x,d)]
    while True:
        # 1칸 이동
        ny = y + dy[d]
        nx = x + dx[d]

        if 0 <= ny <n and 0 <= nx < n and visited[ny][nx] == 0:
            zero2cen.append((ny,nx,d))
            visited[ny][nx]=1
            y, x = ny, nx
            if (y, x) == (n // 2, n // 2):
                zero2cen.pop()
                return zero2cen

        else:
            d = (d - 1) % 4

            # 마지막이 필요가 없을 경우 pop()
            zero2cen.pop()
            zero2cen.append((y, x, d))
            visited[y][x] = 1


# setting
n,m,h,k = map(int,input().split())
grid = [[0]*n for _ in range(n)]
tree_grid = [[0]*n for _ in range(n)]
esc_per = []
trees = set()
dy_lr = [0,0]
dx_lr = [1,-1]
dy_ud = [1,-1]
dx_ud = [0,0]
dy = [-1, 0, 1, 0]
dx = [0, 1, 0, -1]

for _ in range(m):
    y,x,num = map(int, input().split())
    esc_per.append((y-1,x-1,num,0))
    grid[y-1][x-1]=num
for _ in range(h):
    y,x = map(int, input().split())
    trees.add((y-1,x-1))
    tree_grid[y-1][x-1]=1

cen2zero = make_cen2zero(n//2,n//2)
zero2cen = make_zero2cen(0,0)
cz_lst = cen2zero+zero2cen


cnt = 0
total = 0
while 1:
    for c in range(len(cz_lst)):
        if c==len(cz_lst)-1:
            cy, cx, d = cz_lst[c]
            ncy, ncx, nd = cz_lst[0]
        else:
            cy,cx,d = cz_lst[c]
            ncy,ncx,nd = cz_lst[c+1]

        # print(cy,cx,ncy,ncx)

        esc_per = esc_move(cy, cx, esc_per)
        esc_per,score= check(nd, ncy, ncx, esc_per,cnt+1)
        total+=score
        cnt+=1
        if cnt==k:
            print(total)
            break
    if cnt == k:
        break




'''
5 3 2 3
2 2 1
2 4 1
3 4 1
2 3
2 5
'''




