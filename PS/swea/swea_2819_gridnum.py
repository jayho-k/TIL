'''
1
1 1 1 1
1 1 1 2
1 1 2 1
1 1 1 1
 
7자리수
'''
def dfs(y,x,s,dp):

    if dp == 7:
        lst.add(s)
        return 

    dy = [0,0,1,-1]
    dx = [1,-1,0,0]

    for d in range(4):
        ny = y + dy[d]
        nx = x + dx[d]
        
        if 0<=ny<n and 0<=nx<n:
            dfs(ny,nx,s+str(grid[ny][nx]),dp+1)

T = int(input())
for tc in range(1,T+1):
    grid = [list(map(int, input().split())) for _ in range(4)]
    n = 4

    lst = set([])
    for y in range(n):
        for x in range(n):
            dfs(y,x,str(grid[y][x]),1)


    print(f'#{tc} {len(lst)}')




# def dfs(y,x,s,dp):

#     if dp == 7:
#         if s not in lst:
#             lst.append(s)
#         return 

#     dy = [0,0,1,-1]
#     dx = [1,-1,0,0]

#     for d in range(4):
#         ny = y + dy[d]
#         nx = x + dx[d]
        
#         if 0<=ny<n and 0<=nx<n:
#             dfs(ny,nx,s+[grid[ny][nx]],dp+1)


# T = int(input())
# for tc in range(1,T+1):
#     grid = [list(map(int, input().split())) for _ in range(4)]
#     n = 4

#     lst = []
#     for y in range(n):
#         for x in range(n):
#             dfs(y,x,[grid[y][x]],1)

#     print(f'#{tc} {len(lst)}')



# 같던 곳을 다시 안가는 경우
# def dfs(y,x,s):
#     global lst

#     if visited[y][x] == 7:

#         if s not in lst:
#             lst.append(s)
#         return 

#     dy = [0,0,1,-1]
#     dx = [1,-1,0,0]

#     for d in range(4):
#         ny = y + dy[d]
#         nx = x + dx[d]

#         if 0<=ny<n and 0<=nx<n and not visited[ny][nx]:
#             visited[ny][nx] = visited[y][x] + 1
#             dfs(ny,nx,s+[grid[ny][nx]])
#             visited[ny][nx] = 0
            


# grid = [list(map(int, input().split())) for _ in range(4)]
# n = 4

# lst = []
# for y in range(4):
#     for x in range(4):
#         visited = [[0]*4 for _ in range(4)]
#         visited[y][x] = 1
#         dfs(y,x,[grid[y][x]])

# print(len(lst))