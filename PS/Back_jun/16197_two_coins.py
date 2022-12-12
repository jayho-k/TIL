'''


'''
from pprint import pprint
from collections import deque
import sys

def bfs(coin1,coin2,depth):

    q = deque([(coin1,coin2,depth)])
    while q:

        coin1,coin2,depth = q.popleft()
        y1,x1 = coin1
        y2,x2 = coin2
        if depth >= 10:
            return -1
            
        for d in range(4):
            ny1,nx1 = y1+dy[d],x1+dx[d]
            ny2,nx2 = y2+dy[d],x2+dx[d]


            # 범위 안으로 들어옴
            if 0<=ny1<n and 0<=nx1<m and 0<=ny2<n and 0<=nx2<m:
                
                # 벽이 있을 경우
                if grid[ny1][nx1] == '#':
                    ny1,nx1 = y1,x1

                if grid[ny2][nx2] == '#':
                    ny2,nx2 = y2,x2

                q.append(((ny1,nx1),(ny2,nx2),depth+1))

            elif (ny1<0 or ny1>=n or nx1<0 or nx1>=m) and\
                (ny2<0 or ny2>=n or nx2<0 or nx2>=m):
                continue

            elif ny1<0 or ny1>=n or nx1<0 or nx1>=m:
                return depth + 1
                
            elif ny2<0 or ny2>=n or nx2<0 or nx2>=m:
                return depth + 1

    return -1


def findCoins():
    coins=[]
    for y in range(n):
        for x in range(m):
            if grid[y][x]=='o':
                coins.append((y,x))
    
    # return coins[0],coins[1]
    return coins[0],coins[1]

n,m = map(int,input().split())
grid = [list(input()) for _ in range(n)]
dy = [-1,0,1,0]
dx = [0,1,0,-1]
coin1,coin2 = findCoins()
ans = bfs(coin1,coin2,0)
print(ans)




























# # def bfs(coins,num):

# #     q = deque([coins])
# #     for c in coins:
# #         visited1[c[0]][c[1]]=1

# #     while q:
# #         y,x = q.popleft()
# #         for d in range(4):
# #             ny = y+dy[d]
# #             nx = x+dx[d]
# #             if 0<=ny<n and 0<=nx<m and visited1[ny][nx] == '.':
# #                 pass

# sys.setrecursionlimit(10**6) 
# def dfs(y1,x1,y2,x2,d):
#     global ans
#     for d in range(4):
#         ny1,nx1 = y1+dy[d],x1+dx[d]
#         ny2,nx2 = y2+dy[d],x2+dx[d]

#         if (ny1<0 or ny1>=n or nx1<0 or nx1>=m) and (ny2<0 or ny2>=n or nx2<0 or nx2>=m):
#             return

#         elif (ny1<0 or ny1>=n or nx1<0 or nx1>=m) or (ny2<0 or ny2>=n or nx2<0 or nx2>=m):
#             ans = max(ans,d)
#             print(ans)
#             return


#         if grid[ny1][nx1] == '#' and grid[ny2][nx2] == '#':
#             return

#         # 벽에 박을경우 => 제자리에 있는다, 하지만 num += 1
#         # elif grid[ny1][nx1] != '#' or grid[ny2][nx2] != '#':

#         elif grid[ny1][nx1] == '#':
#             visited2[ny2][nx2] = 1
#             dfs(y1,x1,ny2,nx2,d+1)
#             visited2[ny2][nx2] = 0

#         elif grid[ny2][nx2] == '#':
#             visited2[ny1][nx1] = 1
#             dfs(ny1,nx1,y2,x2,d+1)
#             visited2[ny1][nx1] = 0

#         # 둘다 0일경우 그냥 pass
#         # 하나는 
#         elif visited1[ny1][nx1]==0 and visited1[ny2][nx2]==0:

#             visited1[ny1][nx1] = 1
#             visited1[ny2][nx2] = 1
#             dfs(ny1,nx1,ny2,nx2,d+1)
#             visited1[ny1][nx1] = 0
#             visited1[ny2][nx2] = 0


# def findCoins():
#     coins=[]
#     for y in range(n):
#         for x in range(m):
#             if grid[y][x]=='o':
#                 coins.append((y,x))
    
#     return coins[0],coins[1]

# n,m = map(int,input().split())
# grid = [list(input()) for _ in range(n)]
# visited1 = [[0]*m for _ in range(n)]
# visited2 = [[0]*m for _ in range(n)]
# dy = [-1,0,1,0]
# dx = [0,1,0,-1]
# coin1,coin2 = findCoins()

# visited1[coin1[0]][coin1[1]] = 1
# visited2[coin2[0]][coin2[1]] = 1
# ans = 0
# dfs(coin1[0],coin1[1],coin2[0],coin2[1],0)
