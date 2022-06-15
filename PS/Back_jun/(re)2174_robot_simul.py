'''




5 4
2 2
1 1 E
5 4 W
1 F 7
2 F 7

아래부터? => 그냥 처음에 세팅하고 reverse돌리자

범위
0<=ny<m
0<nx<=n

'''
def order_play(a,b,oro,odi,onum):
    for y in range(b+1):
        for x in range(a+1):
            if grid[y][x] !=0 and grid[y][x][0] == oro:
                robot_num, robot_di = grid[y][x]

                a = order_num(odi,onum, robot_di,y,x, robot_num)
                if a == None:
                    continue

                else:
                    return a
                    
    return
                    


def order_num(odi,onum, robot_di,y,x, robot_num):
    # 반복 order 진행 , 한번 진행 하고 check하고 계속 확인을 해줘야함
    d = {'N':0,'E':1,'S':2,'W':3}
    dy = [-1,0,0,1]
    dx = [0,-1,1,0]

    if odi == 'R':
        tmp = onum+d[robot_di]
        tmp %= 4
        return tmp

    elif odi == 'L':
        d[robot_di] -= onum%4
        if d[robot_di] <0:
            d[robot_di] += 4


    elif odi == 'F':
        for _ in range(onum):
            ny = y+dy[d[robot_di]]
            nx = x+dx[d[robot_di]]
            status  = check(ny,nx)
            if status == 'save':
                grid[ny][nx] = grid[y][x]
                grid[y][x] = 0
                y = ny
                x = nx

            elif status == 'crush':
                crash = f"Robot {robot_num} crashes into robot {grid[ny][nx][0]}"
                return crash

            else:
                wall = f"Robot {robot_num} crashes into the wall"
            
                return wall
        
        return 


def check(ny,nx):
    # wall

    if 0<=ny<m and 1<=nx<=n and grid[ny][nx] == 0:
        return 'save'

    elif grid[ny][nx] != 0:
        return 'crush'

    else:
        return False




a,b = map(int,input().split())
n,m = map(int,input().split()) # n : 로봇개수, m : 명령
robot = []
order = []

for _ in range(n):
    x,y,di = input().split()
    robot.append([int(y),int(x),di])

for _ in range(m):
    r,o,on = input().split()
    order.append([int(r),o,int(on)])

grid = [[0]*(a+1) for _ in range(b+1)]

for i in range(n):
    ly,lx,di = robot[i]
    grid[ly][lx] = [i+1,di]

grid.reverse()


for o in order:

    oro,odi,onum = o
    a = order_play(a,b,oro,odi,onum)
    if a == None:
        continue
    else:
        print(a)
        break

else:
    print('OK')

