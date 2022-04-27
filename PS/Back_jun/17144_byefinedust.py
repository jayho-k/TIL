'''
시작: 1열에 설치, 두행을 차지


1. 미세먼지 확산
    1) 4방향
    2) 공기청정기 or 칸이 없음 => 공기청정기가 없고, 칸안에 있으면 확산
    3) grid[ny][nx] = grid[y][x]//5             ==>  cnt 
    4) grid[y][x] = (grid[y][x]//5)*확산된 개수

2. 공기청정기
    1) 위쪽 : 반시계
    2) 아래 : 시계
    3) 바람의 방향대로 미세먼지가 한칸씩 이동 (새로운 배열을 만들어 줘야함 [ny], [y]값 잘 활용)
    4) 공기청정기로 들어가면 정화

7 8 1
0 0 0 0 0 0 0 9
0 0 0 0 3 0 0 8
-1 0 5 0 0 0 22 0
-1 8 0 0 0 0 0 0
0 0 0 0 0 10 43 0
0 0 5 0 15 0 0 0
0 0 40 0 0 0 20 0
'''
from pprint import pprint

# 달팽이
def wind(status, lst, w_lst):
    
    # uy,ux = cleaner[0]
    # dwy,dwx = cleaner[1]
    # ux += 1
    # dwx += 1

    # up = [0,3,1,2]
    # down = [0,2,1,3]

    # 위쪽 : 동북서남 /  아래 : 동남서북
    if status == 0:
        dd = [0,3,1,2]
        y,x = cleaner[0]
        x += 1
    else:
        dd = [0,2,1,3]
        y,x = cleaner[1]
        x += 1

    d = 0
    # up: status = 0

    chck[y][x] = 1
    while d <= 3:
        ny = y + dy[dd[d]]
        nx = x + dx[dd[d]]

        if 0<=ny<n and 0<=nx<m:
            if lst[ny][nx] == -1:
                return
            chck[ny][nx] = 1
            w_lst[ny][nx] = lst[y][x]
            y = ny
            x = nx

        else:
            ny = y - dy[dd[d]]
            nx = x - dx[dd[d]]
            d += 1




    # if status == 0:

    #     chck[uy][ux] = 1
    #     while d <= 3:
    #         uny = uy + dy[up[d]]
    #         unx = ux + dx[up[d]]

    #         if 0<=uny<n and 0<=unx<m:
    #             if lst[uny][unx] == -1:
    #                 return
    #             chck[uny][unx] = 1
    #             w_lst[uny][unx] = lst[uy][ux]
    #             uy = uny
    #             ux = unx

    #         else:
    #             uny = uy - dy[up[d]]
    #             unx = ux - dx[up[d]]
    #             d += 1

    # else:
    #     chck[dwy][dwx] = 1
    #     while d <= 3:
    #         dwny = dwy + dy[down[d]]
    #         dwnx = dwx + dx[down[d]]

    #         if 0<=dwny<n and 0<=dwnx<m:
    #             if lst[dwny][dwnx] == -1:
    #                 return
    #             chck[dwny][dwnx] = 1
    #             w_lst[dwny][dwnx] = lst[dwy][dwx]
    #             dwy = dwny
    #             dwx = dwnx
    #         else:
    #             dwny = dwy - dy[down[d]]
    #             dwnx = dwx - dx[down[d]]
    #             d += 1
            
def clean(grid):
    cleaner = []
    for y in range(n):
        for x in range(m):
            if grid[y][x] == -1:
                cleaner.append((y,x))
    return cleaner

n,m,t = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]
cleaner = clean(grid)

# 동서남북
dy = [0,0,1,-1]
dx = [1,-1,0,0]

for _ in range(t):
    
    # dust
    a_dust = [[0]*m for _ in range(n)]
    for y in range(n):
        for x in range(m):
            if grid[y][x] == -1:
                a_dust[y][x] = -1
                continue

            # 미세먼지일 경우 : 0이 아니고 공기청정기 아니고
            if grid[y][x] != 0 and grid[y][x] != -1:
                d_cnt = 0
                for d in range(4):
                    ny = y + dy[d]
                    nx = x + dx[d]
                    if 0<=ny<n and 0<=nx<m and grid[ny][nx] != -1: # 범위 내, 공기청정기x
                        a_dust[ny][nx] += (grid[y][x]//5)
                        d_cnt += 1
                else:
                    a_dust[y][x] += grid[y][x]-((grid[y][x]//5)*d_cnt)



    # wind
    wind_grid = [[0]*m for _ in range(n)]
    chck = [[0]*m for _ in range(n)]
    for i in range(2):
        wind(i,a_dust,wind_grid)

    for i in range(n):
        for j in range(m):
            if chck[i][j]==0:
                wind_grid[i][j] = a_dust[i][j]

    grid = wind_grid

total = 0
for g in grid:
    total += sum(g)

print(total+2)