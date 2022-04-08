'''

'''
m = 4
n = 3 
py,px = (2,2)

grid = [[-1]*(m+1)]+[[-1]+[0]*m for _ in range(n)]
grid[py][px] = -1

print(grid)

for i in range(n):
    for j in range(n):
        if i == j == 1:
            continue

        if i == 1:
            pass

        elif j == 1:
            pass
        else:
            grid


