'''

 r,c,m,s,d
'''

def move(fire_balls,grid):
    n_fire_balls = set()
    for y,x,m,s,d in fire_balls:
        ny = (y+(dy[d]*s)%n)%n
        nx = (x+(dx[d]*s)%n)%n
        grid[ny][nx].append((m,s,d))
        n_fire_balls.add((ny,nx))
    return n_fire_balls,grid

def cnt_fire_balls(fire_balls,grid):

    n_fire_balls = []
    for fy,fx in fire_balls:
        cnt = len(grid[fy][fx])
        if cnt>1:
            sm_m = 0
            sm_s = 0
            sm_hall = 0
            sm_jjack = 0
            for m,s,d in grid[fy][fx]:
                sm_m += m
                sm_s += s
                if d%2:
                    sm_hall+=1
                else:
                    sm_jjack+=1

            # div
            div_m = sm_m//5
            div_s = sm_s//cnt
            if div_m < 1:
                continue

            if sm_hall==cnt or sm_jjack==cnt:
                for d in (0,2,4,6):
                    n_fire_balls.append((fy,fx,div_m,div_s,d))

            else:
                for d in (1,3,5,7):
                    n_fire_balls.append((fy,fx,div_m,div_s,d))

        else:
            m,s,d = grid[fy][fx][0]
            n_fire_balls.append((fy,fx,m,s,d))

    grid = [[[] for _ in range(n)] for _ in range(n)]
    return n_fire_balls,grid

def main(fire_balls, grid):
    for _ in range(k):
        n_fire_balls ,n_grid = move(fire_balls,grid)
        fire_balls, grid = cnt_fire_balls(n_fire_balls,n_grid)
    return fire_balls

n,m,k = map(int,input().split())
fire_balls = []
for _ in range(m):
    y,x,m,s,d = map(int,input().split())
    fire_balls.append((y-1,x-1,m,s,d))

dy = [-1,-1,0,1,1,1,0,-1]
dx = [0,1,1,1,0,-1,-1,-1]
grid = [[[] for _ in range(n)] for _ in range(n)]
ans = main(fire_balls,grid)

total = 0
for _,_,ans_m,_,_ in ans:
    total += ans_m
