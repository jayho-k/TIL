'''
10
1 1 1 0 0 0 0 1 1 1
1 1 1 1 0 0 0 0 1 1
1 0 1 1 0 0 0 0 1 1
0 0 1 1 1 0 0 0 0 1
0 0 0 1 0 0 0 0 0 1
0 0 0 0 0 0 0 0 0 1
0 0 0 0 0 0 0 0 0 0
0 0 0 0 1 1 0 0 0 0
0 0 0 0 1 1 1 0 0 0
0 0 0 0 0 0 0 0 0 0

'''
def bfs(y,x,original_num):

    q = deque([(y,x)])
    visited[y][x] = original_num
    dy = [0,0,1,-1]
    dx = [1,-1,0,0]

    while q:
        y,x = q.popleft()
        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]
            if 0<=ny<n and 0<=nx<n and visited[ny][nx]==0 and grid[ny][nx]==1:
                visited[ny][nx] = original_num
                q.append((ny,nx))

def check_bfs(y,x,g_visited,island_num,visited):

    q = deque([(y,x)])
    dy = [0,0,1,-1]
    dx = [1,-1,0,0]
    island_num = island_num
    # print(island_num)

    while q:
        y,x = q.popleft()
        # pprint(g_visited)
        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]

            if 0<=ny<n and 0<=nx<n and g_visited[ny][nx]==0 and visited[ny][nx]==0:
                g_visited[ny][nx] = g_visited[y][x] + 1
                q.append((ny,nx))
            
            if 0<=ny<n and 0<=nx<n and g_visited[ny][nx]==0 and visited[ny][nx]!=0 and visited[ny][nx] != island_num:
                return g_visited[y][x]


def sea(grid):
    sea = []
    for y in range(n):
        for x in range(n):
            if grid[y][x] == 1:
                sea.append((y,x))
    return sea


from collections import deque
from pprint import pprint
import sys
input = sys.stdin.readline


n = int(input())
grid = [list(map(int,input().split())) for _ in range(n)]

g_lst = sea(grid)
sn = len(g_lst)
visited = [[0]*n for _ in range(n)]

original_num = 0
for y in range(n):
    for x in range(n):
        if visited[y][x] == 0 and grid[y][x]==1:
            original_num += 1
            bfs(y,x,original_num)

mn = 1e9
for gy,gx in g_lst:
    g_visited = [[0]*n for _ in range(n)]
    island_num=visited[gy][gx]
    s = check_bfs(gy,gx,g_visited,island_num,visited)
    if s == None:
        continue
    mn = min(mn,s)

print(mn)














# def bfs(y,x,visited,grid):

#     q = deque([(y,x)])
#     visited[y][x] = 1

#     dy = [0,0,1,-1]
#     dx = [1,-1,0,0]

#     while q:
#         y,x = q.popleft()

#         for d in range(4):
#             ny = y+dy[d]
#             nx = x+dx[d]
        
#             if 0<=ny<n and 0<=nx<n and visited[ny][nx]==0 and grid[ny][nx]==1:
#                 visited[ny][nx] = 1
#                 q.append((ny,nx))

# def new_grid(grid):
#     n_grid = []
#     for y in range(n):
#         n_grid.append(grid[y][:])

#     return n_grid


# def sea(grid):
#     sea = []
#     for y in range(n):
#         for x in range(n):
#             if grid[y][x] == 0:
#                 sea.append((y,x))
#     return sea



# from itertools import permutations, combinations
# from collections import deque
# from pprint import pprint

# n = int(input())
# grid = [list(map(int,input().split())) for _ in range(n)]

# sea_lst = sea(grid)
# sn = len(sea_lst)
# # print(sea_lst)
# visited = [[0]*n for _ in range(n)]

# original_num = 0
# for y in range(n):
#     for x in range(n):
#         if visited[y][x] == 0 and grid[y][x]:
#             original_num += 1
#             bfs(y,x,visited,grid)


# def check(sea_lst):
#     for i in range(1,sn+1):
#         c_bridge = list(map(list,combinations(sea_lst,i)))
#         n_grid = new_grid(grid)

#         for c_lst in c_bridge:
#             visited1 = [[0]*n for _ in range(n)]
#             for cy,cx in c_lst:
#                 n_grid[cy][cx] = 1        
            
#             after_num = 0
#             for y in range(n):
#                 for x in range(n):
#                     if visited1[y][x] == 0 and n_grid[y][x]:
#                         after_num += 1
#                         bfs(y,x,visited1,n_grid)

#             if after_num-1 == original_num:
#                 return i

# num = check(sea_lst)
# print(num)







