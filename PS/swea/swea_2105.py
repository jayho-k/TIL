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


#1 6
#2 -1
#3 4
#4 4
#5 8
#6 6
#7 14
#8 12
#9 18
#10 30
'''
from pprint import pprint
def dfs(y,x,visited,gy,gx,cnt):
    global mx
    if gy==y and gx==x and cnt!=0:
        mx = max(mx,len(store))
        return

    for d in range(4):
        ny = y+dy[d]
        nx = x+dx[d]
        if 0<=ny<n and 0<=nx<n and visited[ny][nx]==0 and grid[ny][nx] not in store:
            visited[ny][nx]=1
            store.add(grid[ny][nx])
            dfs(ny,nx,visited,gy,gx,cnt+1)
            store.remove(grid[ny][nx])
            visited[ny][nx]=0


for tc in range(1,int(input())+1):
    n = int(input())
    grid = [list(map(int,input().split())) for _ in range(n)]
    dy = [-1,1,1,-1]
    dx = [1,1,-1,-1]
    mx = 0
    for y in range(n):
        for x in range(n):
            store = set()
            visited = [[0]*n for _ in range(n)]
            dfs(y,x,visited,y,x,0)
    
    if mx==0 or mx==2:
        print(f"#{tc} {-1}")

    else:
        print(f"#{tc} {mx}")




