'''
1 1 2 2 3 3 4 4 

돌리는 것을 언제 돌려야함??
계속 돌려야함

두번 계산 하고 num +=1 


'''



from pprint import pprint

n = 7
grid = [[0]*n for _ in range(n)]
y= x = n//2

grid[y][x] = 1

# 서 남 동 북
dy = [0,1,0,-1]
dx = [-1,0,1,0]
d = 0
time = 0

while 1:

    if 0<=y<n and 0<=x<n:
        
        if not d%2:
            time += 1

        for _ in range(time):
            ny = y+dy[d%4]
            nx = x+dx[d%4]
            grid[ny][nx] = time
            y,x = ny, nx
        d+=1

    else:
        break

pprint(grid)
