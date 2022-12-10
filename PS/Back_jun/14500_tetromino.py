'''
5 5
1 2 3 4 5
5 4 3 2 1
2 3 4 5 6
6 5 4 3 2
1 2 1 2 1

'''

from pprint import pprint
import sys

def dfs(d,y,x,total):
    global ans

    if d == 3:
        ans = max(ans,total)
        return

    for i in range(4):
        ny = y+dy[i]
        nx = x+dx[i]
        if 0<=ny<n and 0<=nx<m and visited[ny][nx]==0:

            if d == 1:
                # depth가 1로 들어가고 난 뒤 부터 2갈래로 나뉘어 간다
                visited[ny][nx]=1
                dfs(d+1,y,x,total+grid[ny][nx])
                visited[ny][nx]=0

            visited[ny][nx]=1
            dfs(d+1,ny,nx,total+grid[ny][nx])
            visited[ny][nx]=0

input = sys.stdin.readline
n,m = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]
dy = [-1,0,1,0]
dx = [0,1,0,-1]
ans = 0
visited = [[0]*m for _ in range(n)]

for y in range(n):
    for x in range(m):
        # visited = [[0]*m for _ in range(n)]
        visited[y][x]=1
        dfs(0,y,x,grid[y][x])
        visited[y][x]=0
        # point : 이렇게 함으로써 visited를 계속해서 만들 필요가 없어진다.
        # 이렇게 하지 않으면 시간초과가 나게됨

print(ans)

















# def dfs(d,y,x,v):
#     global mx

#     if d == 3:
#         mx = max(mx,v)

#         return

#     for i in range(4):
#         ny = y + dy[i]
#         nx = x + dx[i]

#         if 0<=ny<n and 0<=nx<m and visited[ny][nx] ==0:

#             if d == 1:
#                 visited[ny][nx] = 1
#                 dfs(d+1,y,x,v+grid[ny][nx])
#                 visited[ny][nx] = 1

#             visited[ny][nx] = 1
#             dfs(d+1,ny,nx,v+grid[ny][nx])
#             visited[ny][nx] = 0

    

# n,m = map(int,input().split())
# grid = [list(map(int,input().split())) for _ in range(n)]

# dy = [0,0,-1,1]
# dx = [1,-1,0,0]
# visited = [[0]*m for _ in range(n)]
# mx = 0
# for y in range(n):
#     for x in range(m):
#         if visited[y][x] == 0:
#             visited[y][x] = 1
#             dfs(0,y,x,grid[y][x])
#             visited[y][x] = 0

# print(mx)