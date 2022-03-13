from pprint import pprint
from collections import deque

def stp():
    for y in range(n):
        for x in range(n):
            if grid[y][x] == 9:
                grid[y][x] = 0
                return y, x

def bfs(y,x,shark):
    q = deque([(y,x)])
    visited = [[0]*n for _ in range(n)]
    visited[y][x] = 1
    d_lst = []
    # 북 서 남 동
    dy = [-1,1,0,0]
    dx = [0,0,-1,1]

    while q:
        y,x = q.popleft()
        for d in range(4):
            ny = y + dy[d]
            nx = x + dx[d]
            if 0<=ny<n and 0<=nx<n and grid[ny][nx] <= shark and visited[ny][nx] == 0:
                visited[ny][nx] = visited[y][x] + 1
                q.append((ny,nx))

            if 0<=ny<n and 0<=nx<n and 0 < grid[ny][nx] < shark:
                visited[ny][nx] = visited[y][x] + 1
                d =  visited[ny][nx] - 1
                d_lst.append((d,ny,nx))
                # grid[ny][nx] = 0

    if d_lst:
        d_lst.sort()
        d,y,x = d_lst[0]
        grid[y][x] = 0
        return d,y,x

    else:
        return 0,ny,nx    


n = int(input())
grid = [list(map(int, input().split())) for _ in range(n)]
sty, stx = stp()

# stp를 초기화시켜주기
# while문을 사용한다면 break를 언제 걸어줘야 하나?

shark = 2
cnt = 0
total_d = 0
while 1:

    d, y, x = bfs(sty,stx, shark)
    if d == 0:
        break
    sty = y
    stx = x
    cnt += 1
    total_d += d
    if shark == cnt:
        shark += 1
        cnt = 0

print(total_d)

