'''
5 2 1
2 3 2 3 2
2 3 2 3 2
2 3 2 3 2
2 3 2 3 2
2 3 2 3 2
2 1 3
3 2 3
trees.sort(key=lambda x: (x[2],x[1],x[0]))


10 1 1000
100 100 100 100 100 100 100 100 100 100
100 100 100 100 100 100 100 100 100 100
100 100 100 100 100 100 100 100 100 100
100 100 100 100 100 100 100 100 100 100
100 100 100 100 100 100 100 100 100 100
100 100 100 100 100 100 100 100 100 100
100 100 100 100 100 100 100 100 100 100
100 100 100 100 100 100 100 100 100 100
100 100 100 100 100 100 100 100 100 100
100 100 100 100 100 100 100 100 100 100
1 1 1



'''
import sys
from collections import deque
import time
input = sys.stdin.readline
n,m,k = map(int,input().split())
ground = [list(map(int,input().split())) for _ in range(n)]
trees = [tuple(map(int,input().split())) for _ in range(m)]
energy = [[5]*n for _ in range(n)]
energy_tmp = [[0]*n for _ in range(n)]
ddy = [-1,-1,0,1,1,1,0,-1]
ddx = [0,1,1,1,0,-1,-1,-1]

start = time.time()
for num in range(k):

    # spring
    trees.sort(key=lambda x: (x[2],x[1],x[0]))
    trees = deque(trees)
    Ntrees = []
    dead = []
    while trees:
        ex,ey,e_age = trees.popleft()
        E = energy[ey-1][ex-1] + (ground[ey-1][ex-1]*num) + energy_tmp[ey-1][ex-1]
        if E >= e_age:
            energy_tmp[ey-1][ex-1] -= e_age
            e_age += 1
            if e_age%5 == 0:
                for d in range(8):
                    ny = ey+ddy[d]
                    nx = ex+ddx[d]
                    if 0<ny<=n and 0<nx<=n:
                        Ntrees.append((nx,ny,1))

            Ntrees.append((ex,ey,e_age))
        else:
            # dead
            dead.append((ex,ey,e_age))

    # summer
    for dx,dy,d_age in dead:
        energy[dy-1][dx-1] += int(d_age/2)
    trees = Ntrees
print(time.time()-start)
print(len(trees))



# import sys
# from collections import deque
# input = sys.stdin.readline

# def spring():
#     pass

# n,m,k = map(int,input().split())
# ground = [list(map(int,input().split())) for _ in range(n)]
# trees = [tuple(map(int,input().split())) for _ in range(m)]
# energy = [[5]*n for _ in range(n)]
# energy_tmp = [[0]*n for _ in range(n)]
# ddy = [-1,-1,0,1,1,1,0,-1]
# ddx = [0,1,1,1,0,-1,-1,-1]

# for num in range(k):

#     # spring
#     trees.sort(key=lambda x: (x[2],x[1],x[0]))
#     Ntrees = []
#     dead = []
    
#     for ex,ey,e_age in trees:
#         E = energy[ey-1][ex-1] + (ground[ey-1][ex-1]*num) + energy_tmp[ey-1][ex-1]
#         if E >= e_age:
#             energy_tmp[ey-1][ex-1] -= e_age
#             e_age += 1
#             if e_age%5 == 0:
#                 for d in range(8):
#                     ny = ey+ddy[d]
#                     nx = ex+ddx[d]
#                     if 0<ny<=n and 0<nx<=n:
#                         Ntrees.append((nx,ny,1))

#             Ntrees.append((ex,ey,e_age))
#         else:
#             # dead
#             dead.append((ex,ey,e_age//2))

#     # summer
#     for dx,dy,d_age in dead:
#         energy[dy-1][dx-1] += d_age
#     trees = Ntrees
    
# print(len(trees))







# '''
# 5 2 1
# 2 3 2 3 2
# 2 3 2 3 2
# 2 3 2 3 2
# 2 3 2 3 2
# 2 3 2 3 2
# 2 1 3
# 3 2 3

# '''
# import sys
# from collections import deque
# input = sys.stdin.readline


# n,m,k = map(int,input().split())
# A = [[-1]*n]+[[-1]+list(map(int,input().split())) for _ in range(n)]

# # y,x,age
# trees = [list(map(int,input().split())) for _ in range(m)]

# # start
# grid = [[-1]*n]+[[-1]+[5]*n for _ in range(n)]

# for _ in range(k):

#     # spring
#     trees.sort(key=lambda x: (x[2],x[1],x[0]))
#     t = len(trees)

#     deads = []
#     new_trees = []
#     for x,y,age in trees:
#         if grid[y][x] - age < 0:
#             deads.append([x,y,age])

#         else:
#             grid[y][x] -= age
#             age += 1
#             new_trees.append([x,y,age])

#     # summer
#     if deads != []:
#         for ddx,ddy,dd_age in deads:
#             grid[ddy][ddx] += dd_age//2

#     # fall
#     dy = [-1,-1,0,1,1,1,0,-1]
#     dx = [0,1,1,1,0,-1,-1,-1]
        
#     b_trees = []
#     for xx,yy, t_age in new_trees:

#         if t_age%5 == 0:
#             for d in range(8):
#                 ny = yy + dy[d]
#                 nx = xx + dx[d]
#                 if 1<=ny<n+1 and 1<=nx<n+1:
#                     b_trees.append([nx,ny,1])

#     # winter
#     for wy in range(n):
#         for wx in range(n):
#             grid[wy][wx] += A[wy][wx]

#     trees = new_trees + b_trees

# print(len(trees))

