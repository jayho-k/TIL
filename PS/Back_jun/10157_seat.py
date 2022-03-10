'''
padding을 해주고


'''
from pprint import pprint

import sys
gy, gx = map(int, sys.stdin.readline().split())
n = int(sys.stdin.readline())
grid = [[0]*(gx+1) for _ in range(gy+1)]

x = 0  # 초기화를 시킬때 x하나빼고 시작// 그리고 grid[ny][nx]로 만든다 이것이 포인트다
    # 안그러면 끝까지 같을때 
y = 1
di = 0
dx = [1,0,-1,0]
dy = [0,1,0,-1]

if n > gx*gy:
    print(0)
else:
    i = 0
    while i < n:
        # 동 남 서 북
        nx = x + dx[di%4]
        ny = y + dy[di%4]

        if 1<= nx <= gx and 1<=ny<=gy and grid[ny][nx] == 0:
            i += 1 # i먼저 업글해주고 그리드에 표시를 해주어야한다.
            x,y = nx, ny
            grid[ny][nx] = i
            
        else:
            nx -= dx[di%4]
            ny -= dy[di%4]
            di += 1

    pprint(grid)
    print(y, x)

