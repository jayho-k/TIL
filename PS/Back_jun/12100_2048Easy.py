'''
3
4 2 0
4 4 4
8 8 8

4
1 0 0 1
2 2 2 2
4 2 4 2
4 4 8 8

4
0 0 0 0
2 2 2 2
4 2 4 2
4 4 8 8
'''
def copy_grid(grid):
    n_grid = [[0]*n for _ in range(n)]
    for y in range(n):
        for x in range(n):
            n_grid[y][x] = grid[y][x]

    return n_grid


def move(grid,m):

    # 동
    if m==0:
        for m0y in range(n):
            point = n-1
            for m0x in range(n-2,-1,-1):
                if grid[m0y][m0x]:
                    tmp = grid[m0y][m0x]
                    grid[m0y][m0x] = 0

                    if grid[m0y][point] == 0:
                        grid[m0y][point] = tmp

                    elif grid[m0y][point] == tmp:
                        grid[m0y][point] = tmp*2
                        point-=1

                    else:
                        point-=1
                        grid[m0y][point] = tmp


    elif m==1:
        for m1x in range(n):
            point = n-1
            for m1y in range(n-2,-1,-1):
                if grid[m1y][m1x]:
                    tmp = grid[m1y][m1x]
                    grid[m1y][m1x] = 0

                    if grid[point][m1x] == 0:
                        grid[point][m1x] = tmp

                    elif grid[point][m1x] == tmp:
                        grid[point][m1x] =tmp*2
                        point -= 1

                    else:
                        point-=1
                        grid[point][m1x] = tmp

    elif m==2:
        for m2y in range(n):
            point = 0
            for m2x in range(1,n):
                if grid[m2y][m2x]:
                    tmp = grid[m2y][m2x]
                    grid[m2y][m2x] = 0

                    if grid[m2y][point] == 0:
                        grid[m2y][point] = tmp

                    elif grid[m2y][point] == tmp:
                        grid[m2y][point] = tmp*2
                        point += 1

                    else:
                        point += 1
                        grid[m2y][point] = tmp

    else:
        for m3x in range(n):
            point = 0
            for m3y in range(1,n):
                if grid[m3y][m3x]:
                    tmp = grid[m3y][m3x]
                    grid[m3y][m3x] = 0

                    if grid[point][m3x] == 0:
                        grid[point][m3x] = tmp

                    elif grid[point][m3x] == tmp:
                        grid[point][m3x] = tmp*2
                        point += 1

                    else:
                        point += 1
                        grid[point][m3x] = tmp

    return grid

def dfs(grid,d):
    global ans
    if d == 5:
        for y in range(n):
            for x in range(n):
                if ans < n_grid[y][x]:
                    ans = n_grid[y][x]
                # ans = max(ans,grid[y][x])
        return

    for m in range(4):
        n_grid = copy_grid(grid)
        n_grid = move(n_grid,m)
        dfs(n_grid, d+1)

from pprint import pprint
n = int(input())
grid = [list(map(int,input().split())) for _ in range(n)]
ans = 0

# 0:동, 1:남, 2:서, 3:북
# pprint(move(grid,1))
# pprint(move(grid,1))
# pprint(move(grid,0))
# pprint(move(grid,0))

dfs(grid,0)
print(ans)




