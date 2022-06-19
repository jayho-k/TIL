'''
5
RRRBB
GGBBB
BBBRR
BBBRR
RRRRR

'''
def bfs1(y,x,num):
    q = deque([(y,x)])
    visited[y][x] = 1
    color = grid[y][x]
    
    dy = [0,0,1,-1]
    dx = [1,-1,0,0]

    while q:
        y,x = q.popleft()
        
        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]

            if 0<=ny<n and 0<=nx<n and visited[ny][nx]==0 and grid[ny][nx]==color:
                # pprint(visited)
                visited[ny][nx] = num
                q.append((ny,nx))

def bfs2(y,x):
    q = deque([(y,x)])
    visited[y][x] = 1
    color = grid[y][x]
    
    dy = [0,0,1,-1]
    dx = [1,-1,0,0]

    while q:
        y,x = q.popleft()
        
        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]

            if 0<=ny<n and 0<=nx<n and visited[ny][nx]==0 and grid[ny][nx]==color:
                # pprint(visited)
                visited[ny][nx] = num
                q.append((ny,nx))


from pprint import pprint
from collections import deque
n = int(input())
grid = [list(input()) for _ in range(n)]
visited = [[0]*n for _ in range(n)]

num = 1
for y in range(n):
    for x in range(n):
        if visited[y][x] == 0:
            bfs1(y,x,num)
            num += 1
            print(1)

pprint(visited)
