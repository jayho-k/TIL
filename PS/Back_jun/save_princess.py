'''
방법
1. 2가지로 나눈다
    1) 공주로 바로 가는 방법
    그냥 bfs로 돌리면 된다. tp
    1-2) 공주한테 바로 못갈경우
    tp = 1e9

    2) 검을 획득하고 가는 방법
    검을 획득하고 나서 바로 공주(n,m)과 검의 거리를 측정하고
    그 위치까지의 거리와 더한다 = ts
    2-2) 검을 획득하지 못할 경우
    ts = 1e9

2. 비교만 해주면 된다
    
6 6 16
0 0 0 0 1 1
0 0 0 0 0 2
1 1 1 0 1 0
0 0 0 0 0 0
0 1 1 1 1 1
0 0 0 0 0 0
'''
from pprint import pprint
from collections import deque

def bfs(y,x,status):
    visited = [[0]*(m+1) for _ in range(n+1)]
    q = deque([(y,x)])
    visited[y][x] = 1

    dy = [0,0,1,-1]
    dx = [1,-1,0,0]

    while q:
        y,x = q.popleft()

        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]

            # 공주에게 직접가는 방법
            if 1<=ny<n+1 and 1<=nx<m+1 and grid[ny][nx]!=1 and visited[ny][nx] == 0 and status == 1:
                if grid[ny][nx] == -1:
                    visited[ny][nx] = visited[y][x] + 1

                    return visited[ny][nx]-1

                visited[ny][nx] = visited[y][x] + 1
                q.append((ny,nx))

            # 소드를 들고 가는 방법
            if 1<=ny<n+1 and 1<=nx<m+1 and grid[ny][nx]!=1 and visited[ny][nx] == 0 and status == 2:
                if grid[ny][nx] == 2:
                    visited[ny][nx] = visited[y][x] + 1
                    StoP = abs(ny-n)+abs(nx-m)

                    return visited[ny][nx] + StoP -1
                    
                visited[ny][nx] = visited[y][x] + 1
                q.append((ny,nx))

    return 1e9

n,m,limited = map(int,input().split())
grid = [[1]*(m+1)]+[[1]+list(map(int, input().split())) for _ in range(n)]
grid[n][m] = -1

mnt = 1e9
for i in range(1,3):
    t = bfs(1,1,i)
    if mnt > t:
        mnt = t

if mnt > limited:
    print('Fail')
else:
    print(mnt)