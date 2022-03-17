'''

2 1 1
100 100
100 99

'''
from collections import deque
from sys import stdin
from pprint import pprint


def bfs(y,x):
    global never
    q = deque([(y,x)])
    dy = [0,0,1,-1]
    dx = [1,-1,0,0]
    t_lst = []
    sm = 0
    
    while q:
        y,x = q.popleft()

        for d in range(4):
            ny = y + dy[d]
            nx = x + dx[d]
            if 0<=ny<n and 0<=nx<n and (ny,nx) not in visited:
                dif = abs(grid[ny][nx] - grid[y][x])
                if l<=dif<=r:
                    visited.add((ny,nx))
                    q.append((ny,nx))
                    t_lst.append((ny,nx))
                    sm += grid[ny][nx]

                    if len(t_lst) > 1:
                        never = 0

    return t_lst, sm, never

n, l, r = map(int, stdin.readline().split())
grid = [list(map(int, stdin.readline().split())) for _ in range(n)]

cnt = 0
while 1:
    visited = set()
    never = 1
    for y in range(n):
        for x in range(n):
            if (y,x) not in visited:
                t_lst,sm,never = bfs(y,x)
                tn = len(t_lst)
                if tn > 1:
                    num = sm//tn
                    for ty,tx in t_lst:
                        grid[ty][tx] = num

    if never==1:
        break
    cnt += 1

print(cnt)



# from collections import deque
# from pprint import pprint


# def bfs(y,x):
#     global never
#     q = deque([(y,x)])
#     dy = [0,0,1,-1]
#     dx = [1,-1,0,0]
#     t_lst = []
#     sm = 0
    
#     while q:
#         y,x = q.popleft()

#         for d in range(4):
#             ny = y + dy[d]
#             nx = x + dx[d]
#             if 0<=ny<n and 0<=nx<n and visited[ny][nx] == 0:
#                 dif = abs(grid[ny][nx] - grid[y][x])
#                 if l<=dif<=r:
#                     visited[ny][nx] = 1
#                     q.append((ny,nx))
#                     t_lst.append((ny,nx))
#                     sm += grid[ny][nx]

#                     if len(t_lst) > 1:
#                         never = 0

#     return t_lst, sm, never

# n, l, r = map(int, input().split())
# grid = [list(map(int, input().split())) for _ in range(n)]

# cnt = 0
# while 1:
#     visited = [[0]*n for _ in range(n)]
#     never = 1
#     for y in range(n):
#         for x in range(n):
#             if visited[y][x]==0:
#                 t_lst,sm,never = bfs(y,x)
#                 tn = len(t_lst)
#                 if tn > 1:
#                     num = sm//tn
#                     for ty,tx in t_lst:
#                         grid[ty][tx] = num

#     #         print(grid)
#     #         print(visited)
#     #         print(t_lst)
#     # print('*'*30)
#     if never==1:
#         break
#     cnt += 1

# print(cnt)