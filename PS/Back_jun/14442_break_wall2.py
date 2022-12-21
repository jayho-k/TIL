'''
6 4 3
0100
1110
1000
0000
0111
0000

'''
from pprint import pprint
from collections import deque
import sys

def bfs(y,x,w,dim):
    
    q = deque([(y,x,w)])
    visited[y][x][w] = 1

    while q:
        y,x,w = q.popleft()
        if (y,x) == (n-1,m-1):
            pprint(visited)
            return visited[y][x][w]

        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]

            if 0<=ny<n and 0<=nx<m and visited[ny][nx][w]==0:
                
                # 벽x, 방문여부(그 층에 있어야함)
                if grid[ny][nx]==0:
                    q.append((ny,nx,w))
                    visited[ny][nx][w] = visited[y][x][w]+1
                
                # 벽o(벽을 더 부수는게 가능)
                # => 윗층으로 이동 => 이동거리+1
                # 내가 벽을 뚫고 갈곳을 가봤었는지 => 중복되는 부분을 다 막아줬다고 보면 된다.
                # ex) 아랫층에서 뚫으려고 할떄 이미 한번 뚫렸던 곳이나 또는 이미 다른 곳에서 뚫고나서
                # 그쪽으로 갔던 곳일 수 있다. 
                # 즉 그쪽 벽을 뚫는다고 하더라도 최단 거리가 될 수 없다는 뜻
                elif  grid[ny][nx]==1 and w < dim and visited[ny][nx][w+1]==0:
                    if w!=0 and visited[ny][nx][w-1]!=0:
                        continue
                    nw = w+1
                    visited[ny][nx][nw] = visited[y][x][w]+1
                    q.append((ny,nx,nw))

    return -1


input = sys.stdin.readline
n,m,dim = map(int,input().split())
grid = [list(map(int,list(input().rstrip()))) for _ in range(n)]
visited = [[[0]*(dim+1) for _ in range(m)] for _ in range(n)]
dy = [0,0,1,-1]
dx = [1,-1,0,0]
print(bfs(0,0,0,dim))





# from collections import deque
# import sys
# def bfs(y,x,w,dim):

#     q = deque()
#     q.append((0,0,0))

#     while q:
#         y,x,w = q.popleft()
#         if y == n-1 and x == m-1:
#             return visited[y][x][w]

#         check = visited[y][x][w] + 1
        
#         for d in range(4):
#             ny = y + dy[d]
#             nx = x + dx[d]

#             if 0<=ny<n and 0<=nx<m and visited[ny][nx][w] == 0:

#                 if grid[ny][nx] == 1 and w < dim:
#                     visited[ny][nx][w+1] = check
#                     q.append((ny,nx,w+1))

#                 elif grid[ny][nx] == 0:
#                     visited[ny][nx][w] = check
#                     q.append((ny,nx,w))

#     return -1

# input = sys.stdin.readline
# n,m,dim = map(int,input().split())
# grid = [list(map(int,list(input().rstrip()))) for _ in range(n)]
# visited = [[[0]*(dim+1) for _ in range(m)] for _ in range(n)]

# dy = (0,0,1,-1)
# dx = (1,-1,0,0)    

# # 방문표시
# visited[0][0] = [1]*(dim+1)
# print(bfs(0,0,0,dim))