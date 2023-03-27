'''
5 4 1
1 2 0 1 2
1 0 3 3 1
1 3 0 2 3
2 1 2 4 5
0 1 3 2 0
1 3 2 3
2 2 1 5
3 3 2 2
5 1 3 4

y,x =>

2 2 1
0 1
1 0
1 1 1 5
2 2 0 1

4 6 129
67732 49740 76676 0
88582 26758 1197 0
58181 0 75645 0
0 84506 86920 0
4 4 0 21
2 4 1 29
3 4 2 47
4 1 3 23
3 2 3 46
1 4 2 59

7777596 6296272 1599814 575505 1591925 205740

'''

def find_guns_loc():
    guns_loc = {}    
    for y in range(n):
        for x in range(n):
            if grid[y][x]:
                guns_loc[(y,x)]=[grid[y][x]]
            else:
                guns_loc[(y,x)]=[]
    return guns_loc


def get_gun(y,x):
    if guns_loc[(y,x)]:
        guns_loc[(y,x)].sort()
        return guns_loc[(y,x)].pop()
    else:
        return 0

def check_gun(p,gun):
    if players[p][-1]<gun:
        guns_loc[(players[p][0],players[p][1])].append(players[p][-1])
        players[p][-1] = gun
    else:
        guns_loc[(players[p][0],players[p][1])].append(gun)


def fight(p1_s,p1_g,p2_s,p2_g,p1,p2):

    # 이긴 player가 앞, 진 player가 뒤
    p1_power = p1_s+p1_g
    p2_power = p2_s+p2_g

    if p1_power>p2_power:
        return (p1,p2)

    elif p1_power<p2_power:
        return (p2,p1)

    else:
        if p1_s > p2_s:
            return (p1,p2)

        elif p1_s<p2_s:
            return (p2,p1)

def move_check(lny,lnx):
    # 범위 밖이면 false
    if lny>=n or lny<0 or lnx>=n or lnx<0:
        return False
    
    # player가 존재하면 false
    for find_p in range(m):
        if (players[find_p][0],players[find_p][1])==(lny,lnx):
            return False
        
    # 나머지 True
    return True

# setting
n,m,k  = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]
players = {}
for p in range(m):
    y,x,d,s = map(int,input().split())
    players[p] = [y-1,x-1,d,s,0]

guns_loc = find_guns_loc()
dy = [-1,0,1,0]
dx = [0,1,0,-1]


# 북 동 남 서
# 0  1  2  3
rev = [2,3,0,1]
points = [0]*m


for r in range(k):
    # print('round : ',r+1)
    for p1 in range(m):
        p1_y,p1_x,p1_d,p1_s,p1_g = players[p1]
        p1_ny = p1_y+dy[p1_d]
        p1_nx = p1_x+dx[p1_d]

        # 범위 밖 => 방향바꾸고 ny,nx다시 setting
        if p1_ny>=n or p1_ny<0 or p1_nx>=n or p1_nx<0:
            p1_nd = rev[p1_d]
            p1_ny = p1_y+dy[p1_nd]
            p1_nx = p1_x+dx[p1_nd]
            players[p1][2] = p1_nd
            
        players[p1][0]=p1_ny
        players[p1][1]=p1_nx

        p1_gun = get_gun(players[p1][0],players[p1][1])
        check_gun(p1,p1_gun)

        # player가 있는지 확인
        for p2 in range(m):
            if p1==p2:
                continue

            # palyer를 만남
            if (players[p1][0], players[p1][1]) == (players[p2][0], players[p2][1]):
                
                # 싸워
                p2_y,p2_x,p2_d,p2_s,p2_g = players[p2]
                win,los = fight(p1_s,p1_g,p2_s,p2_g,p1,p2)

                # 이김 => point 
                points[win]+= abs((p1_s+p1_g)-(p2_s+p2_g))

                # 짐 => 총기 버림
                guns_loc[(players[los][0],players[los][1])].append(players[los][-1])
                players[los][-1]=0

                # 짐 => 이동
                for _ in range(4):
                    lny = players[los][0] + dy[players[los][2]]
                    lnx = players[los][1] + dx[players[los][2]]
                    if move_check(lny,lnx):
                        players[los][0] = lny
                        players[los][1] = lnx
                        break
                    else:
                        players[los][2] = (players[los][2]+1)%4

                #만약 총이 보이면 획득
                wgun = get_gun(players[win][0],players[win][1])
                check_gun(win,wgun)

                lgun = get_gun(players[los][0],players[los][1])
                check_gun(los,lgun)

print(*points)




                
        





