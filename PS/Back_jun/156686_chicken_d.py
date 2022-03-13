'''
치킨 배달~~~

bfs ===> 시간초과
stp의 개수가 정해져 있음
완탐 ㄱ
1. 시작 지점 세팅을 어떻게 정해주어야 하는가?
    일단 치킨이 있는 곳을 다 lst에 넣어준다
2. visited를 어떻게 설정을 해주는가?
3. 그것만 되면 visieted의 거리의 합을 구하면 된다.
'''
from itertools import combinations
from sys import stdin
from collections import deque
from pprint import pprint


n, m = map(int, stdin.readline().split())
grid = [list(map(int, stdin.readline().split())) for _ in range(n)]

home = []
chicken = []
for y in range(n):
    for x in range(n):
        if grid[y][x] == 1:
            home.append((y,x))

        if grid[y][x] == 2:
            chicken.append((y,x))


r = []
for c in list(combinations(chicken,m)):
    total = 0
    for hy,hx in home:
        mn = 1e9
        for cy, cx in c:
            d=abs(cy-hy)+abs(cx-hx)
            mn = min(mn,d)
        total+=mn
    r.append(total)

print(min(r))


'''
bfs
하지만 시간 초과가 뜨게 된다.
'''
# def stp(grid):
#     lst = []
#     h_lst = []
#     for y in range(n):
#         for x in range(n):
#             if grid[y][x] == 2:
#                 lst.append((y,x))
#             if grid[y][x] == 1:
#                 h_lst.append((y,x))

#     return lst, h_lst

# def sel(d,m):
#     global mn
#     if d == m:
#         st_p= []
#         for m_i in range(stn):
#             if lst[m_i] ==1:
#                 st_p.append(stp_lst[m_i])

#         t = bfs(st_p)
#         if mn > t:
#             mn = t
#         return

#     for i in range(stn):
#         if lst[i] == 0:
#             lst[i] = 1
#             sel(d+1,m)
#             lst[i] = 0

# def bfs(st_p):
#     visited = [[0]*n for _ in range(n)]
#     for y,x in st_p:
#         visited[y][x] = 1

#     q = deque(st_p)
#     dy = [0,0,1,-1]
#     dx = [1,-1,0,0]

#     while q:
#         y,x = q.popleft()
#         for d in range(4):
#             ny = y + dy[d]
#             nx = x + dx[d]
#             if 0<=ny<n and 0<=nx<n and visited[ny][nx]==0:
#                 visited[ny][nx] = visited[y][x] + 1
#                 q.append((ny,nx))


#     total_d = 0
#     for hy,hx in h_lst:
#         distance = visited[hy][hx]
#         total_d += (distance-1)

#     # pprint(visited)
#     return total_d

# n, m = map(int, stdin.readline().split())
# grid = [list(map(int, stdin.readline().split())) for _ in range(n)]

# stp_lst,h_lst = stp(grid)

# stn = len(stp_lst)
# lst = [0]*stn
# mn = 1e9

# sel(0,m)
# print(mn)