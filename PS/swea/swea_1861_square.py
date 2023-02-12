'''

기초 섬문제

'''
from collections import deque
def bfs(y,x,grid,visited):
    dy = [-1,0,1,0]
    dx = [0,1,0,-1]
    cnt = 1
    q = deque([(y,x)])
    visited[y][x]=1
    mn = grid[y][x]
    while q:
        y,x = q.popleft()
        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]
            if 0<=ny<n and 0<=nx<n and visited[ny][nx]==0\
                and (grid[ny][nx]==grid[y][x]+1 or grid[ny][nx]==grid[y][x]-1):
                q.append((ny,nx))
                visited[ny][nx]=1
                mn = min(mn,grid[ny][nx])
                cnt+=1
    return cnt,visited,mn

for tc in range(1,int(input())+1):
    n = int(input())
    grid = [list(map(int,input().split())) for _ in range(n)]
    visited = [[0]*n for _ in range(n)]
    tmp_lst = []
    for y in range(n):
        for x in range(n):
            if visited[y][x]==0:
                cnt,visited,mn = bfs(y,x,grid,visited)
                tmp_lst.append((mn,cnt))
    tmp_lst.sort(key=lambda x : (-x[1],x[0]))
    st,mx = tmp_lst[0]
    print(f"#{tc}",st,mx)