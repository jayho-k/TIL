'''
5 5
1 2 3 4 5
5 4 3 2 1
2 3 4 5 6
6 5 4 3 2
1 2 1 2 1

'''


# 다시 풀기
import sys
def dfs(d,y,x,v):
    global mx

    if d == 3:
        mx = max(mx,v)
        return

    for i in range(4):
        ny = y + dy[i]
        nx = x + dx[i]

        if 0<=ny<n and 0<=nx<m and visited[ny][nx] == 0:

            if d ==1:
                visited[ny][nx] = 1 
                dfs(d+1, y, x, v+grid[ny][nx])
                visited[ny][nx] = 0

            visited[ny][nx] = 1 
            dfs(d+1, ny, nx, v+grid[ny][nx])
            visited[ny][nx] = 0


input = sys.stdin.readline
n,m = map(int, input().split())

grid = [list(map(int,input().split())) for _ in range(n)]
visited = [[0]*m for _ in range(n)]
mx = 0

dy = [0,0,1,-1]
dx = [1,-1,0,0]

for y in range(n):
    for x in range(m):
        if visited[y][x] == 0:
            visited[y][x] = 1
            dfs(0,y,x, grid[y][x])
            visited[y][x] = 0

print(mx)