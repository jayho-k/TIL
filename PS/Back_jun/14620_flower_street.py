'''
6
1 0 2 3 3 4
1 1 1 1 1 1
0 0 1 1 1 1
3 9 9 0 1 99
9 11 3 1 0 3
12 3 0 0 0 1
'''
# 재귀 연습으로 해보기 itertools사용하지 않고

from pprint import pprint
from itertools import combinations

def Loc(n):
    loc = []
    for y in range(n):
        for x in range(n):
            loc.append((y,x))
    
    return loc

def check(fl):
    
    total = 0
    visited = [[0]*n for _ in range(n)]
    for y,x in fl:
        if visited[y][x] == 0:
            visited[y][x] = 1
            total += grid[y][x]

            for d in range(4):
                ny = y+dy[d]
                nx = x+dx[d]

                if 0<=ny<n and 0<=nx<n and visited[ny][nx] == 0:
                    visited[ny][nx] = 1
                    total += grid[ny][nx]
                    
                else:
                    return
        else:
            return
    
    return total


n = int(input())
grid = [list(map(int,input().split())) for _ in range(n)]
visited = [[0]*n for _ in range(n)]
loc = Loc(n)

dy = [0,0,1,-1]
dx = [1,-1,0,0]

flower_loc = list(map(list,combinations(loc,3)))

mn = 1e9
for fl in flower_loc:
    total = check(fl)
    if total == None:
        continue

    else:
        mn = min(mn,total)

print(mn)






# for fl in flower_loc:
#     total = 0
#     visited = [[0]*n for _ in range(n)]
#     for y,x in fl:
#         if visited[y][x] == 0:
#             visited[y][x] = 1
#             total += grid[y][x]
#             for d in range(4):
#                 ny = y+dy[d]
#                 nx = x+dx[d]
#                 if visited[ny][nx] == 0:
#                     visited[ny][nx] = 1
#                     total += grid[ny][nx]
                




