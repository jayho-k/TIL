'''
3 3
101
010
101

4 5
11001
00111
01010
10101

3 3
000
010
000

2 5
00000
10000

'''
def bfs(y,x):

    q = deque([(y,x)])
    visited.add((y,x))
    cnt = 0

    while q:
        y,x = q.popleft()
        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]
            if 0<=ny<n and 0<=nx<m and grid[ny][nx]==0 and (ny,nx) not in visited:
                cnt += 1
                visited.add((ny,nx))
                q.append((ny,nx))

    return cnt

from collections import deque
n,m = map(int,input().split())
grid = [list(map(int,list(input()))) for _ in range(n)]
new = [[0]*m for _ in range(n)]
dy = [-1,0,1,0]
dx = [0,1,0,-1]
wall_lst = []
zero_grid = [[0]*m for _ in range(n)]

group = 0
for y in range(n):
    for x in range(m):

        # 벽일때 저장
        if grid[y][x] == 1:
            wall_lst.append((y,x))

        # 벽이 아니고 내가 방문을 하지 않았을 경우
        elif grid[y][x]==0 and zero_grid[y][x]==0:
            visited = set()
            group += 1
            cnt = bfs(y,x)

            # 방문한 부분을 cnt값으로 바꿔준다
            for vy,vx in visited:
                zero_grid[vy][vx] = (cnt+1,group)

for wy,wx in wall_lst:

    tmp_group = set()
    for d in range(4):
        nwy = wy+dy[d]
        nwx = wx+dx[d]
        if 0<=nwy<n and 0<=nwx<m and zero_grid[nwy][nwx]!=0 \
            and zero_grid[nwy][nwx][1] not in tmp_group:
            tmp_group.add(zero_grid[nwy][nwx][1])
            grid[wy][wx] += zero_grid[nwy][nwx][0]

    grid[wy][wx]%=10


for n in grid:
    print(''.join(map(str,n)))

