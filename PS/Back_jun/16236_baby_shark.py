'''
4
4 3 2 1
0 0 0 0
0 0 9 0
1 2 3 4

'''

from collections import deque
from pprint import pprint

def find_shark():
    shy,shx = -1,-1
    fish_grid = [[0]*n for _ in range(n)]
    for y in range(n):
        for x in range(n):
            if grid[y][x]==9:
                shy,shx = y,x
            elif grid[y][x]:
                fish_grid[y][x]=grid[y][x]

    return shy,shx,fish_grid

def bfs(y,x):
    
    q = deque([(0,y,x)])
    visited = [[0]*n for _ in range(n)]
    visited[y][x]=1
    eat_lst = []

    while q:
        cnt,y,x = q.popleft()

        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]

            if 0<=ny<n and 0<=nx<n and visited[ny][nx]==0:
                if shark==fish_grid[ny][nx] or fish_grid[ny][nx]==0:
                    visited[ny][nx]=1
                    q.append((cnt+1,ny,nx))

                elif shark>fish_grid[ny][nx]:
                    visited[ny][nx]=1
                    q.append((cnt+1,ny,nx))
                    eat_lst.append((cnt+1,ny,nx))
    
    if eat_lst:
        eat_lst.sort(key=lambda x : (x[0],x[1],x[2]))
        cnt,ey,ex = eat_lst[0]
        fish_grid[ey][ex] = 0
        return ey,ex,cnt,True

    else:
        return -1,-1,0,False



n = int(input())
grid = [list(map(int,input().split())) for _ in range(n)]
shark = 2
eatten = 0
total = 0
dy = [-1,0,1,0]
dx = [0,1,0,-1]
shy,shx,fish_grid = find_shark()


while True:
    shy,shx,cnt,flag = bfs(shy,shx)
    total+=cnt
    if flag:
        eatten+=1
        
        if shark==eatten:
            shark+=1
            eatten=0
    else:
        break

print(total)



















# # bfs
# from pprint import pprint
# from collections import deque

# def stp():
#     for y in range(n):
#         for x in range(n):
#             if grid[y][x] == 9:
#                 grid[y][x] = 0
#                 return y, x

# def bfs(y,x,shark):
#     q = deque([(y,x)])
#     visited = [[0]*n for _ in range(n)]
#     visited[y][x] = 1
#     d_lst = []

#     dy = [-1,1,0,0]
#     dx = [0,0,-1,1]

#     while q:
#         y,x = q.popleft()
#         for d in range(4):
#             ny = y + dy[d]
#             nx = x + dx[d]
            
#             # 이아기가 통로를 지나갈 수 있니? 물고기를 지나갈 수 있니??
#             if 0<=ny<n and 0<=nx<n and grid[ny][nx] <= shark and visited[ny][nx] == 0:
#                 visited[ny][nx] = visited[y][x] + 1
#                 q.append((ny,nx))

#             # 물고기를 먹을 수 있니?
#             if 0<=ny<n and 0<=nx<n and 0 < grid[ny][nx] < shark:
#                 visited[ny][nx] = visited[y][x] + 1
#                 d =  visited[ny][nx] - 1
#                 d_lst.append((d,ny,nx))
#                 # grid[ny][nx] = 0

#     if d_lst:
#         d_lst.sort()
#         d,y,x = d_lst[0]
#         grid[y][x] = 0
#         return d,y,x

#     else:
#         return 0,ny,nx    


# n = int(input())
# grid = [list(map(int, input().split())) for _ in range(n)]
# sty, stx = stp()

# # stp를 초기화시켜주기
# # while문을 사용한다면 break를 언제 걸어줘야 하나?

# shark = 2
# cnt = 0
# total_d = 0
# while 1:

#     d, y, x = bfs(sty,stx, shark)
#     if d == 0:
#         break
#     sty = y
#     stx = x
#     cnt += 1
#     total_d += d
#     if shark == cnt:
#         shark += 1
#         cnt = 0

# print(total_d)



# '''
# 거리만으로 구하기
# 이렇게 풀면 상어가 본인보다 큰 물고기도 그냥 지나치게 된다.
# 따라서 이 방법은 막힌것이 없을때 사용하는 것이 좋아 보인다.
# '''

# from sys import stdin
# from collections import deque
# from pprint import pprint

# def stp():
#     for y in range(n):
#         for x in range(n):
#             if grid[y][x] == 9:
#                 return y,x


# n = int(stdin.readline())
# grid = [list(map(int,stdin.readline().split())) for _ in range(n)]
# sty,stx = stp()

# mxd = 0
# shark = 2
# cnt = 0

# while 1:
#     d_lst = deque([])
#     mnd = mny = mnx = 1e9

#     for y in range(n):
#         for x in range(n):
#             if 0 < grid[y][x] < shark:
#                 d = abs(sty-y) +abs(stx-x)
#                 d_lst.append((d,y,x))
        
#     if not d_lst:
#         break

#     print(d_lst)
#     for d,y,x in d_lst:
#         if mnd > d:
#             mnd = d
#             mny = y
#             mnx = x

#     mxd += mnd
#     sty, stx = mny, mnx
#     pprint(grid)
#     print('sh',shark)
#     grid[sty][stx] = 0
#     cnt += 1
#     if shark == cnt:
#         shark += 1
#         cnt = 0

# print(mxd)