'''
색종이
'''
import sys
from pprint import pprint

n = int(sys.stdin.readline())

grid = [[0]*1001 for _ in range(1001)]

for num in range(1,n+1):
    x1,y1,w,h = map(int, sys.stdin.readline().split())
    x2 = x1 + w
    y2 = y1 + h
    for y in range(y1, y2):
        # 슬라이스를 이용해서 통째로 그 부분을 바꿔주는 것이다
        grid[y][x1:x2] = [num]*w

# pprint(grid)

        # for x in range(x1,x2): # 시간이 오래걸림
        #     grid[y][x] = num

# grid = sum(grid,[]) 시간이 너무 오래걸림

for i in range(1,n+1):
    cnt = 0
    for g in grid:
        cnt += g.count(i)

    print(cnt)

