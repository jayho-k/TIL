'''
5 3
0 0 0 0 0
1 0 0 0 1
0 0 0 0 0
0 1 0 0 0
0 0 0 0 1
2 3
4 4
5 1

확인해야 할 것

check_visited부분의 t에서 시작하는 것을
확인해야한다.

'''
from pprint import pprint
from collections import deque

def find_bc():
    bc_lst = []
    for y in range(n):
        for x in range(n):
            if grid[y][x]:
                bc_lst.append((y,x))
    return bc_lst

def find_basecamp(y,x,t):

    q = deque([(y,x)])
    visited = [[0]*n for _ in range(n)]
    visited[y][x]=t
    bc_conv_dist = []

    while q:
        y,x = q.popleft()
        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]

            # check_visited => 0부터 거리+time
            # visited => 1부터 거리
            if 0<=ny<n and 0<=nx<n and visited[ny][nx]==0 and check_visited[ny][nx]!=-1\
                and check_visited[ny][nx]>visited[y][x]:
                if grid[ny][nx]==1:
                    q.append((ny,nx))
                    visited[ny][nx]=visited[y][x]+1
                    bc_conv_dist.append((visited[y][x],ny,nx))

                elif grid[ny][nx]==0:
                    q.append((ny,nx))
                    visited[ny][nx]=visited[y][x]+1

    bc_conv_dist.sort(key=lambda x : (x[0],x[1],x[2]))
    return bc_conv_dist[0]


def find_conv(y,x,cy,cx,t):

    q = deque([(y,x)])
    visited = [[0]*n for _ in range(n)]
    visited[y][x]=t

    while q:
        y,x = q.popleft()
        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]
            if 0<=ny<n and 0<=nx<n and visited[ny][nx]==0 and check_visited[ny][nx]!=-1\
                and check_visited[ny][nx]>visited[y][x]:
                if (ny,nx)==(cy,cx):
                    return (visited[y][x]+1,ny,nx)
                
                visited[ny][nx] = visited[y][x]+1
                q.append((ny,nx))


n,m = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]
conven = []
for _ in range(m):
    iy,ix = map(int,input().split())
    conven.append((iy-1,ix-1))

bc_lst = find_bc()
per_bc = deque()
dy = [-1,0,0,1]
dx = [0,-1,1,0]
check_visited = [[100000]*n for _ in range(n)]


reach_num = 0
conv_num = len(conven)
ans = 0

time = 0
while 1:
    time+=1

    # 편의점을 찾아가는 길
    while per_bc:
        by,bx,gy,gx,t = per_bc.popleft()
        diff,_,_ = find_conv(by,bx,gy,gx,t)
        ans = max(ans, diff)
        check_visited[gy][gx]=diff
        reach_num+=1
    
    # 모두가 도착했을 경우 break
    if reach_num==conv_num:
        break
    
    # 원하는 편의점과 가장 가까운 BC찾기
    # bc도착 = -1
    if time <= m:
        cy,cx = conven[time-1]
        _,bc_y,bc_x = find_basecamp(cy,cx,time)
        per_bc.append((bc_y,bc_x,cy,cx,time))
        check_visited[bc_y][bc_x]=-1

# pprint(check_visited)
print(ans)