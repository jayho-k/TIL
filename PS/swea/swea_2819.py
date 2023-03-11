'''


1
1 1 1 1
1 1 1 2
1 1 2 1
1 1 1 1

'''
def dfs(d,y,x,v):

    if d==6:
        store.add(int(v))
        return
    
    for dd in range(4):
        ny = y+dy[dd]
        nx = x+dx[dd]
        if 0<=ny<4 and 0<=nx<4:
            dfs(d+1,ny,nx,v+grid[ny][nx])

for tc in range(1,int(input())+1):
    grid = [list(input().split()) for _ in range(4)]
    dy = [-1,0,1,0]
    dx = [0,1,0,-1]
    store = set()
    visited = [[0]*4 for _ in range(4)]
    for y in range(4):
        for x in range(4):
            dfs(0,y,x,grid[y][x])
    # print(store)
    print(f"#{tc} {len(store)}")
