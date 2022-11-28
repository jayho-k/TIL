'''

3 3 1 1 9
1 2 3
4 0 5
6 7 8
1 3 2 2 4 4 1 1 3

동쪽은 1, 서쪽은 2, 북쪽은 3, 남쪽은 4
'''



n,m,x,y,k = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]
dir_order = list(map(int,input().split()))
dy = [0,0,0,-1,1]
dx = [0,1,-1,0,0]

# dice setting
dice = [0,0,0,0,0,0,0]

# play
for d in dir_order:

    # direction setting
    ny = y+dy[d]
    nx = x+dx[d]
    if 0<=ny<n and 0<=nx<m:
        east,west,south,north,up,down = dice[1],dice[2],dice[3],dice[4],dice[5],dice[6]
        
        # copy num
        if d==1:
            dice[1],dice[2],dice[5],dice[6] = down,up,east,west
        elif d==2:
            dice[1],dice[2],dice[5],dice[6] = up,down,west,east 
        elif d==3:
            dice[3],dice[4],dice[5],dice[6] = up,down,north,south
        elif d==4:
            dice[3],dice[4],dice[5],dice[6] = down,up,south,north
        
        if grid[ny][nx]==0:
            grid[ny][nx] = dice[6]
            dice[6] = 0
        else:
            dice[6] = grid[ny][nx]
            grid[ny][nx] = 0
        y = ny
        x = nx
    print(dice[5])

