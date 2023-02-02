'''
2
5 3
0 0 1 1 1
1 1 1 1 0
0 0 1 0 0
0 1 1 1 1
1 1 1 0 1
5 3
1 0 0 1 0
1 1 0 1 1
1 0 1 1 1
0 1 1 0 1
0 1 1 1 0

'''

def count_one(grid,y,m):
    cnt=0
    for x in ''.join(map(str,grid[y])).split('0'):
        if x=='1'*m:
            cnt+=1
    return cnt

for tc in range(1,int(input())+1):
    n,m = map(int,input().split())
    grid = [list(map(int,input().split())) for _ in range(n)]
    z_grid = list(map(list,zip(*grid)))
    cnt = 0
    for y in range(n):
        cnt+=count_one(grid,y,m)
        cnt+=count_one(z_grid,y,m)
    print(f'#{tc} {cnt}')