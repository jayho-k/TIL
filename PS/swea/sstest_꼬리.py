'''
7 2 1
3 2 1 0 0 0 0
4 0 4 0 2 1 4
4 4 4 0 2 0 4
0 0 0 0 3 0 4
0 0 4 4 4 0 4
0 0 4 0 0 0 4
0 0 4 4 4 4 4

7 2 2
3 2 1 0 0 0 0
4 0 4 0 2 1 4
4 4 4 0 2 0 4
0 0 0 0 3 0 4
0 0 4 4 4 0 4
0 0 4 0 0 0 4
0 0 4 4 4 4 4

7 3 28
3 2 1 0 0 0 0
4 0 4 0 2 1 4
4 4 4 0 2 0 4
0 0 0 0 3 4 4
2 1 3 2 0 0 0
2 0 0 2 0 0 0
2 2 2 2 0 0 0

7 3 973
3 2 1 0 0 0 0
4 0 4 0 2 1 4
4 4 4 0 2 0 4
0 0 0 0 3 4 4
2 1 3 2 0 0 0
2 0 0 2 0 0 0
2 2 2 2 0 0 0
'''
from collections import defaultdict, deque
from pprint import pprint
def bfs(y,x,team):
    visited = [[0]*n for _ in range(n)]
    visited[y][x]=1
    teams[team].append((y,x))
    q = deque([(y,x,0)])

    while q:
        y,x,cnt = q.popleft()
        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]
            # 팀원이 있다면
            if 0<=ny<n and 0<=nx<n and visited[ny][nx]==0:                
                if cnt == 0:
                     # 처음이라면 2인경우만
                     # 왜냐하면=> 3(꼬리인 경우가 있을 수 있기 때문)
                    if grid[ny][nx]==2:
                        visited[ny][nx]=1
                        teams[team].append((ny,nx))
                        q.append((ny,nx,cnt+1))

                else:
                    if grid[ny][nx]!=4 and grid[ny][nx]!=0:                
                        visited[ny][nx]=1
                        teams[team].append((ny,nx))
                        q.append((ny,nx,cnt+1))

def find_team():
    team = 0
    for y in range(n):
        for x in range(n):
            if grid[y][x]==1:
                bfs(y,x,team)
                team+=1

def move():
    for i in range(m):
        after_move = []
        
        team = teams[i]
        hy,hx = team[0]
        for d in range(4):
            ny = hy+dy[d]
            nx = hx+dx[d]
            if 0<=ny<n and 0<=nx<n and (grid[ny][nx]==4 or grid[ny][nx]==3):
                after_move.append((ny,nx))
                break
    
        # after_move 넣기
        nxt = team[0] # 첫번째 꺼가 다음이 되버린다.
        grid[nxt[0]][nxt[1]]=4
        for j in range(1,len(team)):
            # head
            after_move.append(nxt)
            nxt = team[j]
            grid[nxt[0]][nxt[1]]=4

        teams[i] = after_move

        # grid초기화
        for a in range(len(after_move)):
            ay,ax = after_move[a]
            if a == 0:
                grid[ay][ax]=1
            elif a == len(after_move)-1:
                grid[ay][ax]=3
            else:
                grid[ay][ax]=2

def get_ball(y,x):
    for t_num in range(m):
        for p_num,val in enumerate(teams[t_num]):
            if (y,x)==val:
                return t_num,p_num+1

def throw_ball():
    d = (round//(n))%4 # 4cycle이 넘어가는 경우
    yx = round%n

    # 동
    if d==0:
        for x in range(n):
            # print(yx,x)
            if grid[yx][x]!=4 and grid[yx][x]!=0:
                return get_ball(yx,x)
    # 북
    elif d==1:
        for y in range(n-1,-1,-1):
            if grid[y][yx]!=4 and grid[y][yx]!=0:
                return get_ball(y,yx)
            
    # 서
    elif d==2:
        yx = n-yx-1
        for x in range(n-1,-1,-1):
            if grid[yx][x]!=4 and grid[yx][x]!=0:
                return get_ball(yx,x)

    # 남
    elif d==3:
        yx = n-yx-1
        for y in range(n):
            if grid[y][yx]!=4 and grid[y][yx]!=0:
                return get_ball(y,yx)
    
    return -1,-1

def winner(t_num):
    teams[t_num].reverse()
    rev = teams[t_num]
    for r in range(len(rev)):
        ay,ax = rev[r]
        if r == 0:
            grid[ay][ax]=1
        elif r == len(rev)-1:
            grid[ay][ax]=3
        else:
            grid[ay][ax]=2

n,m,k = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]
teams = defaultdict(list)
dy = [0,-1,0,1]
dx = [1,0,-1,0]

find_team()

total = 0
# round=0부터 시작
for round in range(k):
    move()
    t_num,p_num = throw_ball()
    if t_num==-1:
        continue
    total += (p_num**2)
    winner(t_num)

print(total)