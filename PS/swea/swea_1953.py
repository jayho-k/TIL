'''

1
5 6 2 1 3
0 0 5 3 6 0
0 0 2 0 2 0
3 3 1 3 7 0
0 0 0 0 0 0
0 0 0 0 0 0

1
5 6 2 2 6      
3 0 0 0 0 3
2 0 0 0 0 6
1 3 1 1 3 1
2 0 2 0 0 2
0 0 4 3 1 1

'''

from collections import deque
def bfs(y,x,l):

    visited = [[0]*m for _ in range(n)]
    q = deque([(y,x,1)])
    visited[y][x]=1
    cnt = 1

    while q:
        y,x,time = q.popleft()
        
        if time>=l:
            return cnt

        for d in tunnel[grid[y][x]]:
            ny = y+dy[d]
            nx = x+dx[d]

            if 0<=ny<n and 0<=nx<m and visited[ny][nx]==0\
            and grid[ny][nx]!=0 and (d+2)%4 in tunnel[grid[ny][nx]]:
                visited[ny][nx]=1
                q.append((ny,nx,time+1))
                cnt+=1
    return cnt

dy = [-1,0,1,0]
dx = [0,1,0,-1]
tunnel = {
    1:{0,1,2,3},
    2:{0,2},
    3:{1,3},
    4:{0,1},
    5:{1,2},
    6:{2,3},
    7:{0,3}
}
for tc in range(1,int(input())+1):
    n,m,r,c,l = map(int,input().split())
    grid = [list(map(int,input().split())) for _ in range(n)]
    cnt = bfs(r,c,l)
    print(f"#{tc} {cnt}")