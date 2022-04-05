'''
3
3
0 2 1
0 1 1
1 1 1
5
0 0 0 0 0 
0 1 2 3 0 
0 2 3 4 0 
0 3 4 5 0 
0 0 0 0 0 
5
0 1 1 1 0 
1 1 0 1 0 
0 1 0 1 0 
1 0 0 1 1 
1 1 1 1 1

1
5
0 0 0 0 0 
0 1 2 3 0 
0 2 3 4 0 
0 3 4 5 0 
0 0 0 0 0 
'''
import heapq
from collections import deque
from pprint import pprint

def dsk(y,x):

    q = []
    heapq.heappush(q,(0,y,x))
    table[y][x] = 0
    dy = [0,0,1,-1]
    dx = [1,-1,0,0]

    while q:
        cost, y, x = heapq.heappop(q)

        if cost <= table[y][x]:
            for d in range(4):
                ny = y + dy[d]
                nx = x + dx[d]

                tmp = 0
                if  0<=ny<n and 0<=nx<n:
                    if grid[ny][nx] > grid[y][x]:
                        tmp = cost + grid[ny][nx] - grid[y][x] + 1
                    else:
                        tmp = cost + 1

                    if cost < table[ny][nx]:
                        table[ny][nx] = tmp
                        heapq.heappush(q,(tmp,ny,nx))
            


T = int(input())
for tc in range(1,T+1):
    inf = 1e9
    n = int(input())
    grid = [list(map(int,input().split())) for _ in range(n)]
    table = [[1e9]*(n) for _ in range(n)]
    dsk(0,0)
    print(table)


# def bfs(y,x):

#     q = deque([(y,x)])
#     visited[y][x] = 0

#     dy = [0,0,1,-1]
#     dx = [1,-1,0,0]

#     while q:
#         y,x = q.popleft()

#         for d in range(4):
#             ny = y+dy[d]
#             nx = x+dx[d]

#             if 0<=ny<n and 0<=nx<n:
#                 t = 0
#                 if grid[ny][nx] > grid[y][x]:
#                     t = (grid[ny][nx]-grid[y][x])

#                 # 다시
#                 if visited[ny][nx] >= visited[y][x] + t + 1:
#                     visited[ny][nx] =  visited[y][x] + 1 + t
#                     q.append((ny,nx))

# T = int(input())
# for tc in range(1,T+1):
#     inf = 1e9
#     n = int(input())
#     grid = [list(map(int,input().split())) for _ in range(n)]
#     visited = [[inf]*n for _ in range(n)]

#     bfs(0,0)

#     # pprint(visited)
#     print(f'#{tc} {visited[n-1][n-1]}')
