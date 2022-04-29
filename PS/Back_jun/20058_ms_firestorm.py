'''
90도 돌리기

3 1
1 2 3 4 5 6 7 8
8 7 6 5 4 3 2 1
1 2 3 4 5 6 7 8
8 7 6 5 4 3 2 1
1 2 3 4 5 6 7 8
8 7 6 5 4 3 2 1
1 2 3 4 5 6 7 8
8 7 6 5 4 3 2 1
1

1 2 3 4
5 6 7 8
9 10 11 12
13 14 15 16

'''
def bfs(sy,sx):

    q = deque([(sy,sx)])
    visited[sy][sx] = 1
    dy = [0,0,1,-1]
    dx = [1,-1,0,0]
    
    i_cnt = 1

    while q:
        y,x  = q.popleft()
        
        for d in range(4):
            ny = y + dy[d]
            nx = x + dx[d]
            if 0<=ny<n and 0<=nx<n and visited[ny][nx]==0 and grid[ny][nx] != 0:
                visited[ny][nx] = 1
                q.append((ny,nx))
                i_cnt += 1

    # pprint(visited)
    return i_cnt


from pprint import pprint
from collections import deque

N,Q = map(int,input().split())
n = 2**N
grid = [list(map(int,input().split())) for _ in range(n)]
L = list(map(int,input().split()))

dy = [0,0,1,-1]
dx = [1,-1,0,0]

for q in range(Q):
    l = L[q]
    m = 2**l

    # rotation
    r_grid = [[0]*n for _ in range(n)]
    for y in range(0,n,m):
        for x in range(0,n,m):
            for y1 in range(m):
                for x1 in range(m):
                    r_grid[y+x1][x+m-1-y1] = grid[y+y1][x+x1]

    #chech arr
    chck = [[0]*n for _ in range(n)]

    # not connected
    for y in range(n):
        for x in range(n):
            if r_grid[y][x] <= 0:
                continue

            cnt = 0
            for d in range(4):
                ny = y+dy[d]
                nx = x+dx[d]
                
                if 0<=ny<n and 0<=nx<n and r_grid[ny][nx] > 0:
                    cnt +=1

            # chck
            if cnt<=2:
                chck[y][x] = 1

    for yy in range(n):
        for xx in range(n):
            if chck[yy][xx] == 1:
                r_grid[yy][xx] -= 1

    #initialization
    grid = r_grid

# sum
total = 0
for g in grid:
    total += sum(g)

# island
mx = 0
visited = [[0]*n for _ in range(n)]
for y in range(n):
    for x in range(n):
        if visited[y][x] == 0 and grid[y][x] != 0:
            i_cnt = bfs(y,x)    
            mx = max(mx,i_cnt)

print(total)
print(mx)
