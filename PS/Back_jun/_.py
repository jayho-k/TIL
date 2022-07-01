'''




'''
def snail(st,nn,num):
    global ans
    d = 0
    i = 1
    k_num = 1
    point = (st,st)

    while 1:
        
        for _ in range(2):
            for _ in range(k_num):
                y,x = point
                grid[y][x] = i

                if grid[y][x] == num:
                    ans = (y+1,x+1)
                
                ny=y+dy[d]
                nx=x+dx[d]
                point = (ny,nx)

                i+=1
                if i==nn+1:
                    return

            d=(d+1)%4
        k_num+=1


from pprint import pprint

n = int(input())
num = int(input())
grid = [[0]*n for _ in range(n)]
dy = [-1,0,1,0]
dx = [0,1,0,-1]
st = n//2
nn = n*n
ans = 0

snail(st,nn,num)
pprint(grid)
print(ans[0],ans[1])
