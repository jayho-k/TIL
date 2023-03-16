'''
1. 대각선 방향으로 움직임
2. 사각형 모양을 그림 => d가 총 4번만 진행이 되어야한다.
3. 그 사이에 여러가지 꺽임이 있어야한다.
    ==> d가 돌아오는 길이 아닐때는 다 꺽여야 한다.

움직이고 있는 중간에 여러군데를 더 가주어야 한다면
if d 값안에서 뿌리를 더 뿌리도록 해주어야 한다.

if 0<=ny<n and 0<=nx<n and grid[ny][nx] not in visited:
    visited.add(grid[ny][nx])
    dfs(d,ny,nx,gy,gx)
    visited.remove(grid[ny][nx])

    # 이런식으로 중간에 계속 뿌리를 뻗어주면 된다.
    if d<3:
        visited.add(grid[ny][nx])
        dfs(d+1,ny,nx,gy,gx)
        visited.remove(grid[ny][nx])


2
4                
9 8 9 8
4 6 9 4
8 7 7 8
4 5 3 5
5                
8 2 9 6 6
1 9 3 3 4
8 2 3 3 6
4 3 4 4 9
7 4 6 3 5

'''
def dfs(d,y,x,gy,gx):
    global cnt
    if d==3 and (y,x)==(gy,gx):
        cnt = max(cnt,len(visited))
        return
    
    ny = y+dy[d]
    nx = x+dx[d]
    if 0<=ny<n and 0<=nx<n and grid[ny][nx] not in visited:
        visited.add(grid[ny][nx])
        dfs(d,ny,nx,gy,gx)
        visited.remove(grid[ny][nx])

        if d<3:
            visited.add(grid[ny][nx])
            dfs(d+1,ny,nx,gy,gx)
            visited.remove(grid[ny][nx])



for tc in range(1,int(input())+1):
    n = int(input())
    grid = [list(map(int,input().split())) for _ in range(n)]
    dy = [1,1,-1,-1]
    dx = [-1,1,1,-1]
    cnt = 0
    for y in range(n):
        for x in range(n):
            visited = set()
            dfs(0,y,x,y,x)
    if cnt:
        print(f"#{tc} {cnt}")
    else:
        print(f"#{tc} {-1}")









# from pprint import pprint
# def dfs(y,x,gy,gx,d):
#     global mx

#     if d==3 and gy==y and gx==x:
#         mx = max(mx,len(store))
#         return

#     ny = y+dy[d]
#     nx = x+dx[d]

#     # 직진하는 경우
#     if 0<=ny<n and 0<=nx<n and grid[ny][nx] not in store:
#         store.add(grid[ny][nx])
#         dfs(ny,nx,gy,gx,d)
#         store.remove(grid[ny][nx])

#         # 꺽는 경우
#         if d<3:
#             store.add(grid[ny][nx])
#             dfs(ny,nx,gy,gx,d+1)
#             store.remove(grid[ny][nx])


# for tc in range(1,int(input())+1):
#     n = int(input())
#     grid = [list(map(int,input().split())) for _ in range(n)]
#     dy = [1,1,-1,-1]
#     dx = [1,-1,-1,1]
#     mx = 0

#     for y in range(n):
#         for x in range(n):
#             store = set()
#             dfs(y,x,y,x,0)
    
#     if mx==0:
#         print(f"#{tc} {-1}")

#     else:
#         print(f"#{tc} {mx}")

