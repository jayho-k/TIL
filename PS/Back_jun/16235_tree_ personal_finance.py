'''
5 2 1
2 3 2 3 2
2 3 2 3 2
2 3 2 3 2
2 3 2 3 2
2 3 2 3 2
2 1 3
3 2 3

'''
import sys
from collections import deque
input = sys.stdin.readline


n,m,k = map(int,input().split())
A = [[-1]*n]+[[-1]+list(map(int,input().split())) for _ in range(n)]

# y,x,age
trees = [list(map(int,input().split())) for _ in range(m)]

# start
grid = [[-1]*n]+[[-1]+[5]*n for _ in range(n)]

for _ in range(k):

    # spring
    trees.sort(key=lambda x: (x[2],x[1],x[0]))
    t = len(trees)

    deads = []
    new_trees = []
    for x,y,age in trees:
        if grid[y][x] - age < 0:
            deads.append([x,y,age])

        else:
            grid[y][x] -= age
            age += 1
            new_trees.append([x,y,age])

    # summer
    if deads != []:
        for ddx,ddy,dd_age in deads:
            grid[ddy][ddx] += dd_age//2

    # fall
    dy = [-1,-1,0,1,1,1,0,-1]
    dx = [0,1,1,1,0,-1,-1,-1]
        
    b_trees = []
    for xx,yy, t_age in new_trees:

        if t_age%5 == 0:
            for d in range(8):
                ny = yy + dy[d]
                nx = xx + dx[d]
                if 1<=ny<n+1 and 1<=nx<n+1:
                    b_trees.append([nx,ny,1])

    # winter
    for wy in range(n):
        for wx in range(n):
            grid[wy][wx] += A[wy][wx]

    trees = new_trees + b_trees

print(len(trees))

