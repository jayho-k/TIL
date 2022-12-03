'''

5 7
WLLWWWL
LLLWLLL
LWLWLWW
LWLWLLL
WLLWLWW

'''
from collections import deque
from pprint import pprint
import sys


def bfs(y,x):
    
    dist = 0
    # cnt = 1
    q = deque([(y,x)])
    visited_set = set()
    visited_set.add((y,x))

    while q:
        y,x = q.popleft()

        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]

            if 0<=ny<n and 0<=nx<m and visited[ny][nx]==0 and\
                grid[ny][nx]=='L':
                
                visited[ny][nx] = visited[y][x]+1
                dist = visited[ny][nx]
                q.append((ny,nx))

            # if 0<=ny<n and 0<=nx<m and grid[ny][nx]=='L' and\
            #     (ny,nx) not in visited_set:
            #     visited_set.add((ny,nx))
            #     q.append((ny,nx,cnt+1))
            #     # dist = cnt + 1
                
    return dist


input = sys.stdin.readline
n,m = map(int,input().split())
grid = [list(input()) for _ in range(n)]
dy = [0,1,0,-1]
dx = [1,0,-1,0]
ans = 0
for y in range(n):
    for x in range(m):
        if grid[y][x] == 'L':
            visited = [[0]*m for _ in range(n)]
            visited[y][x] = 1
            tear = bfs(y,x)
            ans = max(tear, ans)

print(ans-1)