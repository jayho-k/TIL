# '''




# '''
from collections import deque

def bfs(y,x):
    global ans
    q = deque([(y,x)])
    grid[y][x] = 1

    while q:
        y,x = q.popleft()

            
        dy = [0,0,-1,1]
        dx = [-1,1,0,0]
        
        for d in range(4):
            ny = y + dy[d]
            nx = x + dx[d]

            if 0<=ny<n and 0<=nx<n and grid[ny][nx] != 1:
                if grid[ny][nx] == 3:
                    ans = 1
                    return
                q.append((ny,nx))
                grid[ny][nx] = 1
                
T = 10
for tc in range(1,T+1):
    t = int(input())
    n = 16
    grid = [list(map(int, input())) for _ in range(n)]
    ans = 0
    bfs(1,1)
    print(f'#{tc} {ans}')


# # from pprint import pprint
# # def dfs(y,x):
# #     global ans

# #     dy = [0,0,-1,1]
# #     dx = [-1,1,0,0]
    
# #     for d in range(4):
# #         ny = y + dy[d]
# #         nx = x + dx[d]

# #         if 0<=ny<n and 0<=nx<n and grid[ny][nx] != 1:
# #             if grid[ny][nx] == 3:
# #                 ans = 1
# #                 return
# #             grid[ny][nx] = 1
# #             # pprint(grid)
# #             dfs(ny,nx)

# # T = 1
# # for tc in range(1,T+1):

# #     t = int(input())
# #     n = 16
# #     grid = [list(map(int, input())) for _ in range(n)]
# #     sty, stx = (1,1)
# #     ans = 0
# #     dfs(sty,stx)

# #     print(ans)