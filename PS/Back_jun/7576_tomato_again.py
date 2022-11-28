'''

6 4
0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 1

'''
from collections import deque
def bfs(lst):
    
    q = deque(lst)
    dy = [-1,0,1,0]
    dx = [0,1,0,-1]
    mx = 0

    for y,x in lst:
        visited[y][x] = 1 

    while q:
        y,x = q.popleft()

        for d in range(4):
            ny = y + dy[d]
            nx = x + dx[d]

            if 0<=ny<n and 0<=nx<m and not visited[ny][nx] and not grid[ny][nx]:
                visited[ny][nx] = visited[y][x] + 1
                mx = max(mx,visited[ny][nx])
                q.append((ny,nx))

    return mx-1


    
def st(grid):
    tmp = []
    for sy in range(n):
        for sx in range(m):
            if grid[sy][sx] == 1:
                tmp.append((sy,sx))
    return tmp


m,n = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]
visited = [[0]*m for _  in range(n)]


tmp = st(grid)
total = bfs(tmp)

state = True
for y_test in range(n):
    for x_test in range(m):
        if visited[y_test][x_test] == 0 and grid[y_test][x_test] != -1:
            state = False
            break

if state == True:
    if total == -1:
        print(0)
    else:
        print(total)

else:
    print(-1)
