'''
5
RRRBB
GGBBB
BBBRR
BBBRR
RRRRR
 
'''
def new_grid(grid):
    n_grid= [[0]*n for _ in range(n)]
    for y in range(n):
        for x in range(n):
            if grid[y][x] == 'R':
                n_grid[y][x] = 'G'

            else:
                n_grid[y][x] = grid[y][x]
    
    return n_grid

def bfs(y,x,num, visited,grid):
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
                visited[ny][nx] = num
                q.append((ny,nx))

from pprint import pprint
from collections import deque
n = int(input())
grid = [list(input()) for _ in range(n)]
visited1 = [[0]*n for _ in range(n)]
visited2 = [[0]*n for _ in range(n)]

num1 = 1
num2 = 1
n_grid = new_grid(grid)


for state in range(1,3):
    if state == 1:
        for y in range(n):
            for x in range(n):
                if visited1[y][x] == 0:
                    bfs(y,x,num1,visited1,grid)
                    num1 += 1

    else:
        for y in range(n):
            for x in range(n):
                if visited2[y][x] == 0:
                    bfs(y,x,num2,visited2,n_grid)
                    num2 += 1

print(num1-1,num2-1)