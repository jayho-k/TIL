'''
6 3 15
0 0 1 0 0 0
0 0 1 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 1 0
0 0 0 1 0 0
6 5
2 2 5 6
5 4 1 6
4 2 3 5

'''
def bfs(y,x,mode):

    q = deque([(y,x)])
    visited = [[0]*n for _ in range(n)]
    visited[y][x]=1

    while q:
        y,x = q.popleft()
        for d in range(4):
            ny = y + dy[d]
            nx = x + dx[d]
            if mode == -1:
                if 0<=ny<n and 0<=nx<n and grid[ny][nx]!= 1 and visited[ny][nx]==0:
                    if st_visited[ny][nx]!=0:
                        # pprint(st_visited)
                        visited[ny][nx]=visited[y][x]+1
                        st_num=st_visited[ny][nx]
                        st_visited[ny][nx]=0
                        # pprint(visited)
                        return ny,nx,st_num,visited[ny][nx]-1
                    else:
                        visited[ny][nx]=visited[y][x]+1
                        q.append((ny,nx))
            else:
                if 0<=ny<n and 0<=nx<n and grid[ny][nx]!= 1 and visited[ny][nx]==0:
                    if gl_visited[ny][nx]==mode:
                        visited[ny][nx]=visited[y][x]+1
                        return ny,nx,gl_visited[ny][nx],visited[ny][nx]-1
                    else:
                        visited[ny][nx]=visited[y][x]+1
                        q.append((ny,nx))

    return

from collections import deque
from pprint import pprint
n,m,oil = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]
dy = [-1,0,1,0]
dx = [0,1,0,-1]
cy,cx = map(int,input().split())
cy -=1
cx -=1

st_visited = [[0]*n for _ in range(n)]
gl_visited = [[0]*n for _ in range(n)]
for i in range(m):
    sy,sx,gy,gx = map(int,input().split())
    st_visited[sy-1][sx-1] = i+1
    gl_visited[gy-1][gx-1] = i+1
pprint(st_visited)
pprint(gl_visited)

for _ in range(m):
    cy,cx,st_num,used_oil = bfs(cy,cx,-1)
    oil-= used_oil
    if oil<0:
        print(-1)
        break
    cy,cx,gl_num,used_oil = bfs(cy,cx,st_num)
    oil-= used_oil
    if oil<0:
        print(-1)
        break
    charge_oil = used_oil*2
    oil+=charge_oil
    print(oil)


