"""
4 3
1 2 4 4
4 2 2 2
5 2 6 6
5 3 3 1


4 1
1 2 4 4
4 2 2 2
5 2 6 6
5 3 3 1

20 708
2 2 3 3 2 2 3 3 3 1 3 3 3 3 3 2 2 1 1 3 
2 2 3 3 3 1 1 1 3 3 3 1 1 3 3 1 1 2 1 1 
3 3 1 3 3 1 1 1 2 2 3 1 1 2 1 1 3 3 3 3 
3 3 1 2 1 1 1 1 2 2 3 1 2 1 1 2 2 3 3 3 
3 1 1 3 3 3 2 2 2 1 1 1 3 1 3 2 2 3 3 3 
2 1 3 3 2 3 2 2 2 1 1 2 1 1 1 2 2 3 3 1 
3 3 1 1 3 3 3 2 3 3 3 2 2 2 2 3 3 3 3 2 
2 1 1 1 2 2 3 2 2 2 2 2 3 3 3 3 2 1 2 2 
1 1 3 1 1 3 2 2 3 1 1 1 1 2 2 3 3 1 1 3 
3 3 2 1 1 3 2 2 1 1 3 2 3 2 2 2 3 3 1 2 
3 1 2 2 2 3 2 2 2 2 3 1 3 2 2 2 2 3 1 2 
1 1 1 1 2 1 1 2 2 2 3 3 2 3 3 3 3 2 3 2 
1 1 1 2 2 1 1 2 1 1 1 1 2 1 3 1 3 3 2 2 
1 3 1 2 2 1 1 1 3 1 1 2 2 1 3 3 3 2 2 2 
1 3 3 2 2 3 3 3 2 2 3 3 2 1 3 3 2 2 1 2 
1 1 3 1 1 3 2 2 3 3 3 3 2 1 3 3 2 2 3 3 
3 3 3 2 1 3 1 2 2 3 2 2 2 1 1 1 1 1 1 1 
3 3 1 3 3 1 3 2 1 3 3 3 3 1 2 2 1 1 1 2 
3 3 2 3 3 3 3 3 3 3 3 2 3 2 2 1 1 2 2 1 
3 1 1 3 3 3 3 3 3 3 2 2 2 2 2 2 1 1 1 1 


4836
"""
from collections import deque
from pprint import pprint

def move(y,x,d,di):

    # move
    ny = y+dy[d]
    nx = x+dx[d]

    # out of grid
    if ny<0 or ny>=n or nx<0 or nx>=n:
        d = (d+2)%4
        ny = y+dy[d]
        nx = x+dx[d]

    # change_dice
    chage_dice(d)
    n_di = dice[1]
    g = grid[ny][nx]


    # compare
    if n_di > g:
        d = (d+1+4)%4

    elif n_di < g:
        d = (d-1+4)%4
    
    return ny,nx,d,n_di

def bfs(y,x,num):
    
    cnt = 1
    q = deque([(y,x)])
    visited[y][x] = 1
    num_grid[y][x] = num
    g = grid[y][x]
    while q:
        y,x = q.popleft()

        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]

            if 0<=ny<n and 0<=nx<n and visited[ny][nx]==0 and grid[ny][nx]==g:
                cnt+=1
                q.append((ny,nx))
                visited[ny][nx] = 1
                num_grid[ny][nx] = num

    return cnt

def chage_dice(d):
    
    # 북0 동1 남2 서3
    # 상0 하1 북2 동3 남4 서5
    # 북동남서 상하

    if d==0:
        b=dice[d+2]
        u=dice[d+4]
        nth=dice[0]
        sth=dice[1]
        dice[1],dice[0],dice[d+2],dice[d+4]=b,u,nth,sth

    elif d==1:
        b=dice[d+2]
        u=dice[d+4]
        est=dice[0]
        wst=dice[1]
        dice[1],dice[0],dice[d+2],dice[d+4]=b,u,est,wst

    elif d==2:
        b=dice[d+2]
        u=dice[d]
        nth=dice[1]
        sth=dice[0]
        dice[1],dice[0],dice[d+2],dice[d]=b,u,sth,nth

    else:
        b=dice[d+2]
        u=dice[d]
        est=dice[1]
        wst=dice[0]
        dice[1],dice[0],dice[d+2],dice[d]=b,u,wst,est

def setting():
    num = 1
    dic = {}
    for y in range(n):
        for x in range(n): 
            if visited[y][x]==0:
                cnt = bfs(y,x,num)
                dic[num]=cnt
                num+=1
    return dic


n,m = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]
visited = [[0]*n for _ in range(n)]
num_grid = [[0]*n for _ in range(n)]

dice = {
    # 상 하 북 동 남 서
    0:1,
    1:6,
    2:5,
    3:3,
    4:2,
    5:4
}

# setting
y,x,d,di = 0,0,1,6

# 북동남서
dy = [-1,0,1,0]
dx = [0,1,0,-1]
total = 0

num_dic = setting()
for _ in range(m):

    y,x,d,di = move(y,x,d,di)
    cnt = num_dic[num_grid[y][x]]
    total += (grid[y][x]*cnt)

print(total)