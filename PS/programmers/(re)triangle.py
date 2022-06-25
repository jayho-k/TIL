'''
[[7], [3, 8], [8, 1, 0], [2, 7, 4, 4], [4, 5, 2, 6, 5]]
result = 30
'''
from itertools import permutations



triangle = [[7], [3, 8], [8, 1, 0], [2, 7, 4, 4], [4, 5, 2, 6, 5]]
# 0 / 0 1 / 0 1 2 / 0 1 2 3 / 0 1 2 3 4 5
n = len(triangle)

mxsm = 0
dimx = 0
t = 0
for i in range(n):
    dism = 0
    sm = 0
    for j in range(n-1,i-1,-1):

        tri = triangle[j]

        if i >= j:
            for k in range(i+1):
                sm += triangle[i][i]
        sm += tri[i]

    for j in range(n-1,i-1,-1):
        if triangle[j][i] > triangle[j][i-1]:
            di = triangle[j][i] - triangle[j][i-1]
            dism += di
            # dimx = max(dimx,dism)
        else:
            break
    mxsm = max(mxsm,(sm+dism))
    print((sm+dism))
    
# print(sm)
# print(dimx)
print(mxsm)
