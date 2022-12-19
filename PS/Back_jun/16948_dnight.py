'''
7
6 6 0 1

y
(r-2, c-1),
(r-2, c+1), 
(r, c-2), 
(r, c+2), 
(r+2, c-1), 
(r+2, c+1)
'''

def bfs(y,x,gy,gx):

    grid[y][x]=1
    q = deque([(y,x)])

    while q:
        y,x = q.popleft()
        if y==gy and x==gx:
            return grid[gy][gx]

        for d in range(6):
            ny = y+dy[d]
            nx = x+dx[d]
            if 0<=ny<n and 0<=nx<n and not grid[ny][nx]:
                grid[ny][nx] = grid[y][x]+1
                q.append((ny,nx))

    return -1

from collections import deque
n = int(input())
grid = [[0]*n for _ in range(n)]
y1,x1,y2,x2 = map(int,input().split())
dy = [-2,-2,0,0,2,2]
dx = [-1,1,-2,2,-1,1]
ans = bfs(y1,x1,y2,x2)
if ans==-1:
    print(-1)
else:
    print(ans-1)