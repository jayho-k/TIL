'''
2

1
5 1       
9 3 2 3 2 
6 3 1 7 5
3 4 8 9 9
2 3 7 7 7
7 6 5 5 8


3 2       
1 2 1     
2 1 2
1 2 1

'''
from pprint import pprint
from collections import deque
def find_top():
    mx = 0
    lst=[]
    for y in range(n):
        for x in range(n):
            if mx<grid[y][x]:
                lst = []
                mx = grid[y][x]
                lst.append((y,x))

            elif mx==grid[y][x]:
                lst.append((y,x))

    return lst

# def dfs2(y,x,cnt):

#     if 


def dfs(y,x,k,cnt):

    if k<0:
        print(cnt)
        pprint(visited)
        return
    
    for d in range(4):
        ny = y+dy[d]
        nx = x+dx[d]
        if 0<=ny<n and 0<=nx<n and visited[ny][nx]==0:
            if grid[ny][nx]<grid[y][x]:
                visited[ny][nx]=1
                dfs(ny,nx,k,cnt+1)
                visited[ny][nx]=0    

            elif grid[ny][nx]-k>=grid[y][x]:
                dfs(y,x,k,cnt)

            elif grid[ny][nx]-k<grid[y][x]:
                for i in range(1,k+1):
                    if grid[ny][nx]-i<grid[y][x]:
                        dk = i
                        break
                nk = k-dk
                visited[ny][nx]=1
                dfs(ny,nx,nk,cnt+1)
                visited[ny][nx]=0


dy = [-1,0,1,0]
dx = [0,1,0,-1]

for tc in range(1,int(input())+1):
    n,k = map(int,input().split())
    grid = [list(map(int,input().split())) for _ in range(n)]
    st_points = find_top()
    for i in range(2,len(st_points)):
        sty,stx = st_points[i]
        visited = [[0]*n for _ in range(n)]
        visited[sty][stx]=1
        dfs(sty,stx,k,1)


# from pprint import pprint
# from collections import deque
# def find_top():
#     mx = 0
#     lst=[]
#     for y in range(n):
#         for x in range(n):
#             if mx<grid[y][x]:
#                 lst = []
#                 mx = grid[y][x]
#                 lst.append((y,x))

#             elif mx==grid[y][x]:
#                 lst.append((y,x))

#     return lst

# def bfs(y,x,k):
    
#     q = deque([(y,x,k)])
#     visited[y][x]=1

#     while q:
#         y,x,k = q.popleft()
#         for d in range(4):
#             ny = y+dy[d]
#             nx = x+dx[d]
#             if 0<=ny<n and 0<=nx<n and visited[ny][nx]==0:
#                 if grid[ny][nx]<grid[y][x]:
#                     visited[ny][nx]=visited[y][x]+1
#                     q.append((ny,nx,k))

#                 elif grid[ny][nx]>=grid[y][x] and grid[ny][nx]-k<grid[y][x]:
#                     for i in range(1,k+1):
#                         if grid[ny][nx]-i<grid[y][x]:
#                             dk = i
#                             break

#                     nk = k-dk
#                     visited[ny][nx]=visited[y][x]+1
#                     q.append((ny,nx,nk))
    
#     pprint(visited)


# dy = [-1,0,1,0]
# dx = [0,1,0,-1]

# for tc in range(1,int(input())+1):
#     n,k = map(int,input().split())
#     grid = [list(map(int,input().split())) for _ in range(n)]
#     st_points = find_top()
#     for sty,stx in st_points:
#         visited = [[0]*n for _ in range(n)]
#         bfs(sty,stx,k)