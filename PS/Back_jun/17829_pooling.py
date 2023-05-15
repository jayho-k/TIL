"""
4
-6 -8 7 -4
-5 -5 14 11
11 11 -1 -1
4 9 -2 -4
"""
def play(n,grid):
    while 1:
        tmp_grid = [[0]*(n//2) for _ in range(n//2)]

        y_cnt = 0
        for y in range(0,n,2):
            x_cnt = 0
            for x in range(0,n,2):
                lst = []
                for yy in range(y,y+2):
                    for xx in range(x,x+2):
                        lst.append(grid[yy][xx])
                tmp_grid[y_cnt][x_cnt] = sorted(lst)[-2]
                x_cnt+=1
            y_cnt+=1

        n = n//2
        grid = tmp_grid

        if n<=1:
            return tmp_grid[0][0]


n = int(input())
grid = [list(map(int,input().split())) for _ in range(n)]
print(play(n,grid))