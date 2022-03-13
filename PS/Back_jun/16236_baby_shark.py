'''
1. 처음 상어의 크기: 2
2. 물고기가 더 크면 먹을수 있음
3. 물고기보다 작으면 지나갈 수 없음
4. 크기 =2 ==> 2마리먹으면 3으로 진화

이동방법
1. 물고기 한마리 => 바로 먹으러 감
2. 물고기 > 1   ==> 가까운거 부터 먹음
3. 위 왼쪽

상어 : 


1. 물고기가 없으면 0
'''
from sys import stdin
from collections import deque
from pprint import pprint

def stp():
    for y in range(n):
        for x in range(n):
            if grid[y][x] == 9:
                return y,x


n = int(stdin.readline())
grid = [list(map(int,stdin.readline().split())) for _ in range(n)]
sty,stx = stp()

mxd = 0
shark = 2
cnt = 0

while 1:
    d_lst = deque([])
    mnd = mny = mnx = 1e9

    for y in range(n):
        for x in range(n):
            if 0 < grid[y][x] < shark:
                d = abs(sty-y) +abs(stx-x)
                d_lst.append((d,y,x))
        
    if not d_lst:
        break

    print(d_lst)
    for d,y,x in d_lst:
        if mnd > d:
            mnd = d
            mny = y
            mnx = x

    mxd += mnd
    sty, stx = mny, mnx
    pprint(grid)
    print('sh',shark)
    grid[sty][stx] = 0
    cnt += 1
    if shark == cnt:
        shark += 1
        cnt = 0

print(mxd)






























# from pprint import pprint
# from collections import deque
# def stp(grid):
#     for y in range(n):
#         for x in range(n):
#             if grid[y][x] == 9:
#                 grid[y][x] = 0
#                 return y, x, grid


# def bfs(y,x,shark, n_grid):
#     q = deque([(y,x)])
#     n_grid[y,x] = 10

#     dy = [-1,0,1,0]
#     dx = [0,-1,0,1]

#     while q:
#         y,x = q.popleft()
        
#         for d in range(4):
#             ny = y + dy[d]
#             nx = x + dx[d]

#             if 0<=ny<n and 0<=nx<n and n_grid[ny][nx] == 0 :
#                 n_grid[ny][nx] = n_grid[y][x] + 10
#                 q.append((ny,nx))

#             if 0<=ny<n and 0<=nx<n and n_grid[ny][nx] < shark:
#                 n_grid[ny][nx] = n_grid[y][x] + 10
#                 print(n_grid)
#                 return ny,nx,n_grid[ny][nx]



# n = int(input())
# grid = [list(map(int,input().split())) for _ in range(n)]


# sty, stx, n_grid = stp(grid)
# tt = 0
# shark =2
# eat = 0
# sy = sty
# sx = stx
# # 문제점 : 스타트 포인트 부분이 지금 꼬였음 이것만 해결 해주면 가능할 듯
# # 즉 먹은 위치, 예전 초기위치는 0이 되어야하고 먹은 위치는 10이 되어야 한다.

# # while 1:
# #     sty,stx,t = bfs(sy,sx,shark,n_grid)
# #     eat += 1
# #     if shark == eat:
# #         eat = 0
# #         shark += 1
# #     tt += (t-10)
    
