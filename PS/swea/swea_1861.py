'''
정사각형 방

2
2
1 2
3 4
3
9 3 4
6 1 5
7 8 2

'''
from collections import deque
from pprint import pprint
def bfs(y,x,grid,visited):

    q = deque([(y,x)])
    visited[y][x]=1
    cnt = 1
    st_point = grid[y][x]
    while q:
        y,x = q.popleft()

        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]
            if 0<=ny<n and 0<=nx<n and visited[ny][nx]==0\
                and (grid[y][x]+1==grid[ny][nx] or grid[y][x]-1==grid[ny][nx]):
                visited[ny][nx]=1
                q.append((ny,nx))
                cnt+=1
                st_point=min(st_point,grid[ny][nx])

    return cnt,st_point,visited


dy = [-1,0,1,0]
dx = [0,1,0,-1]
for tc in range(1,int(input())+1):

    n = int(input())
    grid = [list(map(int,input().split())) for _ in range(n)]
    visited = [[0]*n for _ in range(n)]
    mx_cnt = 0
    stp = 0
    for y in range(n):
        for x in range(n):
            if visited[y][x]==0:
                cnt,st_point,visited = bfs(y,x,grid,visited)
                if mx_cnt<cnt:
                    mx_cnt=cnt
                    stp = st_point                 

                elif mx_cnt==cnt:
                    stp=min(stp, st_point)
                
    print(f"#{tc}",stp,mx_cnt)



