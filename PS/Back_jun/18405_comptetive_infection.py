# '''
# 시간이 지날때 마다 차례대로 전염함?
# 3 3
# 1 0 2
# 0 0 0
# 3 0 0
# 2 3 2
# '''
# 맞는 코드

from collections import deque

def stp():
    st_lst = []
    for y in range(n+1):
        for x in range(n+1):
            if grid[y][x] != 0 and grid[y][x] != -1:
                st_lst.append((grid[y][x],y,x))
    return st_lst

def bfs(st_lst):
    cnt = 0
    q = deque(st_lst)

    # 상하좌우
    dy = [-1,1,0,0]
    dx = [0,0,-1,1]

    while q:
        nq = len(q)

        if cnt == s:
            return

        for i in range(nq):
            num, y, x = q.popleft()
            for d in range(4):
                ny = y + dy[d]
                nx = x + dx[d]

                if 0<=ny<n+1 and 0<=nx<n+1 and grid[ny][nx] == 0:
                    grid[ny][nx] = num
                    q.append((num,ny,nx))
        else:
            cnt += 1

n,k = map(int, input().split())
grid = [[-1]*(n+1)] + [[-1]+list(map(int, input().split())) for _ in range(n)] 
s,ty,tx = map(int, input().split())
st_lst = stp()
st_lst.sort()
bfs(st_lst)

print(grid[ty][tx])


# def stp():
#     st_lst = []
#     for y in range(n+1):
#         for x in range(n+1):
#             if grid[y][x] != 0 and grid[y][x] != -1:
#                 st_lst.append((grid[y][x],y,x))
#     return st_lst

# def bfs(st_lst):
#     q = deque(st_lst)
#     snum, sy, sx = st_lst[-1]

#     # 상하좌우
#     dy = [-1,1,0,0]
#     dx = [0,0,-1,1]
    
#     while q:

#         num, y, x = q.popleft()

#         for d in range(4):
#             ny = y + dy[d]
#             nx = x + dx[d]

#             if 0<=ny<n+1 and 0<=nx<n+1 and grid[ny][nx] == 0:
#                 grid[ny][nx] = num
#                 q.append((num,ny,nx))

#         if snum == num and sy == y and sx == x:
#             return list(q)


# n,k = map(int, input().split())
# grid = [[-1]*(n+1)] + [[-1]+list(map(int, input().split())) for _ in range(n)] 
# s,ty,tx = map(int, input().split())
# st_lst = stp()
# st_lst.sort()

# for _ in range(s):
#     q = bfs(st_lst)
#     st_lst = q[:]

# print(grid[ty][tx])