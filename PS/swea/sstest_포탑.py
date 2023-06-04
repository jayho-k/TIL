'''
4 4 1
0 1 4 4
8 0 10 13
8 0 11 26
0 0 0 0

4 4 1
0 1 4 4
8 0 10 13
8 0 26 26
0 0 0 0

4 4 3
6 8 0 1
0 0 0 0
0 0 0 0
0 0 8 0

5 10 704
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 2186
0 0 0 0 4346 0 0 0 0 0
0 0 0 0 3889 3148 1500 0 0 0
0 3440 0 0 17 0 0 0 0 0
'''

from pprint import pprint
from collections import deque

def make_attack_lst():
    # 공격, 최근, y+x, x, (y,x)
    attack_lst = []
    for y in range(n):
        for x in range(m):
            if attack_grid[y][x]!=0:
                attack_lst.append((attack_grid[y][x],time_dict[(y,x)], y+x, x, (y,x)))

    attack_lst.sort(key=lambda x : (x[0],-x[1],-x[2],-x[3]))
    
    return attack_lst


def make_time_dict():

    time_dict = {}
    for y in range(n):
        for x in range(m):
            time_dict[(y,x)] = 0

    return time_dict

def find_attack(attack):

    y,x = attack[4]
    attack_grid[y][x] += (n+m)

    return (attack_grid[y][x],attack[1],attack[2],attack[3],attack[4])

def back_to_start(visited,sy,sx,gy,gx):

    while True:
        y,x = visited[gy][gx]
        if (y,x) == (sy,sx):
            break

        related_lst.add((y,x))
        gy,gx = y,x

def razer(attack_loc, defend_loc):
    sy,sx = attack_loc
    gy,gx = defend_loc
    visited = [[0]*m for _ in range(n)]
    visited[sy][sx] = (-1,-1)
    q = deque([(sy,sx)])

    while q:
        y,x = q.popleft()
        for d in range(4):
            ny = (y+dy[d]+n)%n
            nx = (x+dx[d]+m)%m

            if visited[ny][nx]==0 and attack_grid[ny][nx]!=0:

                # 레이저를 쏠 수 있다면
                if (ny,nx)==(gy,gx):
                    visited[ny][nx] = (y,x)

                    back_to_start(visited,sy,sx,gy,gx)

                    # 공격피해 => 피해 포탑 , 이동 포탑
                    for ry,rx in related_lst:
                        if (ry,rx)==(gy,gx):
                            attack_grid[ry][rx]-=attack_grid[sy][sx]

                        elif (ry,rx)==(sy,sx):
                            continue

                        else:
                            attack_grid[ry][rx]-=attack_grid[sy][sx]//2

                    return True
                
                q.append((ny,nx))
                visited[ny][nx] = (y,x)


    return False

def bomb(attack_loc,defend_loc):
    # 1.피해 , 2. 8방향 3. 공격자는 피해없음
    sy,sx = attack_loc
    gy,gx = defend_loc
    attack_grid[gy][gx]-= attack_grid[sy][sx]

    for d in range(8):
        ny = (gy+b_dy[d]+n)%n
        nx = (gx+b_dx[d]+m)%m
        if (ny,nx) != (sy,sx):
            related_lst.add((ny,nx))
            attack_grid[ny][nx]-=attack_grid[sy][sx]//2


def attack_to_defend(attack_loc,defend_loc):

    if not razer(attack_loc,defend_loc):
        bomb(attack_loc,defend_loc)
        

def find_break():
    cnt = 0
    for y in range(n):
        for x in range(m):
            if attack_grid[y][x]<=0:
                attack_grid[y][x]=0
            else:
                cnt+=1
    return cnt

def fix():
    for y in range(n):
        for x in range(m):
            if attack_grid[y][x]!=0 and (y,x) not in related_lst:
                attack_grid[y][x]+=1

def find_result():
    mx = 0
    for y in range(n):
        for x in range(m):
            mx = max(mx,attack_grid[y][x])
    return mx

n,m,k = map(int,input().split())
attack_grid = [list(map(int,input().split())) for _ in range(n)]

# time, attack_lst setting
time_dict = make_time_dict()
dy = [0,1,0,-1]
dx = [1,0,-1,0]
b_dy = [1,1,0,-1,-1,-1,0,1]
b_dx = [0,1,1,1,0,-1,-1,-1]
flag=True

# for time in range(1,k+1):
for time in range(1,k+1):
    
    # setting
    attack_lst = make_attack_lst()

    attack,defend = attack_lst[0],attack_lst[-1]

    # 공격자 선정
    attack = find_attack(attack)
    attack_loc = attack[4]
    defend_loc = defend[4]
    time_dict[attack_loc] = time

    # 공격
    related_lst = set()
    related_lst.add(attack_loc)
    related_lst.add(defend_loc)
    attack_to_defend(attack_loc,defend_loc)

    # 포탑 부서짐
    cnt = find_break()
    if cnt<=1:
        break

    # 정비
    fix()

    # pprint(attack_grid)

print(find_result())





