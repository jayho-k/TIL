'''
2

1
5 1       
9 3 2 3 2 
6 3 1 7 5
3 4 8 9 9
2 3 7 7 7
7 6 5 5 8

1
3 2       
1 2 1     
2 1 2
1 2 1

최대 K 깊이만큼 지형을 깎는 공사를 할 수 있다.
==> k가 1부터 k까지 깍을 수 있다는 뜻이구나


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


def dfs(y,x,cnt,k_cnt,cut_num):
    global mx

    if cut_num>k:
        if mx<cnt:
            mx = cnt
        return
    
    for d in range(4):
        ny = y+dy[d]
        nx = x+dx[d]
        if 0<=ny<n and 0<=nx<n and visited[ny][nx]==0:

            if grid[ny][nx]<grid[y][x]:
                visited[ny][nx]=1
                dfs(ny,nx,cnt+1,k_cnt,cut_num)
                visited[ny][nx]=0

            elif grid[ny][nx]-cut_num<grid[y][x] and k_cnt==0:
                visited[ny][nx]=1
                grid[ny][nx]-=cut_num
                dfs(ny,nx,cnt+1,k_cnt+1,cut_num)
                grid[ny][nx]+=cut_num
                visited[ny][nx]=0
            else:
                dfs(y,x,cnt,k_cnt,cut_num+1)


dy = [-1,0,1,0]
dx = [0,1,0,-1]

for tc in range(1,int(input())+1):
    n,k = map(int,input().split())
    grid = [list(map(int,input().split())) for _ in range(n)]
    st_points = find_top()
    mx = 0
    for i in range(len(st_points)):
        sty,stx = st_points[i]
        visited = [[0]*n for _ in range(n)]
        visited[sty][stx]=1
        dfs(sty,stx,1,0,1)
    print(f"#{tc} {mx}")




'''
1
5 1       
9 3 2 3 2 
6 3 1 7 5
3 4 8 9 9
2 3 7 7 7
7 6 5 5 8

'''


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

# def bfs(y,x,k,cnt):
    
#     q = deque([(y,x,cnt)])
#     visited[y][x][cnt]=1
#     mx = 0
#     while q:
#         y,x,cnt = q.popleft()
#         for d in range(4):
#             ny = y+dy[d]
#             nx = x+dx[d]
#             if 0<=ny<n and 0<=nx<n and (visited[ny][nx][cnt]==0 or visited[ny][nx][cnt]<visited[y][x][cnt]):
#                 if grid[ny][nx]<grid[y][x]:
#                     visited[ny][nx][cnt]=visited[y][x][cnt]+1
#                     mx = max(visited[ny][nx][cnt], mx)
#                     q.append((ny,nx,cnt))

#                 elif grid[ny][nx]-k<grid[y][x] and cnt==0:
#                     cnt+=1
#                     visited[ny][nx][cnt]=visited[y][x][cnt-1]+1
#                     mx = max(visited[ny][nx][cnt], mx)
#                     q.append((ny,nx,cnt))
#     return mx
#     # print(mx)
#     # pprint(visited)


# dy = [-1,0,1,0]
# dx = [0,1,0,-1]

# for tc in range(1,int(input())+1):
#     n,k = map(int,input().split())
#     grid = [list(map(int,input().split())) for _ in range(n)]
#     st_points = find_top()
#     ans = 0
#     for sty,stx in st_points:
#         visited = [[[0,0] for _ in range(n)] for _ in range(n)]
#         # pprint(visited[0][0])
#         mx = bfs(sty,stx,k,0)
#         ans = max(ans,mx)

#     print(f"#{tc} {ans}")
