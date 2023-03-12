'''
2
4                
9 8 9 8
4 6 9 4
8 7 7 8
4 5 3 5
5                
8 2 9 6 6
1 9 3 3 4
8 2 3 3 6
4 3 4 4 9
7 4 6 3 5

'''
from pprint import pprint
def dfs(y,x,gy,gx,d):
    global mx

    if d==3 and gy==y and gx==x:
        mx = max(mx,len(store))
        return

    ny = y+dy[d]
    nx = x+dx[d]

    # 직진하는 경우
    if 0<=ny<n and 0<=nx<n and grid[ny][nx] not in store:
        store.add(grid[ny][nx])
        dfs(ny,nx,gy,gx,d)
        store.remove(grid[ny][nx])

        # 꺽는 경우
        if d<3:
            store.add(grid[ny][nx])
            dfs(ny,nx,gy,gx,d+1)
            store.remove(grid[ny][nx])


for tc in range(1,int(input())+1):
    n = int(input())
    grid = [list(map(int,input().split())) for _ in range(n)]
    dy = [1,1,-1,-1]
    dx = [1,-1,-1,1]
    mx = 0

    for y in range(n):
        for x in range(n):
            store = set()
            dfs(y,x,y,x,0)
    
    if mx==0:
        print(f"#{tc} {-1}")

    else:
        print(f"#{tc} {mx}")

