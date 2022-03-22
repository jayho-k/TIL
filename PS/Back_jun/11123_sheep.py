'''
2
4 4
#.#.
.#.#
#.##
.#.#
3 5
###.#
..#..
#.###
'''
from collections import deque
from pprint import pprint
def bfs(y,x,num):

    q = deque([(y,x)])
    visited[y][x] = num
    dy = [0,0,1,-1]
    dx = [1,-1,0,0]

    while q:
        y,x = q.popleft()

        for d in range(4):
            ny = y +dy[d]
            nx = x +dx[d]

            if 0<=ny<n and 0<=nx<m and grid[ny][nx] == '#' and visited[ny][nx] == 0:
                visited[ny][nx] = num
                q.append((ny,nx))

 
T = int(input())
for tc in range(1,T+1):

    n,m = map(int, input().split())
    grid = [list(input()) for _ in range(n)]
    visited = [[0]*m for _ in range(n)]

    num = 0
    for y in range(n):
        for x in range(m):
            if visited[y][x] == 0 and grid[y][x] == '#':
                num += 1
                bfs(y,x,num)
    
    print(num)
    for i in visited:
        print(i)
