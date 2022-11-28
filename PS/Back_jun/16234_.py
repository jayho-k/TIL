'''
island
=> bfs + for

2 20 50
50 30
30 40

'''
from collections import deque
from pprint import pprint
import sys

input = sys.stdin.readline

def bfs(sy,sx):
    q = deque([(sy,sx)])
    sm = 0
    cnt = 0
    flag = False
    tmp = []
    while q:
        y,x = q.popleft()
        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]

            if 0<=ny<n and 0<=nx<n and (ny,nx) not in visited \
                and l<= abs(grid[ny][nx]-grid[y][x])<=r:
                sm += grid[ny][nx]
                cnt += 1
                visited.add((ny,nx))
                tmp.append((ny,nx))
                q.append((ny,nx))
    if visited:
        flag = True
    if cnt:
        avg = sm//cnt
    else:
        avg = 0

    return avg, flag, tmp

def chnge_num(avg,tmp):
    for vy,vx in tmp:
        grid[vy][vx] = avg

def check(visited):
    for y in range(n):
        for x in range(n):
            if (y,x) not in visited:
                avg,flag,tmp = bfs(y,x)
                chnge_num(avg,tmp)
    return flag

n,l,r = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]
dy = [-1,0,1,0]
dx = [0,1,0,-1]

ans = -1
while True:    
    visited = set()
    flag = check(visited)
    ans += 1
    if flag == False:
        break    

print(ans)





# '''
# island
# => bfs + for

# 2 20 50
# 50 30
# 30 40

# '''
# from collections import deque
# from pprint import pprint
# import sys
# input = sys.stdin.readline

# def bfs(sy,sx,num):
#     global flag
#     q = deque([(sy,sx)])
#     sm = 0
#     cnt = 0
#     flag = False

#     while q:
#         y,x = q.popleft()

#         for d in range(4):
#             ny = y+dy[d]
#             nx = x+dx[d]

            
#             if 0<=ny<n and 0<=nx<n and not visited[ny][nx] \
#                 and l<= abs(grid[ny][nx]-grid[y][x])<=r:
#                 visited[ny][nx] = num
#                 sm += grid[ny][nx]
#                 cnt += 1
#                 q.append((ny,nx))

#     if cnt != 0:
#         avg = sm//cnt
#     else:
#         avg = 0

#     chck = 0
#     for v in visited:
#         chck += sum(v)
#     if not chck:
#         flag = True

#     # print('sm',sm,'cnt',cnt,'avg',avg)
#     return avg, flag


# def check(visited):
#     num = 0
#     for y in range(n):
#         for x in range(n):
#             if not visited[y][x]:
#                 num+=1
#                 bfs(y,x,num)


# n,l,r = map(int,input().split())
# grid = [list(map(int,input().split())) for _ in range(n)]
# dy = [-1,0,1,0]
# dx = [0,1,0,-1]


# ans = -1
# while True:    
#     num = 0
#     visited = [[0]*n for _ in range(n)]
#     for y in range(n):
#         for x in range(n):
#             if not visited[y][x]:
#                 num+=1
#                 avg,flag = bfs(y,x,num)
#                 for vy in range(n):
#                     for vx in range(n):
#                         if visited[vy][vx] == num:
#                             grid[vy][vx] = avg
#     ans += 1
#     # print('visited')
#     # pprint(visited)
#     # pprint('grid')
#     # pprint(grid)
    
#     if flag:
#         break    

# print(ans)
