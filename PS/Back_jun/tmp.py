# def bomb(grid, bombs):
#     bombs = deque(bombs)

#     dy = [0,0,1,-1]
#     dx = [1,-1,0,0]

#     while bombs:
#         by,bx = bombs.popleft()
#         grid[by][bx] = '.'

#         for d in range(4):
#             ny = by+dy[d]
#             nx = bx+dx[d]
            
#             if 0<=ny<n and 0<=nx<m:
#                 grid[ny][nx] = '.'
#     return grid

# def bomb_lst(grid):

#     bombs1 = []
#     for y in range(n):
#         for x in range(m):
#             if grid[y][x] == 'O':
#                 bombs1.append((y,x))

#     return bombs1
   
# def install(grid):
    
#     for y in range(n):
#         for x in range(m):
#             if grid[y][x] == '.':
#                 grid[y][x] = 'O'

#     return grid

    
# from collections import deque
# from pprint import pprint
# n,m,time = map(int,input().split())

# grid = [list(input()) for _ in range(n)]

# t = 1
# while t<=time:


#     bomb1 = bomb_lst(grid)
#     # pprint(grid)
#     if t >=time:
#         break


#     grid = install(grid)
#     # pprint(grid)
#     t+=1
#     if t >=time:
#         break


#     grid = bomb(grid,bomb1)
#     # pprint(grid)
#     t+=1
#     if t >=time:
#         break



# # pprint(grid)

# for g in grid:
#     print(''.join(g))


