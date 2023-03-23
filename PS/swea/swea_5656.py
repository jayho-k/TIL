'''


1
3 10 10
0 0 0 0 0 0 0 0 0 0
1 0 1 0 1 0 0 0 0 0
1 0 3 0 1 1 0 0 0 1
1 1 1 0 1 2 0 0 0 9
1 1 4 0 1 1 0 0 1 1
1 1 4 1 1 1 2 1 1 1
1 1 5 1 1 1 1 2 1 1
1 1 6 1 1 1 1 1 2 1
1 1 1 1 1 1 1 1 1 5
1 1 7 1 1 1 1 1 1 1

1
2 9 10
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
0 1 0 0 0 0 0 0 0
0 1 0 0 0 0 0 0 0
1 1 0 0 1 0 0 0 0
1 1 0 1 1 1 0 1 0
1 1 0 1 1 1 0 1 0
1 1 1 1 1 1 1 1 0
1 1 3 1 6 1 1 1 1
1 1 1 1 1 1 1 1 1
'''

from itertools import product
from collections import deque
from pprint import pprint

def break_brick(num,y,x):
    
    q = deque([(num,y,x)])
    cnt = 1
    while q:
        num,y,x = q.popleft()
        grid[y][x]=0
        for d in range(4):
            for i in range(1,num):
                ny = y+dy[d]*i
                nx = x+dx[d]*i
                if 0<=ny<w and 0<=nx<h and grid[ny][nx]!=0:
                    q.append((grid[ny][nx],ny,nx))
                    cnt+=1
                    grid[ny][nx]=0
    return cnt

def rebuild():
    n_grid = []
    for y in range(w):
        n_lst, z_lst = [],[]
        for x in range(h):
            if grid[y][x]:
                n_lst.append(grid[y][x])
            else:
                z_lst.append(0)
        n_grid.append(n_lst+z_lst)
    return n_grid

def find_total():
    total_num = 0
    for y in range(h):
        for x in range(w):
            if tmp[y][x]:
                total_num+=1
    return total_num

for tc in range(1,int(input())+1):
    n,w,h = map(int,input().split())
    tmp = [list(map(int,input().split())) for _ in range(h)]
    dy = [-1,0,1,0]
    dx = [0,1,0,-1]
    total_num = find_total()
    mx_total = 0
    for prd in product(range(w),repeat=n):
        total = 0
        grid = list(map(list,map(lambda x : reversed(x), zip(*tmp))))
        for py in prd:
            for px in range(h-1,-1,-1):
                if grid[py][px]!=0:
                    total += break_brick(grid[py][px],py,px)
                    break

            # after rebuilding
            grid = rebuild()
        mx_total = max(mx_total,total)

    print(f"#{tc} {total_num-mx_total}")


    # for prd in product(range(w),repeat=n):
    #     for py in prd:
    #         grid = list(map(list,map(lambda x : reversed(x), zip(*tmp))))
    #         for px in range(h-1,-1,-1):
    #             if grid[py][px]!=0:
    #                 break_brick(grid[py][px],py,px)
    #                 break
    
