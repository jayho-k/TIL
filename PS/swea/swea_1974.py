'''
1
7 3 6 4 2 9 5 8 1
5 8 9 1 6 7 3 2 4
2 1 4 5 8 3 6 9 7
8 4 7 9 3 6 1 5 2
1 5 3 8 4 2 9 7 6
9 6 2 7 5 1 8 4 3
4 2 1 3 9 8 7 6 5
3 9 5 6 7 4 2 1 8
6 7 8 2 1 5 4 3 9

1
7 3 6 4 2 9 5 8 1
5 8 9 1 6 7 3 2 4
2 1 4 5 8 3 6 9 7
8 4 7 9 3 6 1 5 2
1 5 3 8 4 2 9 7 6
9 6 2 7 5 1 8 4 3
4 2 1 3 9 8 7 6 5
3 9 5 6 7 4 2 1 8
6 7 8 2 1 5 4 3 9
'''
from collections import Counter

def confirm_sudo(grid):
    
    tmp = [[0]*9 for _ in range(9)]

    for y in range(9):
        height = [0]*9
        weight = [0]*9
        for x in range(9):
            height[grid[y][x]-1]=1
            weight[grid[x][y]-1]=1
        if 0 in Counter(height) or 0 in Counter(weight):
            return 0
    
    for i in range(0,9,3):
        for j in range(0,9,3):
            square = [0]*9
            for ii in range(i,i+3):
                for jj in range(j,j+3):
                    square[grid[ii][jj]-1]+=1
                    tmp[ii][grid[ii][jj]-1]+=1
                    tmp[jj][grid[ii][jj]-1]+=1
            if 0 in Counter(square):
                return 0
            
    return 1


for tc in range(1,int(input())+1):
    grid = [list(map(int,input().split())) for _ in range(9)]
    ans = confirm_sudo(grid)
    print(f"#{tc} {ans}")


