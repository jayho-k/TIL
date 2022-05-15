'''
4 5
0 0 0 0 0
0 0 1 0 0
0 0 0 0 0
0 0 0 0 0
2 2 1 1 1 4

직사각형
y,x
가로 y+h-1, 세로 x+w-1



의 크기 H, W, 시작 좌표 Sr, Sc, 도착 좌표 Fr, Fc가 주어진다.

2x2 => 직사각형
1,1
1,4

'''
def bfs(y,x,w_lst):

    q = deque([(y,x)])
    visited[y][x] = 1
    dy = [0,0,1,-1]
    dx = [1,-1,0,0]

    while q:
        y,x = q.popleft()

        for d in range(4):
            ny = y + dy[d]
            nx = x + dx[d]

            if 0<=ny<n and 0<=nx<m and visited[ny][nx] == 0 and grid[ny][nx] != 1 and squre(ny,nx,w_lst) and 0<=y+h-1<n and 0<=x+w-1<m:
                visited[ny][nx] = visited[y][x] + 1
                q.append((ny,nx))


def wll(grid):
    w = []
    for y in range(n):
        for x in range(m):
            if grid[y][x] == 1:
                w.append((y,x))
    return w

def squre(y,x,wll):
    
    for wy,wx in wll:
        # 직사각형 범위 안에 wall이 있으면
        if y<=wy<y+h and x<=wx<x+w :
            return False
    return True


from pprint import pprint
from collections import deque
import sys

input = sys.stdin.readline
n,m = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]
h,w,sy,sx,fy,fx = map(int,input().split())

w_lst = wll(grid)

visited = [[0]*m for _ in range(n)]
bfs(sy-1,sx-1,w_lst)

# pprint(visited)

if visited[fy-1][fx-1] == 0:
    print(-1)
else:
    print(visited[fy-1][fx-1]-1)