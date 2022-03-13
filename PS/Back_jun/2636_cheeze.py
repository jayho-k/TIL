'''
bfs이용
1. (0,0)부터 점점 버지기 시작하면서 겉에만 표기
2. 그리고 표시한 부분을 한번에 제거한다

'''
from pprint import pprint
from collections import deque

def search(y,x):
    
    q = deque([(y,x)])

    while q:
        y,x = q.popleft()

        dy = [0,0,1,-1]
        dx = [1,-1,0,0]

        for d in range(4):
            ny = y + dy[d]
            nx = x + dx[d]

            if 0<=ny<n and 0<=nx<m:
                if grid[ny][nx]==0:
                    grid[ny][nx] = -1
                    q.append((ny,nx))

                if grid[ny][nx]==1:
                    grid[ny][nx] = 5

n,m = map(int, input().split())
grid = [list(map(int, input().split())) for _ in range(n)]
cnt = 0
nm = n*m

ch_lst = []
while 1:
    lst = []
    search(0,0)

    ch = 0
    for y in range(n):
        lst += grid[y]
        for x in range(m):
            if grid[y][x] == -1:
                grid[y][x] = 0

            if grid[y][x] == 5:
                grid[y][x] = 0
                ch += 1

    ch_lst.append(ch)
    if sum(lst) == -nm:
        break

    cnt += 1
    # pprint(grid)

print(cnt)
print(ch_lst[-2])


