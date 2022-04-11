'''
6 4 1
0100
1110
1000
0000
0111
0000

'''

from collections import deque
import sys
def bfs(y,x,w,dim):

    q = deque()
    q.append((0,0,0))

    while q:
        y,x,w = q.popleft()
        if y == n-1 and x == m-1:
            return visited[y][x][w]

        check = visited[y][x][w] + 1
        
        for d in range(4):
            ny = y + dy[d]
            nx = x + dx[d]

            if 0<=ny<n and 0<=nx<m and visited[ny][nx][w] == 0:

                if grid[ny][nx] == 1 and w < dim:
                    visited[ny][nx][w+1] = check
                    q.append((ny,nx,w+1))

                elif grid[ny][nx] == 0:
                    visited[ny][nx][w] = check
                    q.append((ny,nx,w))

    return -1

input = sys.stdin.readline
n,m,dim = map(int,input().split())
grid = [list(map(int,list(input().rstrip()))) for _ in range(n)]
visited = [[[0]*(dim+1) for _ in range(m)] for _ in range(n)]

dy = (0,0,1,-1)
dx = (1,-1,0,0)    

# 방문표시
visited[0][0] = [1]*(dim+1)
print(bfs(0,0,0,dim))