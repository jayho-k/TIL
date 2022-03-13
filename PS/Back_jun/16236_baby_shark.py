'''
1. 처음 상어의 크기: 2
2. 물고기가 더 크면 먹을수 있음
3. 물고기보다 작으면 지나갈 수 없음
4. 크기 =2 ==> 2마리먹으면 3으로 진화

이동방법
1. 물고기 한마리 => 바로 먹으러 감
2. 물고기 > 1   ==> 가까운거 부터 먹음
3. 위 왼쪽

lst 다 넣지 말고 bfs로 최소 값 가능! 한번 구현

'''
# bfs
from pprint import pprint
from collections import deque

def stp():
    for y in range(n):
        for x in range(n):
            if grid[y][x] == 9:
                grid[y][x] = 0
                return y, x

def bfs(y,x,shark):
    q = deque([(y,x)])
    visited = [[0]*n for _ in range(n)]
    visited[y][x] = 1
    d_lst = []

    dy = [-1,1,0,0]
    dx = [0,0,-1,1]

    while q:
        y,x = q.popleft()
        for d in range(4):
            ny = y + dy[d]
            nx = x + dx[d]
            
            # 이아기가 통로를 지나갈 수 있니? 물고기를 지나갈 수 있니??
            if 0<=ny<n and 0<=nx<n and grid[ny][nx] <= shark and visited[ny][nx] == 0:
                visited[ny][nx] = visited[y][x] + 1
                q.append((ny,nx))

            # 물고기를 먹을 수 있니?
            if 0<=ny<n and 0<=nx<n and 0 < grid[ny][nx] < shark:
                visited[ny][nx] = visited[y][x] + 1
                d =  visited[ny][nx] - 1
                d_lst.append((d,ny,nx))
                # grid[ny][nx] = 0

    if d_lst:
        d_lst.sort()
        d,y,x = d_lst[0]
        grid[y][x] = 0
        return d,y,x

    else:
        return 0,ny,nx    


n = int(input())
grid = [list(map(int, input().split())) for _ in range(n)]
sty, stx = stp()

# stp를 초기화시켜주기
# while문을 사용한다면 break를 언제 걸어줘야 하나?

shark = 2
cnt = 0
total_d = 0
while 1:

    d, y, x = bfs(sty,stx, shark)
    if d == 0:
        break
    sty = y
    stx = x
    cnt += 1
    total_d += d
    if shark == cnt:
        shark += 1
        cnt = 0

print(total_d)



'''
거리만으로 구하기
이렇게 풀면 상어가 본인보다 큰 물고기도 그냥 지나치게 된다.
따라서 이 방법은 막힌것이 없을때 사용하는 것이 좋아 보인다.
'''

from sys import stdin
from collections import deque
from pprint import pprint

def stp():
    for y in range(n):
        for x in range(n):
            if grid[y][x] == 9:
                return y,x


n = int(stdin.readline())
grid = [list(map(int,stdin.readline().split())) for _ in range(n)]
sty,stx = stp()

mxd = 0
shark = 2
cnt = 0

while 1:
    d_lst = deque([])
    mnd = mny = mnx = 1e9

    for y in range(n):
        for x in range(n):
            if 0 < grid[y][x] < shark:
                d = abs(sty-y) +abs(stx-x)
                d_lst.append((d,y,x))
        
    if not d_lst:
        break

    print(d_lst)
    for d,y,x in d_lst:
        if mnd > d:
            mnd = d
            mny = y
            mnx = x

    mxd += mnd
    sty, stx = mny, mnx
    pprint(grid)
    print('sh',shark)
    grid[sty][stx] = 0
    cnt += 1
    if shark == cnt:
        shark += 1
        cnt = 0

print(mxd)