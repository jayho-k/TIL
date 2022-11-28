'''
5 5
1 2 3 4 5
5 4 3 2 1
2 3 4 5 6
6 5 4 3 2
1 2 1 2 1

'''

tmp = 0

def dfs(y,x,deep,v):
    global mx
    if deep == 3:
        mx = max(mx,v)
        return

    for d in range(4):
        ny=y+dy[d]
        nx=x+dx[d]
        # if 0<=ny<n and 0<=nx<m and (ny,nx) not in visited:
        #     visited.add((ny,nx))
        if 0<=ny<n and 0<=nx<m and visited[ny][nx] == 0:
            # 이유 : 하나 들어가고 나서부터 경로가 나뉘기 때문
            if deep == 1:
                visited[ny][nx] = 1
                dfs(y,x,deep+1,v+grid[ny][nx])
                visited[ny][nx] = 0

            visited[ny][nx] = 1
            dfs(ny,nx,deep+1,v+grid[ny][nx])
            visited[ny][nx] = 0


from pprint import pprint
import sys
input = sys.stdin.readline

mx = 0
n,m = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]
dy = [-1,0,1,0]
dx = [0,1,0,-1]


visited = [[0]*m for _ in range(n)]

for y in range(n):
    for x in range(m):
        visited[y][x] = 1
        dfs(y,x,0,grid[y][x])
        visited[y][x] = 0

print(mx)
