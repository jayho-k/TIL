'''
3
4 2 5 1 7
3 1 9 4 5
9 8 1 2 3
8 1 9 3 4
7 2 3 4 8
1 9 2 5 7
6 5 2 3 4
5 1 9 2 8
2 9 3 1 4

1번부터

학생의 순서를 정함
좋아하는 4명

'''
import sys
input = sys.stdin.readline
n = int(input())
grid = [[-1]*(n+1)]+[[-1]+[0]*n for _ in range(n)]
stu = [list(map(int,input().split())) for _ in range(n**2)]

dy = [0,0,1,-1]
dx = [1,-1,0,0]

stf = [0,1,10,100,1000]

for st, *like in stu:
    info = []
    for y in range(1,n+1):
        for x in range(1,n+1):
            # 비어있으면
            if grid[y][x] == 0:
                fav = 0
                empty = 0
                for d in range(4):
                    ny = y+dy[d]
                    nx = x+dx[d]
                    if 1<=ny<n+1 and 1<=nx<n+1 and grid[ny][nx] in like:
                        fav += 1
                    if 1<=ny<n+1 and 1<=nx<n+1 and grid[ny][nx] == 0:
                        empty += 1
                info.append((fav,empty,y,x))
                
    info.sort(key=lambda x: (x[0],x[1]), reverse=True)
    sy,sx = info[0][2],info[0][3]
    grid[sy][sx] = st

total = 0

for y in range(1,n+1):
    for x in range(1,n+1):
        for st,*like in stu:
            cnt = 0
            if st == grid[y][x]:
                for d in range(4):
                    ny = y+dy[d]
                    nx = x+dx[d]
                    if 1<=ny<n+1 and 1<=nx<n+1 and grid[ny][nx] in like:
                        cnt+=1
                total += stf[cnt]

print(total)