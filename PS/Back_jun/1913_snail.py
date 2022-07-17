'''

7
35

'''
def snail(i,step):

    global ay,ax,y,x,d

    while i <=nn:

        for _ in range(2):
            for _ in range(step):

                grid[y][x] = i
                y = y+dy[d]
                x = x+dx[d]
                i += 1

                if i == num:
                    ay = y
                    ax = x

                if i == nn+1:
                    return

            d = (d+1)%4
        step += 1

from pprint import pprint

n = int(input())
num = int(input())
nn = n*n
grid = [[0]*n for _ in range(n)]

y = n//2
x = n//2

i = 1
d = 0
step = 1

dy = [-1,0,1,0]
dx = [0,1,0,-1]


ay = 0
ax = 0

snail(i,step)

for a in range(n):
    print(*grid[a])


if num == 1:
    print(n//2+1,n//2+1)

else:
    print(ay+1,ax+1)
