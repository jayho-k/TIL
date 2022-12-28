'''
4 2 1
1 1 5 2 2
1 4 7 1 6

r,c,m,s,d

'''

def move(fire_ball):
    n_grid = [[[] for _ in range(N)] for _ in range(N)]
    for fire in fire_ball:
        y,x,m,s,d = fire
        ny = (y+((dy[d])*s)%N)%N
        nx = (x+((dx[d])*s)%N)%N
        n_grid[ny][nx].append((m,s,d))
    return n_grid

def collect_fireball(y,x,grid,cnt):
    sum_m,sum_s,d_1,d_2 = 0,0,0,0
    for i in range(cnt):
        m,s,d = grid[y][x][i]
        sum_m += m
        sum_s += s
        if d%2: d_1+=1
        else: d_2+=1
    nm = sum_m//5
    ns = sum_s//cnt
    return nm,ns,d_1,d_2

def divide_fireball(decision):
    if decision=='Even':
        return (0,2,4,6)

    elif decision=='Odd':
        return (1,3,5,7)

def collect(grid):
    n_fire_ball = set()
    for y in range(N):
        for x in range(N):
            cnt = len(grid[y][x])
            if cnt>=2:
                nm,ns,d_1,d_2 = collect_fireball(y,x,grid,cnt)

                # 질량이 0일 경우
                if nm<=0:
                    continue

                # 홀수
                if d_1 and d_2:
                    new_direction = divide_fireball('Odd')
                
                # 짝
                else:
                    new_direction = divide_fireball('Even')

                for nd in new_direction:
                    n_fire_ball.add((y,x,nm,ns,nd))

            elif cnt==1:
                m,s,d = grid[y][x][0]
                n_fire_ball.add((y,x,m,s,d))

    return n_fire_ball

N,M,K = map(int,input().split())
dy = [-1,-1,0,1,1,1,0,-1]
dx = [0,1,1,1,0,-1,-1,-1]
fire_ball = set()
for _ in range(M):
    r,c,m,s,d = map(int,input().split())
    fire_ball.add((r-1,c-1,m,s,d))

for _ in range(K):
    grid = move(fire_ball)
    fire_ball = collect(grid)

ans=0
for _,_,a,_,_ in fire_ball:
    ans += a

print(ans)












# def move(fire_balls,grid):
#     n_fire_balls = set()
#     for y,x,m,s,d in fire_balls:
#         ny = (y+(dy[d]*s)%n)%n
#         nx = (x+(dx[d]*s)%n)%n
#         grid[ny][nx].append((m,s,d))
#         n_fire_balls.add((ny,nx))
#     return n_fire_balls,grid

# def cnt_fire_balls(fire_balls,grid):

#     n_fire_balls = []
#     for fy,fx in fire_balls:
#         cnt = len(grid[fy][fx])
#         if cnt>1:
#             sm_m = 0
#             sm_s = 0
#             sm_hall = 0
#             sm_jjack = 0
#             for m,s,d in grid[fy][fx]:
#                 sm_m += m
#                 sm_s += s
#                 if d%2:
#                     sm_hall+=1
#                 else:
#                     sm_jjack+=1

#             # div
#             div_m = sm_m//5
#             div_s = sm_s//cnt
#             if div_m < 1:
#                 continue

#             if sm_hall==cnt or sm_jjack==cnt:
#                 for d in (0,2,4,6):
#                     n_fire_balls.append((fy,fx,div_m,div_s,d))

#             else:
#                 for d in (1,3,5,7):
#                     n_fire_balls.append((fy,fx,div_m,div_s,d))

#         else:
#             m,s,d = grid[fy][fx][0]
#             n_fire_balls.append((fy,fx,m,s,d))

#     grid = [[[] for _ in range(n)] for _ in range(n)]
#     return n_fire_balls,grid

# def main(fire_balls, grid):
#     for _ in range(k):
#         n_fire_balls ,n_grid = move(fire_balls,grid)
#         fire_balls, grid = cnt_fire_balls(n_fire_balls,n_grid)
#     return fire_balls

# n,m,k = map(int,input().split())
# fire_balls = []
# for _ in range(m):
#     y,x,m,s,d = map(int,input().split())
#     fire_balls.append((y-1,x-1,m,s,d))

# dy = [-1,-1,0,1,1,1,0,-1]
# dx = [0,1,1,1,0,-1,-1,-1]
# grid = [[[] for _ in range(n)] for _ in range(n)]
# ans = main(fire_balls,grid)

# total = 0
# for _,_,ans_m,_,_ in ans:
#     total += ans_m
