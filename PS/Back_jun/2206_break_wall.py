'''
3차원으로 구현
6 4
0100
1110
1000
0000
0111
0000

0층으로 시작
벽에서 막히면 1층으로 올라감
둘다 ==> 체크는 계속 해줘야함


'''
from pprint import pprint
from collections import deque
import sys

def bfs(y,x,w):

    q = deque([(y,x,w)])
    dy = [0,0,1,-1]
    dx = [1,-1,0,0]
    visited = [[[0]*2 for _ in range(m)] for _ in range(n)]
    visited[y][x][w] = 1
    
    while q:
        y,x,w = q.popleft()

        if y == n-1 and x == m-1:
            return visited[y][x][w]

        for d in range(4):
            ny = y + dy[d]
            nx = x + dx[d]

            if 0<=ny<n and 0<=nx<m:
                # 안막혔을 때
                if grid[ny][nx] == 0 and visited[ny][nx][w] == 0:
                    visited[ny][nx][w] = visited[y][x][w] + 1
                    q.append((ny,nx,w))
                
                # 벽에서 막혔을 때 (visited)
                if grid[ny][nx] == 1 and w == 0:
                    visited[ny][nx][1] = visited[y][x][0] + 1
                    q.append((ny,nx, w+1))
    
    return -1
    

input = sys.stdin.readline


n, m = map(int,input().split())
grid = [list(map(int,list(input().rstrip()))) for _ in range(n)]
ans = bfs(0,0,0)

print(ans)